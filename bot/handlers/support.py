from aiogram import F, Router
from aiogram.types import Message

router = Router()


@router.message(F.text == "☎️ Поддержка")
async def support(
    message: Message,
):
    await message.answer(
        "Для связи с менеджером:\n"
        "https://t.me/@l_i_l_u_888\n"
        "https://t.me/@Dgekson654"
    )
