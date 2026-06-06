from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def admin_orders_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏳ Проверка оплаты",
                    callback_data="orders_status:payment_check",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📦 В обработке",
                    callback_data="orders_status:processing",
                )
            ],
            [
                InlineKeyboardButton(
                    text="✔️ Выполнены",
                    callback_data="orders_status:completed",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📜 Архив заказов",
                    callback_data="admin_orders_all",
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
