import httpx
from fastapi import APIRouter, Depends, Request, HTTPException
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import User
from app.security import create_access_token
from app.utils import hash_password

router = APIRouter()

@router.get("/yandex/login")
async def yandex_login():
    """
    Отправляем пользователя на страницу Яндекса для авторизации.
    """
    # Документация: https://yandex.ru/dev/id/doc/dg/oauth/reference/authorize-docpage/
    params = {
        "response_type": "code",
        "client_id": settings.YANDEX_CLIENT_ID,
        "redirect_uri": settings.YANDEX_REDIRECT_URI
    }
    url = "https://oauth.yandex.ru/authorize"
    # Собираем URL для редиректа
    # Можно вернуть просто JSON с этим url, или сделать редирект
    # Для простоты вернём ссылку
    return {"auth_url": f"{url}?response_type={params['response_type']}&client_id={params['client_id']}&redirect_uri={params['redirect_uri']}"}

@router.get("/yandex/callback")
async def yandex_callback(code: str, session: AsyncSession = Depends(get_session)):
    """
    Callback-эндпоинт, который Яндекс вызывает с параметром code.
    """
    # Обмениваем code на токен
    token_url = "https://oauth.yandex.ru/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": settings.YANDEX_CLIENT_ID,
        "client_secret": settings.YANDEX_CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, data=data, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get token from Yandex")

        token_data = resp.json()
        access_token = token_data.get("access_token")

        # Теперь получим информацию о пользователе
        userinfo_url = "https://login.yandex.ru/info"
        headers = {"Authorization": f"OAuth {access_token}"}
        resp_userinfo = await client.post(userinfo_url, headers=headers)
        if resp_userinfo.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info from Yandex")

        userinfo = resp_userinfo.json()
        yandex_id = userinfo.get("id")
        default_email = userinfo.get("default_email")
        real_name = userinfo.get("real_name")

    # Проверяем, есть ли пользователь в БД
    user = await session.execute(
        f"SELECT * FROM users WHERE yandex_id = '{yandex_id}' OR email = '{default_email}'"
    )
    user_obj = user.scalars().first()

    # Если нет - создаём
    if not user_obj:
        user_obj = User(
            email=default_email,
            username=real_name,
            yandex_id=yandex_id,
            hashed_password=hash_password("random_generated_password"),  # Заглушка
            is_superuser=False
        )
        session.add(user_obj)
        await session.commit()
        await session.refresh(user_obj)

    # Генерируем наш внутренний токен
    internal_token = create_access_token({"sub": str(user_obj.id)})

    return {"access_token": internal_token, "token_type": "bearer"}
