from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def cancel_tracking_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_tracking")]
        ]
    )
