from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram import F
from aiogram.types import Message

from bot.keyboards.admin_menu import admin_menu_keyboard
from bot.keyboards.admin_products import admin_products_keyboard

router = Router()


@router.message(F.text == "⚙️ Админка")
async def admin_button(message: Message):
    await message.answer(
        "⚙️ Админ-панель",
        reply_markup=admin_menu_keyboard(),
    )


@router.callback_query(F.data == "admin_back")
async def admin_back(
    callback: CallbackQuery,
):
    await callback.message.edit_text(
        "⚙️ Админ-панель",
        reply_markup=admin_menu_keyboard(),
    )

    await callback.answer()


@router.callback_query(F.data == "admin_products")
async def admin_products(
    callback: CallbackQuery,
):
    await callback.message.edit_text(
        "📦 Управление товарами",
        reply_markup=admin_products_keyboard(),
    )

    await callback.answer()
