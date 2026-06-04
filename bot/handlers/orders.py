from aiogram import Router, F
from aiogram.types import Message
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from bot.utils.order_status import ORDER_STATUSES
from repositories.order import OrderRepository
from repositories.user import UserRepository

router = Router()

order_repository = OrderRepository()
user_repository = UserRepository()


@router.message(
    F.text == "📋 Мои заказы"
)
async def my_orders(
        message: Message,
        session: AsyncSession,
):
    user = await user_repository.get_by_telegram_id(
        session=session,
        telegram_id=message.from_user.id,
    )

    if not user:
        await message.answer(
            "Пользователь не найден"
        )
        return

    orders = await order_repository.get_user_orders(
        session=session,
        user_id=user.id,
    )

    if not orders:
        await message.answer(
            "У вас пока нет заказов 📦"
        )
        return

    text = "📦 Ваши заказы\n\n"

    for order in orders:

        date = (
                order.created_at + timedelta(hours=3)
        ).strftime("%d.%m.%Y %H:%M")

        text += (
            f"Заказ №{order.id}\n"
            f"Статус: {ORDER_STATUSES.get(order.status, order.status)}\n"
            f"📅 {date}\n\n"
            f"Сумма: {order.total_price} ₽\n"
            f"Товары:\n"
        )
        if order.tracking_number:
            text += (
                f"\n📦 Трек-номер:\n"
                f"{order.tracking_number}\n"
            )

        for item in order.items:
            text += (
                f"• {item.product.name} "
                f"x {item.quantity}\n"
            )

        text += "\n"

    await message.answer(text)
