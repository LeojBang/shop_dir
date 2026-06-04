from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.main_menu import (
    main_menu_keyboard
)

from sqlalchemy.ext.asyncio import AsyncSession

from services.user import UserService
from config import ADMIN_IDS

router = Router()

user_service = UserService()


@router.message(CommandStart())
async def start_handler(
    message: Message,
    session: AsyncSession,
):
    await user_service.register_user(
        session=session,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
    )

    is_admin = message.from_user.id in ADMIN_IDS

    await message.answer(
        "🧬 Добро пожаловать!\n\n"
        "Магазин современных пептидов и продукции для поддержки здоровья.\n\n"
        "В ассортименте представлены решения для:\n"
        "• мужского здоровья\n"
        "• женского здоровья\n"
        "• контроля веса\n"
        "• восстановления организма\n"
        "• поддержки печени и обмена веществ\n\n"
        "✔️ Актуальные остатки\n"
        "✔️ Безопасная оплата\n"
        "✔️ Быстрая обработка заказов\n"
        "✔️ Поддержка клиентов\n\n"
        "Выберите интересующие товары в каталоге и оформите заказ прямо в Telegram.\n\n"
        "💪 Спасибо за доверие!",
        reply_markup=main_menu_keyboard(
            is_admin=is_admin
        ),
    )