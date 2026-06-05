from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.admin_payment import payment_confirm_keyboard
from bot.keyboards.payment import payment_keyboard
from config import ADMIN_IDS
from bot.keyboards.cart import cart_keyboard, checkout_keyboard
from repositories.cart import CartRepository
from repositories.user import UserRepository
from repositories.order import OrderRepository

order_repository = OrderRepository()

router = Router()

cart_repository = CartRepository()
user_repository = UserRepository()


def build_cart_item_text(item):
    total = item.quantity * item.product.price

    return (
        f"🛒 {item.product.name}\n\n"
        f"Количество: {item.quantity}\n"
        f"Цена за шт: {item.product.price} ₽\n"
        f"Сумма: {total} ₽"
    )


@router.message(
    F.text == "🛒 Корзина"
)
async def cart_button(
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

    items = await cart_repository.get_user_cart(
        session=session,
        user_id=user.id,
    )

    if not items:
        await message.answer(
            "Корзина пуста 🛒"
        )
        return

    total = sum(
        item.quantity * float(item.product.price)
        for item in items
    )

    for item in items:
        await message.answer(
            text=(
                f"🛒 {item.product.name}\n\n"
                f"Количество: {item.quantity}\n"
                f"Цена: {item.product.price} ₽"
            ),
            reply_markup=cart_keyboard(
                item.id
            )
        )

    await message.answer(
        text=f"💰 Итого: {total:.2f} ₽",
        reply_markup=checkout_keyboard(),
    )


@router.callback_query(lambda c: c.data == "checkout")
async def checkout_handler(
        callback: CallbackQuery,
        session: AsyncSession,
):
    user = await user_repository.get_by_telegram_id(
        session=session,
        telegram_id=callback.from_user.id,
    )
    if not user.first_name:
        await callback.answer(
            "Заполните имя в профиле",
            show_alert=True,
        )
        return

    if not user.phone:
        await callback.answer(
            "Заполните телефон в профиле",
            show_alert=True,
        )
        return

    if not user.address:
        await callback.answer(
            "Заполните адрес в профиле",
            show_alert=True,
        )
        return

    items = await cart_repository.get_user_cart(
        session=session,
        user_id=user.id,
    )

    if not items:
        await callback.answer(
            "Корзина пуста",
            show_alert=True,
        )
        return

    for item in items:
        if item.product.stock < item.quantity:
            await callback.answer(
                (
                    f"Недостаточно товара:\n"
                    f"{item.product.name}\n"
                    f"Остаток: {item.product.stock} шт."
                ),
                show_alert=True,
            )
            return

    total_price = sum(
        item.quantity * float(item.product.price)
        for item in items
    )

    order = await order_repository.create_order(
        session=session,
        user_id=user.id,
        items=items,
        total_price=total_price,
    )

    await cart_repository.clear_cart(
        session=session,
        user_id=user.id,
    )

    await callback.message.answer(
        f"✅ Заказ №{order.id} создан\n\n"
        f"💰 К оплате: {total_price:.2f} ₽\n\n"
        f"Переведите указанную сумму на номер карты:\n\n"
        f"<b>💰 OZON BANK 💰</b>\n"
        f"Ермилов Евгений\n"
        f"<code>2204320905741320</code>\n\n"
        f"После оплаты нажмите кнопку ниже.",
        reply_markup=payment_keyboard(order.id),
        parse_mode="HTML",
    )

    admin_text = (
        f"🆕 Новый заказ #{order.id}\n\n"
        f"👤 Имя: {user.first_name or 'Не указано'}\n"
        f"📱 Телефон: {user.phone or 'Не указан'}\n"
        f"📍 Адрес: {user.address or 'Не указан'}\n"
        f"🆔 Telegram: @{callback.from_user.username}\n\n"
        f"💰 Сумма: {total_price:.2f} ₽\n\n"
        f"Товары:\n"
    )
    for item in items:
        admin_text += (
            f"• {item.product.name} "
            f"x {item.quantity}\n"
        )

    for admin_id in ADMIN_IDS:
        await callback.bot.send_message(
            chat_id=admin_id,
            text=admin_text,
        )

    await callback.answer()


@router.callback_query(
    F.data.startswith("paid:")
)
async def paid_handler(
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
    if order.status != "waiting_payment":
        await callback.answer(
            "Заявка уже отправлена",
            show_alert=True,
        )
        return

    admin_text = (
        f"💳 Заявка на подтверждение оплаты\n\n"
        f"Заказ №{order.id}\n"
        f"Сумма: {order.total_price} ₽\n\n"
        f"Пользователь сообщил, что оплатил заказ."
    )

    for admin_id in ADMIN_IDS:
        await callback.bot.send_message(
            chat_id=admin_id,
            text=admin_text,
            reply_markup=payment_confirm_keyboard(
                order.id
            )
        )

    await order_repository.update_status(
        session=session,
        order_id=order_id,
        status="payment_check",
    )

    await callback.message.edit_text(
        "⏳ Заявка на проверку оплаты отправлена.\n\n"
        "Пожалуйста, дождитесь подтверждения администратора.\n"
        "После проверки вы получите уведомление."
    )

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("plus:"))
async def plus_handler(
        callback: CallbackQuery,
        session: AsyncSession,
):
    cart_item_id = int(
        callback.data.split(":")[1]
    )

    item = await cart_repository.get_item(
        session=session,
        cart_item_id=cart_item_id,
    )

    if item is None:
        await callback.answer(
            "Товар не найден",
            show_alert=True,
        )
        return

    if item.quantity >= item.product.stock:
        await callback.answer(
            "Больше товара нет на складе",
            show_alert=True,
        )
        return

    await cart_repository.increase_quantity(
        session=session,
        cart_item_id=cart_item_id,
    )

    item = await cart_repository.get_item(
        session=session,
        cart_item_id=cart_item_id,
    )

    await callback.message.edit_text(
        text=build_cart_item_text(item),
        reply_markup=cart_keyboard(item.id),
    )

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("minus:"))
async def minus_handler(
        callback: CallbackQuery,
        session: AsyncSession,
):
    cart_item_id = int(
        callback.data.split(":")[1]
    )

    await cart_repository.decrease_quantity(
        session=session,
        cart_item_id=cart_item_id,
    )

    item = await cart_repository.get_item(
        session=session,
        cart_item_id=cart_item_id,
    )

    if item is None:
        await callback.message.delete()
    else:
        await callback.message.edit_text(
            text=build_cart_item_text(item),
            reply_markup=cart_keyboard(item.id),
        )

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("delete:"))
async def delete_handler(
        callback: CallbackQuery,
        session: AsyncSession,
):
    cart_item_id = int(
        callback.data.split(":")[1]
    )

    await cart_repository.remove_item(
        session=session,
        cart_item_id=cart_item_id,
    )

    await callback.message.delete()

    await callback.answer(
        "Товар удалён"
    )
