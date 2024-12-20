# SQL Alchemy models declaration.
# https://docs.sqlalchemy.org/en/20/orm/quickstart.html#declare-models
# mapped_column syntax from SQLAlchemy 2.0.

# https://alembic.sqlalchemy.org/en/latest/tutorial.html
# Note, it is used by alembic migrations logic, see `alembic/env.py`

# Alembic shortcuts:
# # create migration
# alembic revision --autogenerate -m "migration_name"

# # apply all migrations
# alembic upgrade head


import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Uuid, func
from sqlalchemy import Enum, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class EventType(PyEnum):
    MODIFY = "modify"
    READ = "read"
    CREATE = "create"
    DELETE = "delete"


class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(Base):
    __tablename__ = "user_account"

    user_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), primary_key=True, default=lambda _: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(
        String(256), nullable=False, unique=True, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    refresh_token: Mapped[str] = mapped_column(
        String(512), nullable=False, unique=True, index=True
    )
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    exp: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("user_account.user_id", ondelete="CASCADE"),
    )
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")


class Link(Base):
    __tablename__ = "link"
    url: Mapped[str] = mapped_column(String(256), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=True)
    description: Mapped[str] = mapped_column(String(1024), nullable=True)


class DatasetGeneralInfo(Base):
    __tablename__ = "dataset_general_info"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(String(1024), nullable=True)

    dataset_id: Mapped[int] = mapped_column(ForeignKey("dataset.id"), nullable=False)

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="dataset_general_info", uselist=False)

class Dataset(Base):
    __tablename__ = "dataset"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    file_path: Mapped[str] = mapped_column(String(256), nullable=False)
    access_rights: Mapped[str] = mapped_column(String(3), nullable=False)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    host: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at_device: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at_server: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    dataset_general_info: Mapped["DatasetGeneralInfo"] = relationship(
        "DatasetGeneralInfo", back_populates="dataset", uselist=False
    )

class DatasetUsageHistory(Base):
    __tablename__ = "dataset_usage_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    host_name: Mapped[str] = mapped_column(String(256), nullable=False)
    dataset_name: Mapped[str] = mapped_column(String(256), nullable=False)

    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType), nullable=False
    )
    event_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), nullable=False)
