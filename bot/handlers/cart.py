from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.cart import cart_item_keyboard, empty_cart_keyboard
from repositories.cart import CartRepository
from repositories.user import UserRepository
from repositories.order import OrderRepository

order_repository = OrderRepository()
router = Router()
cart_repository = CartRepository()
user_repository = UserRepository()
# Показываем прогресс до минимальной суммы
MIN_ORDER_AMOUNT = 7000


def build_cart_text(item, current_index: int, total: int, all_items) -> str:
    """Формирует текст карточки товара в корзине."""
    total_sum = sum(i.quantity * i.product.price for i in all_items)
    item_sum = item.quantity * item.product.price

    lines = [
        f"🛒 <b>Корзина</b>  ({current_index + 1}/{total})",
        "",
        f"<b>{item.product.name}</b>",
        f"Цена за шт.: {item.product.price} ₽",
        f"Количество: {item.quantity} шт.",
        f"Сумма: <b>{item_sum} ₽</b>",
    ]
    lines += [
        "",
        f"💰 Итого по корзине: <b>{total_sum} ₽</b>",
        "🚚 Доставка: бесплатно",
    ]

    if total_sum < MIN_ORDER_AMOUNT:
        lines.append(
            f"⚠️ Минимальный заказ {MIN_ORDER_AMOUNT} ₽ · не хватает {MIN_ORDER_AMOUNT - total_sum:.0f} ₽"
        )
    else:
        lines.append("✅ Сумма заказа достаточна для оформления")

    if item.product.stock <= 3:
        lines.append(f"⚠️ Осталось на складе: {item.product.stock} шт.")

    lines += [
        "",
        f"💰 Итого по корзине: <b>{total_sum} ₽</b>",
    ]

    return "\n".join(lines)


