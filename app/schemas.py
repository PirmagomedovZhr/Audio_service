from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID

# Схемы пользователя
class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str]

class UserCreate(UserBase):
    password: Optional[str]

class UserUpdate(BaseModel):
    username: Optional[str]
    is_superuser: Optional[bool] = None

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    username: Optional[str]
    is_superuser: bool

    class Config:
        orm_mode = True

# Аудиофайл
class AudioFileOut(BaseModel):
    id: UUID
    filename: str
    filepath: str

    class Config:
        orm_mode = True

# Ответ на получение списка файлов
class AudioFilesListOut(BaseModel):
    audio_files: List[AudioFileOut]

# Токены
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
