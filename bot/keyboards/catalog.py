from aiogram.utils.keyboard import InlineKeyboardBuilder


def categories_keyboard(categories):

    builder = InlineKeyboardBuilder()

    for category in categories:
        builder.button(
            text=category.name,
            callback_data=f"category:{category.id}"
        )

    builder.adjust(1)

    return builder.as_markup()