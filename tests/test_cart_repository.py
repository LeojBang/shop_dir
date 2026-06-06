import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.cart import CartRepository
from conftest import make_user, make_category, make_product

repo = CartRepository()


@pytest.mark.asyncio
async def test_add_new_product_to_cart(session: AsyncSession):
    """Добавление нового товара создаёт запись с quantity=1."""
    user = await make_user(session, telegram_id=1)
    category = await make_category(session)
    product = await make_product(session, category_id=category.id)

    await repo.add_product(
        session=session,
        user_id=user.id,
        product_id=product.id,
    )

    cart = await repo.get_user_cart(session=session, user_id=user.id)

    assert len(cart) == 1
    assert cart[0].product_id == product.id
    assert cart[0].quantity == 1


@pytest.mark.asyncio
async def test_add_same_product_increases_quantity(session: AsyncSession):
    """Повторное добавление того же товара увеличивает quantity."""
    user = await make_user(session, telegram_id=2)
    category = await make_category(session)
    product = await make_product(session, category_id=category.id)

    await repo.add_product(session=session, user_id=user.id, product_id=product.id)
    await repo.add_product(session=session, user_id=user.id, product_id=product.id)

    cart = await repo.get_user_cart(session=session, user_id=user.id)

    assert len(cart) == 1
    assert cart[0].quantity == 2


@pytest.mark.asyncio
async def test_increase_quantity(session: AsyncSession):
    """increase_quantity увеличивает количество на 1."""
    user = await make_user(session, telegram_id=3)
    category = await make_category(session)
    product = await make_product(session, category_id=category.id)

    await repo.add_product(session=session, user_id=user.id, product_id=product.id)
    cart = await repo.get_user_cart(session=session, user_id=user.id)

    await repo.increase_quantity(session=session, cart_item_id=cart[0].id)

    item = await repo.get_item(session=session, cart_item_id=cart[0].id)
    assert item.quantity == 2


@pytest.mark.asyncio
async def test_decrease_quantity_above_one(session: AsyncSession):
    """decrease_quantity уменьшает количество если > 1."""
    user = await make_user(session, telegram_id=4)
    category = await make_category(session)
    product = await make_product(session, category_id=category.id)

    await repo.add_product(session=session, user_id=user.id, product_id=product.id)
    await repo.add_product(session=session, user_id=user.id, product_id=product.id)

    cart = await repo.get_user_cart(session=session, user_id=user.id)
    await repo.decrease_quantity(session=session, cart_item_id=cart[0].id)

    item = await repo.get_item(session=session, cart_item_id=cart[0].id)
    assert item.quantity == 1


@pytest.mark.asyncio
async def test_decrease_quantity_removes_item_when_one(session: AsyncSession):
    """decrease_quantity удаляет запись если quantity = 1."""
    user = await make_user(session, telegram_id=5)
    category = await make_category(session)
    product = await make_product(session, category_id=category.id)

    await repo.add_product(session=session, user_id=user.id, product_id=product.id)
    cart = await repo.get_user_cart(session=session, user_id=user.id)

    await repo.decrease_quantity(session=session, cart_item_id=cart[0].id)

    item = await repo.get_item(session=session, cart_item_id=cart[0].id)
    assert item is None


@pytest.mark.asyncio
async def test_remove_item(session: AsyncSession):
    """remove_item удаляет конкретный товар из корзины."""
    user = await make_user(session, telegram_id=6)
    category = await make_category(session)
    product = await make_product(session, category_id=category.id)

    await repo.add_product(session=session, user_id=user.id, product_id=product.id)
    cart = await repo.get_user_cart(session=session, user_id=user.id)

    await repo.remove_item(session=session, cart_item_id=cart[0].id)

    remaining = await repo.get_user_cart(session=session, user_id=user.id)
    assert remaining == []


@pytest.mark.asyncio
async def test_clear_cart(session: AsyncSession):
    """clear_cart удаляет все товары пользователя."""
    user = await make_user(session, telegram_id=7)
    category = await make_category(session)
    product1 = await make_product(session, category_id=category.id, name="Товар 1")
    product2 = await make_product(session, category_id=category.id, name="Товар 2")

    await repo.add_product(session=session, user_id=user.id, product_id=product1.id)
    await repo.add_product(session=session, user_id=user.id, product_id=product2.id)

    await repo.clear_cart(session=session, user_id=user.id)

    cart = await repo.get_user_cart(session=session, user_id=user.id)
    assert cart == []


@pytest.mark.asyncio
async def test_clear_cart_does_not_affect_other_users(session: AsyncSession):
    """clear_cart одного пользователя не трогает корзину другого."""
    user1 = await make_user(session, telegram_id=8)
    user2 = await make_user(session, telegram_id=9)
    category = await make_category(session)
    product = await make_product(session, category_id=category.id)

    await repo.add_product(session=session, user_id=user1.id, product_id=product.id)
    await repo.add_product(session=session, user_id=user2.id, product_id=product.id)

    await repo.clear_cart(session=session, user_id=user1.id)

    cart2 = await repo.get_user_cart(session=session, user_id=user2.id)
    assert len(cart2) == 1
