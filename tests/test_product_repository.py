import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.product import ProductRepository
from conftest import make_category, make_product

repo = ProductRepository()


@pytest.mark.asyncio
async def test_create_product(session: AsyncSession):
    """Товар создаётся с правильными полями."""
    category = await make_category(session)

    product = await repo.create(
        session=session,
        name="Пептид X",
        description="Описание",
        price=Decimal("2500.00"),
        stock=20,
        category_id=category.id,
    )

    assert product.id is not None
    assert product.name == "Пептид X"
    assert product.price == Decimal("2500.00")
    assert product.stock == 20


@pytest.mark.asyncio
async def test_get_by_category_only_in_stock(session: AsyncSession):
    """get_by_category возвращает только товары с stock > 0."""
    category = await make_category(session)

    await make_product(session, category_id=category.id, name="Есть в наличии", stock=5)
    await make_product(session, category_id=category.id, name="Нет в наличии", stock=0)

    products = await repo.get_by_category(
        session=session,
        category_id=category.id,
    )

    assert len(products) == 1
    assert products[0].name == "Есть в наличии"


@pytest.mark.asyncio
async def test_get_by_id(session: AsyncSession):
    """Товар находится по ID."""
    category = await make_category(session)
    product = await make_product(session, category_id=category.id)

    found = await repo.get_by_id(session=session, product_id=product.id)

    assert found is not None
    assert found.id == product.id


@pytest.mark.asyncio
async def test_get_by_id_not_found(session: AsyncSession):
    """Несуществующий ID возвращает None."""
    found = await repo.get_by_id(session=session, product_id=99999)
    assert found is None


@pytest.mark.asyncio
async def test_update_fields(session: AsyncSession):
    """Обновление полей товара сохраняется."""
    category = await make_category(session)
    product = await make_product(
        session, category_id=category.id, price=Decimal("1000.00")
    )

    updated = await repo.update_fields(
        session=session,
        product_id=product.id,
        price=Decimal("1500.00"),
        stock=50,
    )

    assert updated.price == Decimal("1500.00")
    assert updated.stock == 50


@pytest.mark.asyncio
async def test_delete_product(session: AsyncSession):
    """Удалённый товар больше не находится."""
    category = await make_category(session)
    product = await make_product(session, category_id=category.id)

    result = await repo.delete(session=session, product_id=product.id)
    assert result is True

    found = await repo.get_by_id(session=session, product_id=product.id)
    assert found is None


@pytest.mark.asyncio
async def test_delete_nonexistent_product(session: AsyncSession):
    """Удаление несуществующего товара возвращает False."""
    result = await repo.delete(session=session, product_id=99999)
    assert result is False


@pytest.mark.asyncio
async def test_get_page(session: AsyncSession):
    """Пагинация возвращает нужное количество товаров."""
    category = await make_category(session)

    for i in range(7):
        await make_product(session, category_id=category.id, name=f"Товар {i}")

    page1 = await repo.get_page(session=session, offset=0, limit=5)
    page2 = await repo.get_page(session=session, offset=5, limit=5)

    assert len(page1) == 5
    assert len(page2) == 2


@pytest.mark.asyncio
async def test_count(session: AsyncSession):
    """count() возвращает точное количество товаров."""
    category = await make_category(session)
    await make_product(session, category_id=category.id, name="Товар 1")
    await make_product(session, category_id=category.id, name="Товар 2")

    total = await repo.count(session=session)
    assert total == 2
