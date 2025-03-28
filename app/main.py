import uvicorn
from fastapi import FastAPI, Depends, File, UploadFile, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session, engine
from app.models import Base
from app.schemas import UserCreate, UserUpdate, UserOut, AudioFilesListOut, AudioFileOut, Token
from app.services import (
    create_user, get_user_by_email, get_user_by_id, update_user, delete_user,
    get_audio_files_for_user, upload_audio_file
)
from app.utils import verify_password
from app.security import create_access_token, decode_token
from app.oauth import router as yandex_oauth_router
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


app = FastAPI(title="Audio Service with Yandex OAuth")
bearer_scheme = HTTPBearer()

@app.get("/test")
def test_route(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    return {"token_received": credentials.credentials}

# Роутер с Яндекс OAuth
app.include_router(yandex_oauth_router, prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ============= Авторизация/Аутентификация ==============

@app.post("/login", response_model=Token, tags=["Auth"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):

    user = await get_user_by_email(session, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    # Генерация токена:
    access_token_expires = timedelta(hours=1)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



@app.post("/refresh_token", response_model=Token, tags=["Auth"])
async def refresh_token(current_token: str = Depends(oauth2_scheme)):
    payload = decode_token(current_token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    # Генерируем новый токен
    new_access_token_expires = timedelta(hours=1)
    new_access_token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=new_access_token_expires
    )
    return {"access_token": new_access_token, "token_type": "bearer"}


# ============= Зависимость для получения текущего пользователя ==============

async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)):
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

async def get_current_superuser(current_user=Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a superuser")
    return current_user

# ============= Эндпоинты по работе с пользователями ==============

@app.post("/users", response_model=UserOut, tags=["Users"])
async def create_user_endpoint(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    existing_user = await get_user_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    new_user = await create_user(
        db=session,
        email=user_data.email,
        username=user_data.username or "",
        password=user_data.password or "",
        is_superuser=False
    )
    return new_user

@app.get("/users/me", response_model=UserOut, tags=["Users"])
async def get_me(current_user=Depends(get_current_user)):
    return current_user

@app.patch("/users/me", response_model=UserOut, tags=["Users"])
async def update_me(
    user_data: UserUpdate,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    updated_user = await update_user(session, current_user.id, user_data.username, user_data.is_superuser)
    return updated_user

# Эндпоинты для суперпользователя
@app.delete("/users/{user_id}", tags=["Users"])
async def delete_user_endpoint(user_id: str, superuser=Depends(get_current_superuser), session: AsyncSession = Depends(get_session)):
    await delete_user(session, user_id)
    return {"detail": f"User {user_id} deleted"}

# ============= Эндпоинты по работе с аудиофайлами ==============

@app.post("/upload", response_model=AudioFileOut, tags=["Audio"])
async def upload_audio(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),  # имя, которое пользователь задаёт
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    audio = await upload_audio_file(session, file, current_user.id, filename=name or file.filename)
    return audio

@app.get("/my_files", response_model=AudioFilesListOut, tags=["Audio"])
async def get_my_files(current_user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    files = await get_audio_files_for_user(session, current_user.id)
    return {"audio_files": files}


# Запуск при локальном старте (не в Docker)
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
