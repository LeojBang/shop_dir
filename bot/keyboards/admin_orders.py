from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def order_status_keyboard(
    order_id: int,
    status: str,
):
    buttons = []

    if status == "waiting_payment":
        buttons.append(
            [
                InlineKeyboardButton(
                    text="📦 В обработке",
                    callback_data=f"order_processing:{order_id}",
                )
            ]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text="💰 Оплата получена",
                    callback_data=f"confirm_payment:{order_id}",
                )
            ]
        )

        buttons.append(
            [
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data=f"order_cancel:{order_id}",
                )
            ]
        )
    elif status == "payment_check":
        buttons.append(
            [
                InlineKeyboardButton(
                    text="💰 Оплата получена",
                    callback_data=f"confirm_payment:{order_id}",
                )
            ]
        )

        buttons.append(
            [
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data=f"order_cancel:{order_id}",
                )
            ]
        )
    elif status == "processing":

        buttons.append(
            [
                InlineKeyboardButton(
                    text="📦 Добавить трек",
                    callback_data=f"tracking:{order_id}",
                )
            ]
        )

        buttons.append(
            [
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data=f"order_cancel:{order_id}",
                )
            ]
        )

    # Кнопка назад — возвращает в список заказов с тем же статусом
    buttons.append(
        [
            InlineKeyboardButton(
                text="◀️ Назад к списку",
                callback_data="admin_orders_all",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)
