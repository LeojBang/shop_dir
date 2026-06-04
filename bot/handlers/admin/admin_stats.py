from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram import F
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.order import OrderRepository

router = Router()
order_repository = OrderRepository()


@router.callback_query(
    F.data == "admin_stats"
)
async def admin_stats(
        callback: CallbackQuery,
        session: AsyncSession,
):
    orders = await order_repository.get_all_orders(
        session=session
    )

    total_orders = len(orders)

    total_revenue = sum(
        float(order.total_price)
        for order in orders
    )

    await callback.message.answer(
        f"📊 Статистика\n\n"
        f"Заказов всего: {total_orders}\n"
        f"Выручка: {total_revenue:.2f} ₽"
    )

    await callback.answer()

