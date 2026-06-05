from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import F

from bot.keyboards.admin_orders_filter import orders_filter_keyboard
from bot.keyboards.admin_orders_menu import admin_orders_menu_keyboard
from bot.keyboards.cancel_tracking import cancel_tracking_keyboard
from bot.states.order import TrackingState
from models import User
from repositories.order import OrderRepository
from sqlalchemy.ext.asyncio import AsyncSession
from bot.utils.order_status import ORDER_STATUSES
from bot.keyboards.admin_orders import order_status_keyboard
from bot.filters.admin import AdminFilter
from bot.keyboards.orders_list_keyboard import (
    orders_list_keyboard
)
from bot.keyboards.order_detail_keyboard import (
    order_detail_keyboard
)

router = Router()

order_repository = OrderRepository()
router.message.filter(AdminFilter())


@router.callback_query(
    TrackingState.waiting_tracking_number,
    ~F.data.in_(["cancel_tracking"])
)
async def block_callbacks(
        callback: CallbackQuery,
):
    await callback.answer(
        "Сначала введите трек-номер или нажмите Отмена",
        show_alert=True,
    )


@router.callback_query(
    F.data == "admin_orders_menu"
)
async def admin_orders_menu(
        callback: CallbackQuery,
):
    await callback.message.edit_text(
        "🧾 Управление заказами",
        reply_markup=admin_orders_menu_keyboard(),
    )

    await callback.answer()


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
        user = await session.get(
            User,
            order.user_id,
        )
        text = (
            f"📦 Заказ #{order.id}\n"
            f"Статус: {ORDER_STATUSES.get(order.status)}\n"
            f"Сумма: {order.total_price} ₽\n\n"

            f"👤 {user.first_name}\n"
            f"📱 {user.phone}\n"
            f"📍 {user.address}\n\n"

            f"Товары:\n"
        )
        if order.tracking_number:
            text += (
                f"📦 Трек: "
                f"{order.tracking_number}\n\n"
            )

        for item in order.items:
            text += (
                f"• {item.product.name} "
                f"x {item.quantity}\n"
            )

        await callback.message.answer(
            text,
            reply_markup=order_status_keyboard(
                order.id,
                order.status,
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


@router.callback_query(
    F.data == "admin_orders_all"
)
async def admin_orders_all(
        callback: CallbackQuery,
        session: AsyncSession,
):
    orders = await order_repository.get_all_orders(
        session=session
    )

    if not orders:
        await callback.answer(
            "Заказов нет",
            show_alert=True,
        )
        return

    for order in orders:
        user = await session.get(
            User,
            order.user_id,
        )
        text = (
            f"📦 Заказ #{order.id}\n"
            f"Статус: {ORDER_STATUSES.get(order.status)}\n"
            f"Сумма: {order.total_price} ₽\n\n"

            f"👤 {user.first_name}\n"
            f"📱 {user.phone}\n"
            f"📍 {user.address}\n\n"

            f"Товары:\n"
        )
        if order.tracking_number:
            text += (
                f"📦 Трек: "
                f"{order.tracking_number}\n\n"
            )

        for item in order.items:
            text += (
                f"• {item.product.name} "
                f"x {item.quantity}\n"
            )

        await callback.message.answer(
            text,
            reply_markup=order_status_keyboard(
                order.id,
                order.status,
            )
        )
    await callback.answer()


@router.callback_query(
    F.data == "orders_filters"
)
async def orders_filters(
        callback: CallbackQuery,
):
    await callback.message.edit_text(
        "Выберите статус заказов:",
        reply_markup=orders_filter_keyboard()
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("orders_status:")
)
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
        await callback.answer(
            "Заказов нет",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        (
            f"📦 Заказы: "
            f"{ORDER_STATUSES.get(status)}"
        ),
        reply_markup=orders_list_keyboard(
            orders
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("show_order:")
)
async def show_order(
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

    text = (
        f"📦 Заказ #{order.id}\n\n"
        f"Статус: "
        f"{ORDER_STATUSES.get(order.status)}\n\n"
        f"👤 {user.first_name}\n"
        f"📱 {user.phone}\n"
        f"📍 {user.address}\n\n"
        f"💰 {order.total_price} ₽\n\n"
        f"Товары:\n"
    )

    for item in order.items:
        text += (
            f"• {item.product.name} "
            f"x {item.quantity}\n"
        )

    if order.tracking_number:
        text += (
            f"\n📦 Трек:\n"
            f"{order.tracking_number}"
        )

    await callback.message.edit_text(
        text,
        reply_markup=order_detail_keyboard(
            order
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("back_to_status:")
)
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
        (
            f"📦 Заказы: "
            f"{ORDER_STATUSES.get(status)}"
        ),
        reply_markup=orders_list_keyboard(
            orders
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("order_complete:")
)
async def order_complete(
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

    await order_repository.update_status(
        session=session,
        order_id=order_id,
        status="completed",
    )

    await callback.bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f"✔️ Заказ №{order.id} выполнен.\n\n"
            f"Спасибо за покупку!"
        )
    )

    await callback.message.edit_text(
        f"📦 Заказ #{order.id}\n"
        f"Статус: ✔️ Выполнен"
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("tracking:")
)
async def tracking_number_start(
        callback: CallbackQuery,
        state: FSMContext,
):
    order_id = int(
        callback.data.split(":")[1]
    )

    await state.update_data(
        order_id=order_id
    )

    await state.set_state(
        TrackingState.waiting_tracking_number
    )

    await callback.message.answer(
        "Введите трек-номер:",
        reply_markup=cancel_tracking_keyboard()
    )

    await callback.answer()


@router.callback_query(
    F.data == "cancel_tracking"
)
async def cancel_tracking(
        callback: CallbackQuery,
        state: FSMContext,
):
    await state.clear()

    await callback.message.edit_text(
        "❌ Ввод трек-номера отменён"
    )

    await callback.answer()


@router.message(
    TrackingState.waiting_tracking_number
)
async def save_tracking_number(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
):
    data = await state.get_data()

    order_id = data["order_id"]

    tracking_number = message.text

    await order_repository.update_tracking_number(
        session=session,
        order_id=order_id,
        tracking_number=tracking_number,
    )

    await order_repository.update_status(
        session=session,
        order_id=order_id,
        status="shipped",
    )
    order = await order_repository.get_order(
        session=session,
        order_id=order_id,
    )

    user = await session.get(
        User,
        order.user_id,
    )

    await message.bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f"🚚 Ваш заказ №{order.id} отправлен.\n\n"
            f"📦 Трек-номер:\n"
            f"{tracking_number}\n\n"
            f"Отслеживайте движение посылки "
            f"на сайте службы доставки."
        )
    )

    await message.answer(
        "✅ Трек сохранён.\n"
        "Заказ автоматически переведён в статус 'Отправлен'."
    )

    await state.clear()


@router.callback_query(
    F.data.startswith("order_processing:")
)
async def order_processing(
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

    await order_repository.update_status(
        session=session,
        order_id=order_id,
        status="processing",
    )

    await callback.bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f"📦 Заказ №{order.id} принят в работу.\n\n"
            f"Мы готовим его к отправке."
        )
    )

    await callback.message.edit_text(
        f"📦 Заказ #{order.id}\n"
        f"Статус: 📦 В обработке"
    )

    await callback.answer()
