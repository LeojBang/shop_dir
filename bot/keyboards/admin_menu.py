from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup


def admin_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📦 Товары",
                    callback_data="admin_products",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🧾 Заказы",
                    callback_data="admin_orders_menu",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="admin_stats",
                )
            ]
        ]
    )