async def show_cart_page(
    target,  # Message или CallbackQuery
    session: AsyncSession,
    page: int = 0,
    edit: bool = False,
):
    """Универсальная функция показа страницы корзины."""
    # Получаем пользователя
    tg_id = target.from_user.id if isinstance(target, Message) else target.from_user.id

    user = await user_repository.get_by_telegram_id(
        session=session,
        telegram_id=tg_id,
    )

    if not user:
        msg = "Пользователь не найден"
        if isinstance(target, Message):
            await target.answer(msg)
        else:
            await target.answer(msg, show_alert=True)
        return

    items = await cart_repository.get_user_cart(
        session=session,
        user_id=user.id,
    )

    if not items:
        text = "🛒 Корзина пуста"
        if isinstance(target, Message):
            await target.answer(text, reply_markup=empty_cart_keyboard())
        else:
            await target.message.edit_text(text, reply_markup=empty_cart_keyboard())
        return

    # Защита от выхода за границы после удаления товара
    page = min(page, len(items) - 1)

    item = items[page]
    text = build_cart_text(item, page, len(items), items)
    keyboard = cart_item_keyboard(
        cart_item_id=item.id,
        current_index=page,
        total=len(items),
        quantity=item.quantity,
    )

    if isinstance(target, Message):
        await target.answer(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await target.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")


# ── Открыть корзину ──────────────────────────────────────────────────────────


@router.message(F.text == "🛒 Корзина")
async def cart_button(message: Message, session: AsyncSession):
    await show_cart_page(message, session, page=0, edit=False)


# ── Навигация между товарами ─────────────────────────────────────────────────


@router.callback_query(F.data.startswith("cart_page:"))
async def cart_page(callback: CallbackQuery, session: AsyncSession):
    page = int(callback.data.split(":")[1])
    await show_cart_page(callback, session, page=page, edit=True)
    await callback.answer()


# ── Увеличить количество ─────────────────────────────────────────────────────


@router.callback_query(F.data.startswith("plus:"))
async def plus_handler(callback: CallbackQuery, session: AsyncSession):
    cart_item_id = int(callback.data.split(":")[1])

    item = await cart_repository.get_item(
        session=session,
        cart_item_id=cart_item_id,
    )

    if item is None:
        await callback.answer("Товар не найден", show_alert=True)
        return

    if item.quantity >= item.product.stock:
        await callback.answer(
            f"Больше нет на складе (доступно {item.product.stock} шт.)",
            show_alert=True,
        )
        return

    await cart_repository.increase_quantity(
        session=session,
        cart_item_id=cart_item_id,
    )

    # Узнаём текущую страницу из корзины чтобы остаться на ней
    user = await user_repository.get_by_telegram_id(
        session=session,
        telegram_id=callback.from_user.id,
    )
    items = await cart_repository.get_user_cart(session=session, user_id=user.id)
    page = next((i for i, it in enumerate(items) if it.id == cart_item_id), 0)

    await show_cart_page(callback, session, page=page, edit=True)
    await callback.answer()


# ── Уменьшить количество ─────────────────────────────────────────────────────


@router.callback_query(F.data.startswith("minus:"))
async def minus_handler(callback: CallbackQuery, session: AsyncSession):
    cart_item_id = int(callback.data.split(":")[1])

    await cart_repository.decrease_quantity(
        session=session,
        cart_item_id=cart_item_id,
    )

    user = await user_repository.get_by_telegram_id(
        session=session,
        telegram_id=callback.from_user.id,
    )
    items = await cart_repository.get_user_cart(session=session, user_id=user.id)

    if not items:
        await callback.message.edit_text(
            "🛒 Корзина пуста",
            reply_markup=empty_cart_keyboard(),
        )
        await callback.answer()
        return

    page = next((i for i, it in enumerate(items) if it.id == cart_item_id), 0)
    # Если товар удалился (quantity был 1) — остаёмся на той же позиции
    page = min(page, len(items) - 1)

    await show_cart_page(callback, session, page=page, edit=True)
    await callback.answer()


# ── Удалить товар ────────────────────────────────────────────────────────────


@router.callback_query(F.data.startswith("delete:"))
async def delete_handler(callback: CallbackQuery, session: AsyncSession):
    cart_item_id = int(callback.data.split(":")[1])

    user = await user_repository.get_by_telegram_id(
        session=session,
        telegram_id=callback.from_user.id,
    )
    items = await cart_repository.get_user_cart(session=session, user_id=user.id)
    current_page = next((i for i, it in enumerate(items) if it.id == cart_item_id), 0)

    await cart_repository.remove_item(
        session=session,
        cart_item_id=cart_item_id,
    )

    items_after = await cart_repository.get_user_cart(
        session=session,
        user_id=user.id,
    )

    if not items_after:
        await callback.message.edit_text(
            "🛒 Корзина пуста",
            reply_markup=empty_cart_keyboard(),
        )
        await callback.answer("Товар удалён")
        return

    # После удаления переходим на предыдущий товар
    page = max(0, current_page - 1)
    await show_cart_page(callback, session, page=page, edit=True)
    await callback.answer("Товар удалён")


# ── Оформить заказ ───────────────────────────────────────────────────────────


async def _check_user_profile(user, callback) -> bool:
    """Проверяет заполненность профиля. Возвращает False если что-то не заполнено."""
    if not user.first_name:
        await callback.answer("Заполните имя в профиле", show_alert=True)
        return False
    if not user.phone:
        await callback.answer("Заполните телефон в профиле", show_alert=True)
        return False
    if not user.address:
        await callback.answer("Заполните адрес в профиле", show_alert=True)
        return False
    return True


@router.callback_query(F.data == "checkout")
async def checkout_handler(callback: CallbackQuery, session: AsyncSession):
    from core.config import settings
    from repositories.payment_settings import PaymentSettingsRepository
    from bot.keyboards.payment import payment_keyboard

    user = await user_repository.get_by_telegram_id(
        session=session,
        telegram_id=callback.from_user.id,
    )

    if not await _check_user_profile(user, callback):
        return

    items = await cart_repository.get_user_cart(session=session, user_id=user.id)
    total_price = sum(item.quantity * float(item.product.price) for item in items)
    if total_price < MIN_ORDER_AMOUNT:
        await callback.answer(
            f"Минимальная сумма заказа — {MIN_ORDER_AMOUNT} ₽\n"
            f"Ваша корзина: {total_price:.0f} ₽\n"
            f"Добавьте ещё товаров на {MIN_ORDER_AMOUNT - total_price:.0f} ₽",
            show_alert=True,
        )
        return
    if not items:
        await callback.answer("Корзина пуста", show_alert=True)
        return

    for item in items:
        if item.product.stock < item.quantity:
            await callback.answer(
                f"Недостаточно товара: {item.product.name}\n"
                f"Остаток: {item.product.stock} шт.",
                show_alert=True,
            )
            return

    total_price = sum(item.quantity * float(item.product.price) for item in items)

    try:
        order = await order_repository.create_order(
            session=session,
            user_id=user.id,
            items=items,
            total_price=total_price,
        )
    except ValueError as e:
        await callback.answer(str(e), show_alert=True)
        return

    await cart_repository.clear_cart(session=session, user_id=user.id)

    pay_repo = PaymentSettingsRepository()
    pay = await pay_repo.get_or_default(session)

    await callback.message.answer(
        f"✅ Заказ №{order.id} создан\n\n"
        f"💰 К оплате: {total_price:.2f} ₽\n\n"
        f"Переведите указанную сумму на номер карты:\n\n"
        f"<b>💰 {pay.bank_name} 💰</b>\n"
        f"{pay.recipient}\n"
        f"<code>{pay.card_number}</code>\n\n"
        f"После оплаты нажмите кнопку ниже.",
        reply_markup=payment_keyboard(order.id),
        parse_mode="HTML",
    )

    admin_text = (
        f"🆕 Новый заказ #{order.id}\n\n"
        f"👤 {user.first_name}\n"
        f"📱 {user.phone}\n"
        f"📍 {user.address}\n"
        f"🆔 @{callback.from_user.username}\n\n"
        f"💰 {total_price:.2f} ₽\n\nТовары:\n"
    )
    for item in items:
        admin_text += f"• {item.product.name} × {item.quantity}\n"

    for admin_id in settings.ADMIN_IDS:
        await callback.bot.send_message(chat_id=admin_id, text=admin_text)

    await callback.answer()


# ── Кнопка "В каталог" из пустой корзины ────────────────────────────────────


@router.callback_query(F.data == "open_catalog")
async def open_catalog(callback: CallbackQuery, session: AsyncSession):
    from repositories.category import CategoryRepository
    from bot.keyboards.catalog import categories_keyboard

    categories = await CategoryRepository().get_all(session=session)

    await callback.message.edit_text(
        "🏋️ Категории товаров",
        reply_markup=categories_keyboard(categories),
    )
    await callback.answer()


# ── Я оплатил ────────────────────────────────────────────────────────────────


@router.callback_query(F.data.startswith("paid:"))
async def paid_handler(callback: CallbackQuery, session: AsyncSession):
    from core.config import settings
    from bot.keyboards.admin_payment import payment_confirm_keyboard

    order_id = int(callback.data.split(":")[1])

    order = await order_repository.get_order(
        session=session,
        order_id=order_id,
    )

    if not order:
        await callback.answer("Заказ не найден", show_alert=True)
        return

    if order.status != "waiting_payment":
        await callback.answer("Заявка уже отправлена", show_alert=True)
        return

    await order_repository.update_status(
        session=session,
        order_id=order_id,
        status="payment_check",
    )

    admin_text = (
        f"💳 Заявка на подтверждение оплаты\n\n"
        f"Заказ №{order.id}\n"
        f"Сумма: {order.total_price} ₽\n\n"
        f"Пользователь сообщил, что оплатил заказ."
    )

    for admin_id in settings.ADMIN_IDS:
        await callback.bot.send_message(
            chat_id=admin_id,
            text=admin_text,
            reply_markup=payment_confirm_keyboard(order.id),
        )

    await callback.message.edit_text(
        "⏳ Заявка на проверку оплаты отправлена.\n\n"
        "Дождитесь подтверждения администратора.\n"
        "После проверки вы получите уведомление."
    )

    await callback.answer()


# ── Заглушка для некликабельных кнопок ──────────────────────────────────────


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()
