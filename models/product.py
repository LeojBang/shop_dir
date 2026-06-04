from decimal import Decimal

from sqlalchemy import ForeignKey
from sqlalchemy import Numeric

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from models.base import Base
from sqlalchemy import String


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2)
    )
    stock: Mapped[int] = mapped_column(
        default=0
    )
    image_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id")
    )
    category = relationship(
        "Category"
    )
