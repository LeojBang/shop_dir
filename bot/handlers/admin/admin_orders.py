from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram import F

from models import User
from repositories.order import OrderRepository
from sqlalchemy.ext.asyncio import AsyncSession
from bot.utils.order_status import ORDER_STATUSES
from bot.keyboards.admin_orders import order_status_keyboard
from bot.filters.admin import AdminFilter

router = Router()

order_repository = OrderRepository()
router.message.filter(AdminFilter())


@router.callback_query(
    F.data == "admin_orders"
)
async def admin_orders_button(
        callback: CallbackQuery,
        session: AsyncSession,
):
    orders = await order_repository.get_new_orders(
        session=session,
    )

    if not orders:
        await callback.message.answer(
            "Новых заказов нет"
        )

        await callback.answer()
        return

    for order in orders:
        text = (
            f"📦 Заказ #{order.id}\n"
            f"Статус: {ORDER_STATUSES.get(order.status, order.status)}\n"
            f"Сумма: {order.total_price} ₽\n\n"
            f"Товары:\n"
        )

        for item in order.items:
            text += (
                f"• {item.product.name} "
                f"x {item.quantity}\n"
            )

        await callback.message.answer(
            text,
            reply_markup=order_status_keyboard(
                order.id
            )
        )

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("order_done:"))
async def order_done(
        callback: CallbackQuery,
        session,
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

    await order_repository.update_status(
        session=session,
        order_id=order_id,
        status="completed",
    )
    await callback.bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f"✅ Ваш заказ №{order.id} подтвержден!\n\n"
            f"Скоро мы свяжемся с вами."
        )
    )
    await callback.message.edit_text(
        f"📦 Заказ #{order_id}\n"
        f"Статус: ✅ Выполнен"
    )

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("order_cancel:"))
async def order_cancel(
        callback: CallbackQuery,
        session,
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

    await order_repository.update_status(
        session=session,
        order_id=order_id,
        status="cancelled",
    )

    await callback.bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f"❌ Ваш заказ №{order.id} отменен.\n\n"
            f"Свяжитесь с администратором для уточнения."
        )
    )

    await callback.message.edit_text(
        f"📦 Заказ #{order_id}\n"
        f"Статус: ❌ Отменен"
    )

    await callback.answer()

