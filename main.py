import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from core.config import settings
from core.database_init import create_tables
from core.logger import setup_logger
from bot import main_router
from bot.middlewares.database import DatabaseMiddleware
from bot.middlewares.error import ErrorMiddleware
from bot.handlers.admin.admin_menu import router as admin_menu_router
from bot.handlers.admin.admin_orders import router as admin_orders_router
from bot.handlers.admin.admin_product_edit import router as admin_product_edit_router
from bot.handlers.admin.admin_products import router as admin_products_router
from bot.handlers.admin.admin_stats import router as admin_stats_router
from bot.handlers.admin.admin_payments import router as admin_payments_router
from bot.handlers.admin.admin_common import router as admin_common_router
from bot.handlers.admin.admin_payment_settings import (
    router as admin_payment_settings_router,
)

# Настраиваем логирование до всего остального
setup_logger()
logger = logging.getLogger(__name__)


async def notify_admins_on_start(bot: Bot) -> None:
    """Уведомляет администраторов о запуске бота."""
    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text="✅ <b>Бот запущен</b> и готов к работе.",
                parse_mode="HTML",
            )
        except Exception as e:
            logger.warning("Не удалось уведомить админа %s: %s", admin_id, e)


async def notify_admins_on_stop(bot: Bot) -> None:
    """Уведомляет администраторов об остановке бота."""
    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text="🔴 <b>Бот остановлен.</b>",
                parse_mode="HTML",
            )
        except Exception as e:
            logger.warning("Не удалось уведомить админа %s: %s", admin_id, e)


async def main():
    logger.info("Запуск бота...")

    bot = Bot(token=settings.BOT_TOKEN)
    await create_tables()

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Глобальный обработчик ошибок — первым
    dp.update.outer_middleware(ErrorMiddleware())

    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())

    # Админские роутеры
    dp.include_router(admin_menu_router)
    dp.include_router(admin_orders_router)
    dp.include_router(admin_product_edit_router)
    dp.include_router(admin_products_router)
    dp.include_router(admin_stats_router)
    dp.include_router(admin_common_router)
    dp.include_router(admin_payments_router)
    dp.include_router(admin_payment_settings_router)

    # Пользовательские хендлеры
    dp.include_router(main_router)

    # Уведомляем админов о старте
    await notify_admins_on_start(bot)
    logger.info("Бот запущен успешно")

    try:
        await dp.start_polling(bot)
    finally:
        # Уведомляем о штатной остановке
        await notify_admins_on_stop(bot)
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())