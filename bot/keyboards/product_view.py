from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def product_view_keyboard(
        category_id: int,
        product_id: int,
        index: int,
        total: int,
):
    keyboard = [
        [
            InlineKeyboardButton(
                text="🛒 В корзину",
                callback_data=f"cart:{product_id}",
            )
        ]
    ]

    navigation = []

    if index > 0:
        navigation.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"product_prev:{category_id}:{index}",
            )
        )

    if index < total - 1:
        navigation.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"product_next:{category_id}:{index}",
            )
        )

    if navigation:
        keyboard.append(navigation)

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔙 Категории",
                callback_data="catalog_back",
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )