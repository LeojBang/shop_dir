from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def products_list_keyboard(
        products,
        category_id: int,
):
    keyboard = []

    for product in products:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=product.name,
                    callback_data=f"product:{product.id}"
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="⬅️ Категории",
                callback_data="catalog_categories",
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )