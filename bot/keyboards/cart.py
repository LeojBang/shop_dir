from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def checkout_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🧾 Оформить заказ",
                    callback_data="checkout"
                )
            ]
        ]
    )


def cart_keyboard(
        cart_item_id: int,
):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➖",
                    callback_data=f"minus:{cart_item_id}",
                ),
                InlineKeyboardButton(
                    text="➕",
                    callback_data=f"plus:{cart_item_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"delete:{cart_item_id}",
                )
            ]
        ]
    )
