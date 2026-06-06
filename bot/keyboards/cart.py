from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def cart_item_keyboard(
        cart_item_id: int,
        current_index: int,
        total: int,
        quantity: int,
) -> InlineKeyboardMarkup:
    """
    Клавиатура для одного товара в корзине.
    Показывает навигацию если товаров > 1.
    """
    keyboard = []

    # Строка: количество и управление им
    keyboard.append([
        InlineKeyboardButton(
            text="➖",
            callback_data=f"minus:{cart_item_id}",
        ),
        InlineKeyboardButton(
            text=f"  {quantity} шт.  ",
            callback_data="noop",  # просто отображение, не кликабельно
        ),
        InlineKeyboardButton(
            text="➕",
            callback_data=f"plus:{cart_item_id}",
        ),
    ])

    # Навигация между товарами (только если товаров больше одного)
    if total > 1:
        prev_index = (current_index - 1) % total
        next_index = (current_index + 1) % total

        keyboard.append([
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"cart_page:{prev_index}",
            ),
            InlineKeyboardButton(
                text=f"{current_index + 1} / {total}",
                callback_data="noop",
            ),
            InlineKeyboardButton(
                text="▶️",
                callback_data=f"cart_page:{next_index}",
            ),
        ])

    # Удалить товар
    keyboard.append([
        InlineKeyboardButton(
            text="🗑 Удалить из корзины",
            callback_data=f"delete:{cart_item_id}",
        ),
    ])

    # Оформить заказ
    keyboard.append([
        InlineKeyboardButton(
            text="🧾 Оформить заказ",
            callback_data="checkout",
        ),
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def empty_cart_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для пустой корзины."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛍 В каталог",
                    callback_data="open_catalog",
                )
            ]
        ]
    )