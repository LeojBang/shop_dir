from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton


def main_menu_keyboard(is_admin=False):
    keyboard = [
        [
            KeyboardButton(text="📦 Каталог"),
            KeyboardButton(text="🛒 Корзина"),
        ],
        [
            KeyboardButton(text="📋 Мои заказы"),
            KeyboardButton(text="👤 Профиль"),
        ],
        [
            KeyboardButton(text="☎️ Поддержка"),
        ],
    ]

    if is_admin:
        keyboard.append([KeyboardButton(text="⚙️ Админка")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )
