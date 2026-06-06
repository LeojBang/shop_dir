from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton


def cancel_tracking_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_tracking")]
        ]
    )
