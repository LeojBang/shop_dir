from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == "ignore")
async def ignore_callback(
    callback: CallbackQuery,
):
    await callback.answer()
