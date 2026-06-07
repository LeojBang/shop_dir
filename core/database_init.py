from core.database import engine
from models.base import Base
from models.cart_item import CartItem  # noqa: F401
from models.category import Category  # noqa: F401
from models.order import Order  # noqa: F401
from models.order_item import OrderItem  # noqa: F401
from models.payment_settings import PaymentSettings  # noqa: F401
from models.product import Product  # noqa: F401

# Импорты нужны для Alembic и create_tables — не удалять
from models.user import User  # noqa: F401


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
