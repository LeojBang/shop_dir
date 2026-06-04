from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def order_detail_keyboard(
        order,
):
    keyboard = []

    if order.status == "payment_check":
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить оплату",
                    callback_data=(
                        f"confirm_payment:{order.id}"
                    )
                )
            ]
        )

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="❌ Отклонить оплату",
                    callback_data=(
                        f"reject_payment:{order.id}"
                    )
                )
            ]
        )

    elif order.status == "processing":

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="🚚 Отправить",
                    callback_data=(
                        f"tracking:{order.id}"
                    )
                )
            ]
        )

    elif order.status == "shipped":

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="✅ Завершить",
                    callback_data=(
                        f"order_complete:{order.id}"
                    )
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="⬅️ К списку",
                callback_data=(
                    f"back_to_status:{order.status}"
                )
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )