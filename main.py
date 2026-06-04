import asyncio

from aiogram import Bot, Dispatcher

from bot import main_router
from bot.middlewares.database import DatabaseMiddleware
from core.config import settings
from bot.handlers.admin.admin_menu import router as admin_menu_router
from bot.handlers.admin.admin_orders import router as admin_orders_router
from bot.handlers.admin.admin_product_edit import router as admin_product_edit_router
from bot.handlers.admin.admin_products import router as admin_products_router
from bot.handlers.admin.admin_stats import router as admin_stats_router
from bot.handlers.profile import router as profile_router
from bot.handlers.support import router as support_router
from bot.handlers.admin.admin_payments import (
    router as admin_payments_router
)
from bot.handlers.admin.admin_common import (
    router as admin_common_router
)





from bot.handlers import orders


async def main():
    bot = Bot(token=settings.BOT_TOKEN)

    dp = Dispatcher()

    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.include_router(orders.router)
    dp.include_router(profile_router)
    dp.include_router(support_router)


    dp.include_router(admin_menu_router)
    dp.include_router(admin_orders_router)
    dp.include_router(admin_product_edit_router)
    dp.include_router(admin_products_router)
    dp.include_router(admin_stats_router)
    dp.include_router(admin_common_router)
    dp.include_router(admin_payments_router)

    dp.include_router(main_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())