from aiogram import Router
from aiogram.filters import Command

from bot.filters.admin import AdminFilter
from repositories.order import OrderRepository

router = Router()

order_repository = OrderRepository()


@router.message(
    Command("admin_orders"),
    AdminFilter(),
)
async def admin_orders(
    message,
    session,
):
    orders = await order_repository.get_all_orders(
        session=session
    )

    text = "📦 Все заказы\n\n"

    for order in orders:
        text += (
            f"Заказ #{order.id}\n"
            f"Пользователь: {order.user_id}\n"
            f"Статус: {order.status}\n"
            f"Сумма: {order.total_price} ₽\n\n"
        )

    await message.answer(text)