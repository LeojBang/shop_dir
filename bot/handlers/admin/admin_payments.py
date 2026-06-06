from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.order import OrderRepository
from models import User

router = Router()

order_repository = OrderRepository()


@router.callback_query(F.data.startswith("confirm_payment:"))
async def confirm_payment(
    callback: CallbackQuery,
    session: AsyncSession,
):
    order_id = int(callback.data.split(":")[1])

    order = await order_repository.get_order(
        session=session,
        order_id=order_id,
    )

    # Проблема 1 — не было проверки что заказ существует
    if not order:
        await callback.answer("Заказ не найден", show_alert=True)
        await callback.message.edit_text("❌ Заказ не найден")
        return

    if order.status not in ("waiting_payment", "payment_check"):
        await callback.answer("Заказ уже обработан", show_alert=True)
        return

    await order_repository.update_status(
        session=session,
        order_id=order_id,
        status="processing",
    )

    user = await session.get(User, order.user_id)
    await callback.bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f"✅ Оплата заказа №{order.id} подтверждена.\n\n"
            f"Заказ передан в обработку."
        ),
    )

    await callback.message.edit_text(
        f"✅ Заказ №{order.id} — оплата подтверждена\n" f"Статус: 📦 В обработке"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("reject_payment:"))
async def reject_payment(
    callback: CallbackQuery,
    session: AsyncSession,
):
    order_id = int(callback.data.split(":")[1])

    order = await order_repository.get_order(
        session=session,
        order_id=order_id,
    )

    # Проблема 2 — не было проверки статуса, можно было отклонить дважды
    if not order:
        await callback.answer("Заказ не найден", show_alert=True)
        await callback.message.edit_text("❌ Заказ не найден")
        return

    if order.status not in ("waiting_payment", "payment_check"):
        await callback.answer("Заказ уже обработан", show_alert=True)
        return

    # Возвращаем товары на склад
    for item in order.items:
        item.product.stock += item.quantity

    await order_repository.update_status(
        session=session,
        order_id=order_id,
        status="cancelled",
    )
    await session.commit()

    user = await session.get(User, order.user_id)
    await callback.bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f"❌ Оплата заказа №{order.id} не найдена.\n\n"
            f"Если вы уже оплатили — свяжитесь с поддержкой."
        ),
    )

    await callback.message.edit_text(
        f"❌ Заказ №{order.id} — оплата отклонена\n" f"Статус: Отменён"
    )
    await callback.answer()
