import uuid
import os
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models import User, AudioFile
from app.utils import hash_password

UPLOAD_DIR = "uploads"

async def create_user(db: AsyncSession, email: str, username: str, password: str, is_superuser=False):
    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
        is_superuser=is_superuser
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def update_user(db: AsyncSession, user_id: uuid.UUID, username: str = None, is_superuser: bool = None):
    stmt = update(User).where(User.id == user_id)
    values = {}
    if username is not None:
        values["username"] = username
    if is_superuser is not None:
        values["is_superuser"] = is_superuser
    if values:
        stmt = stmt.values(**values)
        stmt = stmt.execution_options(synchronize_session="fetch")
        await db.execute(stmt)
        await db.commit()

    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()

async def delete_user(db: AsyncSession, user_id: uuid.UUID):
    stmt = delete(User).where(User.id == user_id)
    await db.execute(stmt)
    await db.commit()

async def get_audio_files_for_user(db: AsyncSession, user_id: uuid.UUID):
    result = await db.execute(select(AudioFile).where(AudioFile.owner_id == user_id))
    return result.scalars().all()

async def upload_audio_file(db: AsyncSession, file: UploadFile, owner_id: uuid.UUID, filename: str):
    # Сохраняем файл локально
    file_ext = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as out_file:
        content = await file.read()
        out_file.write(content)

    audio = AudioFile(
        filename=filename or file.filename,
        filepath=file_path,
        owner_id=owner_id
    )
    db.add(audio)
    await db.commit()
    await db.refresh(audio)

    return audio
