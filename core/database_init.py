from core.database import engine
from models.base import Base

# импортируем модели
from models.user import User
from models.product import Product
from models.order import Order
from models.order_item import OrderItem
from models.cart_item import CartItem
from models.category import Category
from models.payment_settings import PaymentSettings


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)