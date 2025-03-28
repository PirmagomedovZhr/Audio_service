from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    username = Column(String)
    yandex_id = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    is_superuser = Column(Boolean, default=False)

    # Пример отношения: User может иметь много AudioFile
    audio_files = relationship("AudioFile", back_populates="owner")


class AudioFile(Base):
    __tablename__ = "audio_files"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String)
    filepath = Column(String)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    owner = relationship("User", back_populates="audio_files")
