from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def orders_list_keyboard(
        orders,
):
    keyboard = []

    for order in orders:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=(
                        f"Заказ #{order.id}"
                    ),
                    callback_data=(
                        f"show_order:{order.id}"
                    )
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="admin_orders_menu",
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )