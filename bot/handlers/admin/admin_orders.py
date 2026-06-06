from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram import F
from datetime import timedelta

from bot.keyboards.admin_orders_filter import orders_filter_keyboard
from bot.keyboards.admin_orders_menu import admin_orders_menu_keyboard
from bot.states.order import TrackingState
from models import User
from repositories.order import OrderRepository
from sqlalchemy.ext.asyncio import AsyncSession
from bot.utils.order_status import ORDER_STATUSES
from bot.keyboards.admin_orders import order_status_keyboard
from bot.filters.admin import AdminFilter

router = Router()

order_repository = OrderRepository()
router.message.filter(AdminFilter())


# ── Вспомогательные функции ──────────────────────────────────────────────────


def safe_user_info(user) -> tuple[str, str, str]:
    """Безопасно возвращает данные пользователя даже если user=None."""
    if user is None:
        return "не указано", "не указан", "не указан"
    return (
        user.first_name or "не указано",
        user.phone or "не указан",
        user.address or "не указан",
    )


def build_order_text(order, user) -> str:
    name, phone, address = safe_user_info(user)
    date = (order.created_at + timedelta(hours=3)).strftime("%d.%m.%Y %H:%M")
    status = ORDER_STATUSES.get(order.status, order.status)

    lines = [
        f"<b>Заказ №{order.id}</b>",
        f"Статус: {status}",
        f"📅 {date}",
        f"💰 {order.total_price} ₽",
        "",
        f"👤 {name}",
        f"📱 {phone}",
        f"📍 {address}",
        "",
        "🛒 Товары:",
    ]

    for item in order.items:
        lines.append(f"• {item.product.name} × {item.quantity}")

    if order.tracking_number:
        lines += ["", f"📦 Трек: <code>{order.tracking_number}</code>"]

    return "\n".join(lines)


def orders_buttons_keyboard(orders) -> InlineKeyboardMarkup:
    """Список заказов кнопками."""
    buttons = []
    for order in orders:
        status = ORDER_STATUSES.get(order.status, order.status)
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"№{order.id}  {status}  · {order.total_price} ₽",
                    callback_data=f"show_order:{order.id}",
                )
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data="admin_orders_menu",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ── Меню заказов ─────────────────────────────────────────────────────────────


@router.callback_query(F.data == "admin_orders_menu")
async def admin_orders_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🧾 Управление заказами",
        reply_markup=admin_orders_menu_keyboard(),
    )
    await callback.answer()


# ── Активные заказы ──────────────────────────────────────────────────────────


@router.callback_query(F.data == "admin_orders")
async def admin_orders_button(
    callback: CallbackQuery,
    session: AsyncSession,
):
    orders = await order_repository.get_new_orders(session=session)

    if not orders:
        await callback.answer("Новых заказов нет", show_alert=True)
        return

    await callback.message.edit_text(
        f"📦 Активные заказы ({len(orders)} шт.)\n\nВыберите заказ:",
        reply_markup=orders_buttons_keyboard(orders),
    )
    await callback.answer()


# ── Все заказы ───────────────────────────────────────────────────────────────


@router.callback_query(F.data == "admin_orders_all")
async def admin_orders_all(
    callback: CallbackQuery,
    session: AsyncSession,
):
    orders = await order_repository.get_all_orders(session=session)

    if not orders:
        await callback.answer("Заказов нет", show_alert=True)
        return

    await callback.message.edit_text(
        f"📋 Все заказы ({len(orders)} шт.)\n\nВыберите заказ:",
        reply_markup=orders_buttons_keyboard(orders),
    )
    await callback.answer()


# ── Детали заказа ────────────────────────────────────────────────────────────


@router.callback_query(F.data.startswith("show_order:"))
async def show_order(
    callback: CallbackQuery,
    session: AsyncSession,
):
    order_id = int(callback.data.split(":")[1])
    order = await order_repository.get_order(session=session, order_id=order_id)

    if not order:
        await callback.answer("Заказ не найден", show_alert=True)
        return

    # Исправление NoneType: session.get может вернуть None
    user = await session.get(User, order.user_id)

    await callback.message.edit_text(
        build_order_text(order, user),
        reply_markup=order_status_keyboard(order.id, order.status),
        parse_mode="HTML",
    )
    await callback.answer()


# ── Фильтр по статусу ────────────────────────────────────────────────────────


