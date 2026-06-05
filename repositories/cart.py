from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from models.cart_item import CartItem




class CartRepository:

    async def add_product(
            self,
            session,
            user_id: int,
            product_id: int,
    ):
        stmt = select(CartItem).where(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id,
        )

        result = await session.execute(stmt)
        cart_item = result.scalar_one_or_none()

        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = CartItem(
                user_id=user_id,
                product_id=product_id,
                quantity=1,
            )
            session.add(cart_item)

        await session.commit()

    async def increase_quantity(
            self,
            session,
            cart_item_id: int,
    ):
        item = await session.get(CartItem, cart_item_id)

        if item:
            item.quantity += 1
            await session.commit()

    async def decrease_quantity(
            self,
            session,
            cart_item_id: int,
    ):
        item = await session.get(CartItem, cart_item_id)

        if not item:
            return

        if item.quantity > 1:
            item.quantity -= 1
            await session.commit()
        else:
            await session.delete(item)
            await session.commit()

    async def remove_item(
            self,
            session,
            cart_item_id: int,
    ):
        item = await session.get(CartItem, cart_item_id)

        if item:
            await session.delete(item)
            await session.commit()

    async def get_user_cart(
            self,
            session,
            user_id: int,
    ):
        result = await session.execute(
            select(CartItem)
            .options(selectinload(CartItem.product))
            .where(CartItem.user_id == user_id)
        )
        return list(result.scalars().all())

    async def clear_cart(
            self,
            session,
            user_id: int,
    ):
        await session.execute(
            delete(CartItem).where(
                CartItem.user_id == user_id
            )
        )
        await session.commit()

    async def get_item(
            self,
            session,
            cart_item_id: int,
    ):
        result = await session.execute(
            select(CartItem)
            .options(selectinload(CartItem.product))
            .where(CartItem.id == cart_item_id)
        )
        return result.scalar_one_or_none()