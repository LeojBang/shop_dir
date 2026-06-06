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

    all_orders = await order_repository.get_all_orders(session=session)
    completed = [o for o in all_orders if o.status == "completed"]
    cancelled = [o for o in all_orders if o.status == "cancelled"]
    revenue = sum(float(o.total_price) for o in completed)

    await callback.message.edit_text(
        f"📊 <b>Статистика</b>\n\n"
        f"✅ Выполнено заказов: {len(completed)}\n"
        f"❌ Отменено: {len(cancelled)}\n"
        f"📦 Всего заказов: {len(all_orders)}\n\n"
        f"💰 Выручка: {revenue:.2f} ₽",
        parse_mode="HTML",
    )

    await callback.answer()

