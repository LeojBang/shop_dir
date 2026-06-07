from aiogram import Router

from bot.handlers.cancel import router as cancel_router
from bot.handlers.cart import router as cart_router
from bot.handlers.catalog import router as catalog_router
from bot.handlers.orders import router as orders_router
from bot.handlers.profile import router as profile_router
from bot.handlers.start import router as start_router
from bot.handlers.support import router as support_router

# добавь первым — до всех остальных
main_router = Router()

main_router.include_router(start_router)
main_router.include_router(catalog_router)
main_router.include_router(cart_router)
main_router.include_router(orders_router)
main_router.include_router(profile_router)
main_router.include_router(support_router)
main_router.include_router(cancel_router)
