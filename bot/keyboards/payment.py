from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def payment_keyboard(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 Я оплатил",
                    callback_data=f"paid:{order_id}",
                )
            ]
        ]
    )
