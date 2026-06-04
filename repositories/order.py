from models.order import Order
from models.order_item import OrderItem
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload


class OrderRepository:

    async def create_order(
            self,
            session,
            user_id: int,
            items,
            total_price: float,
    ):
        order = Order(
            user_id=user_id,
            total_price=total_price,
            status="waiting_payment",
        )

        session.add(order)

        await session.flush()

        for item in items:

            if item.product.stock < item.quantity:
                raise ValueError(
                    f"Недостаточно товара {item.product.name}"
                )

            # уменьшаем остаток сразу
            item.product.stock -= item.quantity

            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price,
            )

            session.add(order_item)

        await session.commit()

        return order

    async def get_user_orders(
            self,
            session,
            user_id: int,
    ):
        result = await session.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .options(
                selectinload(Order.items)
                .selectinload(OrderItem.product)
            )
            .order_by(Order.created_at.desc())
        )

        return result.scalars().all()

    async def get_all_orders(
            self,
            session,
    ):
        result = await session.execute(
            select(Order)
            .options(
                selectinload(Order.items)
                .selectinload(OrderItem.product)
            )
            .order_by(Order.created_at.desc())
        )

        return result.scalars().all()

    async def get_new_orders(
            self,
            session,
    ):
        result = await session.execute(
            select(Order)
            .where(
                Order.status.in_([
                    "waiting_payment",
                    "processing",
                    "shipped",
                ])
            )
            .options(
                selectinload(Order.items)
                .selectinload(OrderItem.product)
            )
            .order_by(Order.created_at.desc())
        )

        return result.scalars().all()

    async def get_order(
            self,
            session,
            order_id: int,
    ):
        result = await session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.items)
                .selectinload(OrderItem.product)
            )
        )

        return result.scalar_one_or_none()

    async def update_status(
            self,
            session,
            order_id: int,
            status: str,
    ):
        await session.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(status=status)
        )

        await session.commit()

    async def get_orders_by_status(
            self,
            session,
            status: str,
    ):
        result = await session.execute(
            select(Order)
            .where(Order.status == status)
            .options(
                selectinload(Order.items)
                .selectinload(OrderItem.product)
            )
            .order_by(Order.created_at.desc())
        )

        return result.scalars().all()

    async def update_tracking_number(
            self,
            session,
            order_id: int,
            tracking_number: str,
    ):
        await session.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(
                tracking_number=tracking_number
            )
        )

        await session.commit()
