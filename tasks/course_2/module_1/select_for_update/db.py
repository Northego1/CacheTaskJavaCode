import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
from typing import AsyncGenerator

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import UUID, VARCHAR, DateTime

async_engine = create_async_engine(
    url="postgresql+asyncpg://postgres:0420@localhost:5432/test",
)


@asynccontextmanager
async def connection_maker() -> AsyncGenerator[AsyncConnection, None]: 
    async with async_engine.begin() as conn:
        yield conn


class Status(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"


class Base(DeclarativeBase): ...

class TaskModel(Base):
    __tablename__ = "tasks"


    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    task_name: Mapped[str] = mapped_column(
        VARCHAR(60),
        nullable=False,
    )
    status: Mapped[Status] = mapped_column(
        ENUM(Status, name="status"),
        nullable=False,
    )
    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )
