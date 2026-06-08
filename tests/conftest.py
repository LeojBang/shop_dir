from decimal import Decimal

import pytest  # noqa: F401
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models.base import Base
from models.cart_item import CartItem  # noqa: F401
from models.category import Category
from models.order import Order  # noqa: F401
from models.order_item import OrderItem  # noqa: F401
from models.payment_settings import PaymentSettings  # noqa: F401
from models.product import Product
from models.user import User

# Используем SQLite в памяти — не нужен PostgreSQL для тестов
DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def session():
    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with factory() as s:
        yield s

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def session_factory():
    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    yield factory

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
    price: Decimal | None = None,
    stock: int = 10,
) -> Product:
    if price is None:
        price = Decimal("1000.00")
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
