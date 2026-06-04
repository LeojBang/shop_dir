from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup


def add_to_cart_keyboard(
    product_id: int,
):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Добавить в корзину",
                    callback_data=f"cart:{product_id}",
                )
            ]
        ]
    )

