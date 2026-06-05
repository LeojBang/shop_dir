from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int]

    status: Mapped[str] = mapped_column(
        String(20),
        default="new",
    )

    total_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2)
    )

    tracking_number: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )

    items = relationship(
        "OrderItem",
        back_populates="order",
        lazy="selectin",
    )