from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="cancel_fsm",
                )
            ]
        ]
    )
