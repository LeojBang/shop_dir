from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def profile_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👤 Имя",
                    callback_data="edit_name",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📱 Телефон",
                    callback_data="edit_phone",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Адрес выдачи OZON",
                    callback_data="edit_address",
                )
            ],
        ]
    )
