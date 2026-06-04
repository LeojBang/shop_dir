import asyncio

from aiogram import Bot, Dispatcher

from bot import main_router
from bot.middlewares.database import DatabaseMiddleware
from core.config import settings
from bot.handlers.admin_orders import router as admin_orders_router

from bot.handlers.admin import router as admin_router

from bot.handlers import orders


async def main():
    bot = Bot(token=settings.BOT_TOKEN)

    dp = Dispatcher()

    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.include_router(orders.router)
    dp.include_router(admin_orders_router)
    dp.include_router(admin_router)
    dp.include_router(main_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())