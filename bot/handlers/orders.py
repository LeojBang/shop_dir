from datetime import timedelta

from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from sqlalchemy.ext.asyncio import AsyncSession

from bot.utils.order_status import ORDER_STATUSES
from repositories.order import OrderRepository
from repositories.user import UserRepository

router = Router()

order_repository = OrderRepository()
user_repository = UserRepository()


def orders_list_keyboard(orders) -> InlineKeyboardMarkup:
    """Список заказов — каждый заказ одной кнопкой."""
    buttons = []

    for order in orders:
        status = ORDER_STATUSES.get(order.status, order.status)
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"№{order.id}  {status}  · {order.total_price} ₽",
                    callback_data=f"order_detail:{order.id}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def order_detail_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Кнопка назад в списке деталей заказа."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="◀️ К списку заказов",
                    callback_data="my_orders_list",
                )
            ]
        ]
    )


def build_order_detail_text(order) -> str:
    """Формирует текст с деталями заказа."""
    date = (order.created_at + timedelta(hours=3)).strftime("%d.%m.%Y %H:%M")
    status = ORDER_STATUSES.get(order.status, order.status)

    lines = [
        f"<b>Заказ №{order.id}</b>",
        f"Статус: {status}",
        f"📅 {date}",
        f"💰 Сумма: {order.total_price} ₽",
        "",
        "🛒 <b>Состав:</b>",
    ]

    for item in order.items:
        price = item.price * item.quantity
        lines.append(f"• {item.product.name} × {item.quantity} = {price} ₽")

    if order.tracking_number:
        lines += [
            "",
            "📦 <b>Трек-номер:</b>",
            f"<code>{order.tracking_number}</code>",
            "",
            "Отслеживание: https://tracking.ozon.ru/",
        ]

    return "\n".join(lines)


# ── Список заказов ───────────────────────────────────────────────────────────


@router.message(F.text == "📋 Мои заказы")
async def my_orders(
    message: Message,
    session: AsyncSession,
):
    user = await user_repository.get_by_telegram_id(
        session=session,
        telegram_id=message.from_user.id,
    )

    if not user:
        await message.answer("Пользователь не найден")
        return

    orders = await order_repository.get_user_orders(
        session=session,
        user_id=user.id,
    )

    if not orders:
        await message.answer("У вас пока нет заказов 📦")
        return

    await message.answer(
        f"📦 <b>Ваши заказы</b> ({len(orders)} шт.)\n\n"
        "Нажмите на заказ чтобы увидеть детали:",
        reply_markup=orders_list_keyboard(orders),
        parse_mode="HTML",
    )


# ── Детали заказа ────────────────────────────────────────────────────────────


@router.callback_query(F.data.startswith("order_detail:"))
async def order_detail(
    callback: CallbackQuery,
    session: AsyncSession,
):
    order_id = int(callback.data.split(":")[1])

    order = await order_repository.get_order(
        session=session,
        order_id=order_id,
    )

    if not order:
        await callback.answer("Заказ не найден", show_alert=True)
        return

    await callback.message.edit_text(
        text=build_order_detail_text(order),
        reply_markup=order_detail_keyboard(order_id),
        parse_mode="HTML",
    )

    await callback.answer()


# ── Назад к списку ───────────────────────────────────────────────────────────


@router.callback_query(F.data == "my_orders_list")
async def back_to_orders_list(
    callback: CallbackQuery,
    session: AsyncSession,
):
    user = await user_repository.get_by_telegram_id(
        session=session,
        telegram_id=callback.from_user.id,
    )

    orders = await order_repository.get_user_orders(
        session=session,
        user_id=user.id,
    )

    await callback.message.edit_text(
        f"📦 <b>Ваши заказы</b> ({len(orders)} шт.)\n\n"
        "Нажмите на заказ чтобы увидеть детали:",
        reply_markup=orders_list_keyboard(orders),
        parse_mode="HTML",
    )

    await callback.answer()
