from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup


def order_status_keyboard(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data=f"order_done:{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data=f"order_cancel:{order_id}"
                )
            ]
        ]
    )