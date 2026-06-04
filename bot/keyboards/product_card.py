from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def product_card_keyboard(
        product_id: int,
        category_id: int,
):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 В корзину",
                    callback_data=f"cart:{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ К товарам",
                    callback_data=f"category:{category_id}",
                )
            ]
        ]
    )