import pytest
import pytest_asyncio
from decimal import Decimal

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from models.base import Base
from models.user import User
from models.category import Category
from models.product import Product
from models.order import Order
from models.order_item import OrderItem
from models.cart_item import CartItem

# Используем SQLite в памяти — не нужен PostgreSQL для тестов
DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def session():
    """Создаёт чистую БД и сессию для каждого теста."""
    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as s:
        yield s

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


# ── Вспомогательные фабрики ──────────────────────────────────────────────────

async def make_user(
    session: AsyncSession,
    telegram_id: int = 123456789,
    username: str | None = "testuser",
    first_name: str | None = None,
    phone: str | None = None,
    address: str | None = None,
) -> User:
    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        phone=phone,
        address=address,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def make_category(
    session: AsyncSession,
    name: str = "Тестовая категория",
) -> Category:
    category = Category(name=name)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def make_product(
    session: AsyncSession,
    category_id: int,
    name: str = "Тестовый товар",
    price: Decimal = Decimal("1000.00"),
    stock: int = 10,
) -> Product:
    product = Product(
        name=name,
        price=price,
        stock=stock,
        category_id=category_id,
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product