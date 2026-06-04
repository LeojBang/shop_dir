from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import String

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column

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

    total_price: Mapped[float]

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    items = relationship(
        "OrderItem",
        back_populates="order",
        lazy="selectin",
    )