from aiogram import Router, F
from aiogram.types import Message

from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.product_view import (
    product_view_keyboard
)
from models import Product
from repositories.category import CategoryRepository
from bot.keyboards.catalog import categories_keyboard
from repositories.product import ProductRepository
from repositories.cart import CartRepository
from repositories.user import UserRepository


cart_repository = CartRepository()
user_repository = UserRepository()
product_repository = ProductRepository()

router = Router()

repository = CategoryRepository()


@router.message(
    F.text == "📦 Каталог"
)
async def catalog_button(
        message: Message,
        session: AsyncSession,
):
    categories = await repository.get_all(
        session=session
    )

    await message.answer(
        "🏋️ Категории товаров",
        reply_markup=categories_keyboard(
            categories
        )
    )


@router.callback_query(
    lambda c: c.data.startswith("category:")
)
async def category_callback(
        callback: CallbackQuery,
        session: AsyncSession,
):
    category_id = int(
        callback.data.split(":")[1]
    )

    products = await product_repository.get_by_category(
        session=session,
        category_id=category_id,
    )

    if not products:
        await callback.answer(
            "Товаров нет"
        )
        return

    product = products[0]

    text = (
        f"📦 {product.name}\n\n"
        f"💰 Цена: {product.price} ₽\n"
        f"📦 Остаток: {product.stock} шт."
    )

    if product.description:
        text += (
            f"\n\n"
            f"{product.description}"
        )

    if product.image_id:
        await callback.message.answer_photo(
            photo=product.image_id,
            caption=text,
            reply_markup=product_view_keyboard(
                category_id=category_id,
                product_id=product.id,
                index=0,
                total=len(products),
            )
        )
    else:
        await callback.message.answer(
            text,
            reply_markup=product_view_keyboard(
                category_id=category_id,
                product_id=product.id,
                index=0,
                total=len(products),
            )
        )

    await callback.answer()

async def show_product(
        callback: CallbackQuery,
        session: AsyncSession,
        category_id: int,
        index: int,
):
    products = await product_repository.get_by_category(
        session=session,
        category_id=category_id,
    )

    product = products[index]

    text = (
        f"📦 {product.name}\n\n"
        f"💰 Цена: {product.price} ₽\n"
        f"📦 Остаток: {product.stock} шт."
    )

    if product.description:
        text += (
            f"\n\n"
            f"{product.description}"
        )

    if product.image_id:

        await callback.message.delete()

        await callback.message.answer_photo(
            photo=product.image_id,
            caption=text,
            reply_markup=product_view_keyboard(
                category_id=category_id,
                product_id=product.id,
                index=index,
                total=len(products),
            )
        )

    else:
        await callback.message.edit_text(
            text,
            reply_markup=product_view_keyboard(
                category_id=category_id,
                product_id=product.id,
                index=index,
                total=len(products),
            )
        )

@router.callback_query(
    F.data.startswith("product_next:")
)
async def product_next(
        callback: CallbackQuery,
        session: AsyncSession,
):
    _, category_id, index = (
        callback.data.split(":")
    )

    await show_product(
        callback,
        session,
        int(category_id),
        int(index) + 1,
    )

    await callback.answer()

@router.callback_query(
    F.data.startswith("product_prev:")
)
async def product_prev(
        callback: CallbackQuery,
        session: AsyncSession,
):
    _, category_id, index = (
        callback.data.split(":")
    )

    await show_product(
        callback,
        session,
        int(category_id),
        int(index) - 1,
    )

    await callback.answer()

@router.callback_query(
    F.data == "catalog_back"
)
async def catalog_back(
        callback: CallbackQuery,
        session: AsyncSession,
):
    categories = await repository.get_all(
        session=session
    )

    await callback.message.answer(
        "🏋️ Категории товаров",
        reply_markup=categories_keyboard(
            categories
        )
    )

    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("cart:"))
async def add_to_cart(
    callback: CallbackQuery,
    session: AsyncSession,
):
    product_id = int(
        callback.data.split(":")[1]
    )
    product = await session.get(
        Product,
        product_id,
    )

    if not product:
        await callback.answer(
            "Товар не найден",
            show_alert=True,
        )
        return

    if product.stock <= 0:
        await callback.answer(
            "Товар закончился",
            show_alert=True,
        )
        return

    user = await user_repository.get_by_telegram_id(
        session=session,
        telegram_id=callback.from_user.id,
    )

    if user is None:
        await callback.answer(
            "Сначала выполните /start",
            show_alert=True,
        )
        return

    await cart_repository.add_product(
        session=session,
        user_id=user.id,
        product_id=product_id,
    )

    await callback.answer(
        "Товар добавлен в корзину ✅"
    )