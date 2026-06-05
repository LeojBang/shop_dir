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
    orders = await order_repository.get_stats_orders(
        session=session
    )


    completed_orders = [
        o for o in orders
        if o.status == "completed"
    ]

    total_revenue = sum(
        float(o.total_price)
        for o in completed_orders
    )

    await callback.message.answer(
        f"📊 Статистика\n\n"
        f"Заказов всего: {len(completed_orders)}\n"
        f"Выручка: {total_revenue:.2f} ₽"
    )

    await callback.answer()

