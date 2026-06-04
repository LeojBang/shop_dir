from datetime import datetime

from sqlalchemy import BigInteger, Column, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
    )
    first_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    username: Mapped[str | None]

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )