from aiogram import Router

from bot.handlers.start import router as start_router
from bot.handlers.catalog import (
    router as catalog_router)
from bot.handlers.cart import (
    router as cart_router
)

main_router = Router()

main_router.include_router(start_router)
main_router.include_router(
    catalog_router
)
main_router.include_router(cart_router)