@router.callback_query(F.data == "orders_filters")
async def orders_filters(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите статус заказов:",
        reply_markup=orders_filter_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("orders_status:"))
async def orders_by_status(
    callback: CallbackQuery,
    session: AsyncSession,
):
    status = callback.data.split(":")[1]
    orders = await order_repository.get_orders_by_status(
        session=session,
        status=status,
    )

    if not orders:
        await callback.answer("Заказов нет", show_alert=True)
        return

    await callback.message.edit_text(
        f"📦 {ORDER_STATUSES.get(status, status)} ({len(orders)} шт.)\n\nВыберите заказ:",
        reply_markup=orders_buttons_keyboard(orders),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("back_to_status:"))
async def back_to_status(
    callback: CallbackQuery,
    session: AsyncSession,
):
    status = callback.data.split(":")[1]
    orders = await order_repository.get_orders_by_status(
        session=session,
        status=status,
    )

    await callback.message.edit_text(
        f"📦 {ORDER_STATUSES.get(status, status)} ({len(orders)} шт.)\n\nВыберите заказ:",
        reply_markup=orders_buttons_keyboard(orders),
    )
    await callback.answer()


# ── Действия над заказом ─────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("order_cancel:"))
async def order_cancel(callback: CallbackQuery, session: AsyncSession):
    order_id = int(callback.data.split(":")[1])
    order = await order_repository.get_order(session=session, order_id=order_id)

    if not order:
        await callback.answer("Заказ не найден", show_alert=True)
        return

    if order.status in ("completed", "cancelled"):
        await callback.answer("Заказ уже закрыт", show_alert=True)
        return

    # Возвращаем товары на склад
    for item in order.items:
        item.product.stock += item.quantity
    await session.commit()

    await order_repository.update_status(
        session=session, order_id=order_id, status="cancelled"
    )

    user = await session.get(User, order.user_id)
    if user:
        await callback.bot.send_message(
            chat_id=user.telegram_id,
            text=(
                f"❌ Ваш заказ №{order.id} отменён.\n\n"
                f"Свяжитесь с администратором для уточнения."
            ),
        )

    await callback.message.edit_text(f"❌ Заказ №{order_id} — отменён")
    await callback.answer()


@router.callback_query(F.data.startswith("order_processing:"))
async def order_processing(callback: CallbackQuery, session: AsyncSession):
    order_id = int(callback.data.split(":")[1])
    order = await order_repository.get_order(session=session, order_id=order_id)
    user = await session.get(User, order.user_id)

    await order_repository.update_status(
        session=session, order_id=order_id, status="processing"
    )

    if user:
        await callback.bot.send_message(
            chat_id=user.telegram_id,
            text=(
                f"📦 Заказ №{order.id} принят в работу.\n\n"
                f"Мы готовим его к отправке."
            ),
        )

    await callback.message.edit_text(
        f"📦 Заказ №{order_id} — в обработке",
    )
    await callback.answer()


# ── Трек-номер ───────────────────────────────────────────────────────────────


@router.callback_query(F.data.startswith("tracking:"))
async def tracking_number_start(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split(":")[1])
    await state.update_data(order_id=order_id)
    await state.set_state(TrackingState.waiting_tracking_number)
    await callback.message.answer("Введите трек-номер:")
    await callback.answer()


@router.message(TrackingState.waiting_tracking_number)
async def save_tracking_number(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.get_data()
    order_id = data["order_id"]
    tracking_number = message.text.strip()

    await order_repository.update_tracking_number(
        session=session,
        order_id=order_id,
        tracking_number=tracking_number,
    )
    await order_repository.update_status(
        session=session,
        order_id=order_id,
        status="completed",
    )

    order = await order_repository.get_order(session=session, order_id=order_id)
    user = await session.get(User, order.user_id)

    if user:
        await message.bot.send_message(
            chat_id=user.telegram_id,
            text=(
                f"🚚 Ваш заказ №{order.id} отправлен.\n\n"
                f"📦 Трек-номер:\n"
                f"<code>{tracking_number}</code>\n\n"
                f"Отслеживание: https://tracking.ozon.ru"
            ),
            parse_mode="HTML",
        )

    await message.answer(
        f"✅ Трек сохранён: {tracking_number}\n"
        f"Заказ переведён в статус «Отправлен»."
    )
    await state.clear()
