from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def categories_edit_keyboard(categories):
    buttons = []

    for category in categories:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=category.name,
                    callback_data=f"select_category:{category.id}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def categories_select_keyboard(categories):
    buttons = []

    for category in categories:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=category.name,
                    callback_data=f"select_category:{category.id}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)
