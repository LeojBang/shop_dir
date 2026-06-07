from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.main_menu import main_menu_keyboard
from core.config import settings
from services.user import UserService

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

    is_admin = message.from_user.id in settings.ADMIN_IDS

    await message.answer(
        "🧬 <b>Добро пожаловать в ShopPeptid!</b>\n\n"
        "Современные пептиды и продукция для поддержки здоровья.\n\n"
        "📦 <b>Ассортимент:</b>\n"
        "• Мужское и женское здоровье\n"
        "• Контроль веса\n"
        "• Восстановление организма\n"
        "• Поддержка печени и обмена веществ\n\n"
        "✅ Актуальные остатки на складе\n"
        "🚚 Бесплатная доставка через OZON\n"
        "💳 Безопасная оплата\n"
        "⚡️ Быстрая обработка заказов\n"
        "💬 Поддержка клиентов\n\n"
        "⚠️ Минимальная сумма заказа — <b>7 000 ₽</b>\n\n"
        "Выбирайте товары в каталоге и оформляйте заказ прямо здесь 👇",
        reply_markup=main_menu_keyboard(is_admin=is_admin),
        parse_mode="HTML",
    )
