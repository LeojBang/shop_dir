from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def orders_filter_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🆕 Новые",
                    callback_data="orders_status:new",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💳 Ожидают оплату",
                    callback_data="orders_status:waiting_payment",
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Оплачены",
                    callback_data="orders_status:paid",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отменены",
                    callback_data="orders_status:cancelled",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="admin_back",
                )
            ],
        ]
    )
