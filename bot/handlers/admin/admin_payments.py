from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.order import OrderRepository
from models import User

router = Router()

order_repository = OrderRepository()


@router.callback_query(
    F.data.startswith("confirm_payment:")
)
async def confirm_payment(
        callback: CallbackQuery,
        session: AsyncSession,
):
    order_id = int(
        callback.data.split(":")[1]
    )

    order = await order_repository.get_order(
        session=session,
        order_id=order_id,
    )
    if order.status not in (
            "waiting_payment",
            "payment_check",
    ):
        await callback.answer(
            "Заказ уже обработан",
            show_alert=True,
        )
        return

    await order_repository.update_status(
        session=session,
        order_id=order_id,
        status="processing",
    )
    user = await session.get(
        User,
        order.user_id,
    )
    await callback.bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f"✅ Оплата заказа №{order.id} подтверждена.\n\n"
            f"Заказ передан в обработку."
        )
    )
    await callback.message.edit_text(
        f"💰 Заказ №{order.id}\n"
        f"Оплата подтверждена"
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("reject_payment:")
)
async def reject_payment(
        callback: CallbackQuery,
        session: AsyncSession,
):
    order_id = int(
        callback.data.split(":")[1]
    )

    order = await order_repository.get_order(
        session=session,
        order_id=order_id,
    )

    user = await session.get(
        User,
        order.user_id,
    )

    await callback.bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f"❌ Оплата заказа №{order.id} не найдена.\n\n"
            f"Если вы уже оплатили заказ, "
            f"свяжитесь с поддержкой."
        )
    )

    await callback.message.edit_text(
        f"❌ Заказ №{order.id}\n"
        f"Оплата отклонена"
    )
    for item in order.items:
        item.product.stock += item.quantity

    await session.commit()
    await callback.answer()
