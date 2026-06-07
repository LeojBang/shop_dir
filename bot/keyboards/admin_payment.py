from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def payment_confirm_keyboard(
    order_id: int,
):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить оплату",
                    callback_data=f"confirm_payment:{order_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"reject_payment:{order_id}",
                )
            ],
        ]
    )
