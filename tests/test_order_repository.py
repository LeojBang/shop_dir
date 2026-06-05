import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.order import OrderRepository
from repositories.cart import CartRepository
from conftest import make_user, make_category, make_product

order_repo = OrderRepository()
cart_repo = CartRepository()


async def _prepare_cart(session, telegram_id=100, stock=10):
    """Вспомогательная функция: создаёт пользователя, товар и кладёт в корзину."""
    user = await make_user(session, telegram_id=telegram_id)
    category = await make_category(session)
    product = await make_product(session, category_id=category.id, stock=stock)

    await cart_repo.add_product(
        session=session,
        user_id=user.id,
        product_id=product.id,
    )

    items = await cart_repo.get_user_cart(session=session, user_id=user.id)
    return user, product, items


@pytest.mark.asyncio
async def test_create_order_success(session: AsyncSession):
    """Успешное создание заказа — статус и сумма правильные."""
    user, product, items = await _prepare_cart(session, telegram_id=101)

    order = await order_repo.create_order(
        session=session,
        user_id=user.id,
        items=items,
        total_price=Decimal("1000.00"),
    )

    assert order.id is not None
    assert order.user_id == user.id
    assert order.status == "waiting_payment"
    assert order.total_price == Decimal("1000.00")


@pytest.mark.asyncio
async def test_create_order_decreases_stock(session: AsyncSession):
    """При создании заказа остаток товара уменьшается."""
    user, product, items = await _prepare_cart(session, telegram_id=102, stock=5)

    await order_repo.create_order(
        session=session,
        user_id=user.id,
        items=items,
        total_price=Decimal("1000.00"),
    )

    await session.refresh(product)
    assert product.stock == 4  # было 5, купили 1


@pytest.mark.asyncio
async def test_create_order_insufficient_stock(session: AsyncSession):
    """Создание заказа падает с ValueError если товара не хватает."""
    user, product, items = await _prepare_cart(session, telegram_id=103, stock=0)

    # Принудительно ставим stock=0 чтобы сымитировать гонку
    product.stock = 0
    await session.commit()

    with pytest.raises(ValueError, match="Недостаточно товара"):
        await order_repo.create_order(
            session=session,
            user_id=user.id,
            items=items,
            total_price=Decimal("1000.00"),
        )


@pytest.mark.asyncio
async def test_get_user_orders(session: AsyncSession):
    """Заказы пользователя возвращаются в правильном количестве."""
    user, product, items = await _prepare_cart(session, telegram_id=104)

    await order_repo.create_order(
        session=session,
        user_id=user.id,
        items=items,
        total_price=Decimal("1000.00"),
    )

    orders = await order_repo.get_user_orders(
        session=session,
        user_id=user.id,
    )

    assert len(orders) == 1
    assert orders[0].user_id == user.id


@pytest.mark.asyncio
async def test_get_user_orders_empty(session: AsyncSession):
    """Пользователь без заказов возвращает пустой список."""
    user = await make_user(session, telegram_id=105)

    orders = await order_repo.get_user_orders(
        session=session,
        user_id=user.id,
    )

    assert orders == [] or list(orders) == []


@pytest.mark.asyncio
async def test_update_status(session: AsyncSession):
    """Статус заказа обновляется корректно."""
    user, product, items = await _prepare_cart(session, telegram_id=106)

    order = await order_repo.create_order(
        session=session,
        user_id=user.id,
        items=items,
        total_price=Decimal("1000.00"),
    )

    await order_repo.update_status(
        session=session,
        order_id=order.id,
        status="paid",
    )

    updated = await order_repo.get_order(session=session, order_id=order.id)
    assert updated.status == "paid"


@pytest.mark.asyncio
async def test_update_tracking_number(session: AsyncSession):
    """Трек-номер сохраняется и читается правильно."""
    user, product, items = await _prepare_cart(session, telegram_id=107)

    order = await order_repo.create_order(
        session=session,
        user_id=user.id,
        items=items,
        total_price=Decimal("1000.00"),
    )

    await order_repo.update_tracking_number(
        session=session,
        order_id=order.id,
        tracking_number="RA123456789RU",
    )

    updated = await order_repo.get_order(session=session, order_id=order.id)
    assert updated.tracking_number == "RA123456789RU"


@pytest.mark.asyncio
async def test_get_orders_by_status(session: AsyncSession):
    """Фильтрация заказов по статусу работает правильно."""
    user, product, items = await _prepare_cart(session, telegram_id=108)

    order = await order_repo.create_order(
        session=session,
        user_id=user.id,
        items=items,
        total_price=Decimal("1000.00"),
    )

    await order_repo.update_status(
        session=session,
        order_id=order.id,
        status="paid",
    )

    paid_orders = await order_repo.get_orders_by_status(
        session=session,
        status="paid",
    )
    waiting_orders = await order_repo.get_orders_by_status(
        session=session,
        status="waiting_payment",
    )

    assert len(paid_orders) == 1
    assert len(waiting_orders) == 0


@pytest.mark.asyncio
async def test_get_order_includes_items(session: AsyncSession):
    """get_order возвращает заказ вместе с товарами внутри."""
    user, product, items = await _prepare_cart(session, telegram_id=109)

    order = await order_repo.create_order(
        session=session,
        user_id=user.id,
        items=items,
        total_price=Decimal("1000.00"),
    )

    fetched = await order_repo.get_order(session=session, order_id=order.id)

    assert len(fetched.items) == 1
    assert fetched.items[0].product_id == product.id