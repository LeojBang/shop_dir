from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.catalog import categories_keyboard
from bot.keyboards.product_card import product_card_keyboard
from bot.keyboards.product_list import products_list_keyboard
from models import Product
from repositories.cart import CartRepository
from repositories.category import CategoryRepository
from repositories.product import ProductRepository
from repositories.user import UserRepository

cart_repository = CartRepository()
user_repository = UserRepository()
product_repository = ProductRepository()

router = Router()

repository = CategoryRepository()


@router.message(F.text == "📦 Каталог")
async def catalog_button(
    message: Message,
    session: AsyncSession,
):
    categories = await repository.get_all(session=session)

    await message.answer(
        "🏋️ Категории товаров",
        reply_markup=categories_keyboard(categories),
    )


@router.callback_query(F.data.startswith("category:"))
async def category_callback(
    callback: CallbackQuery,
    session: AsyncSession,
):
    category_id = int(callback.data.split(":")[1])

    products = await product_repository.get_by_category(
        session=session,
        category_id=category_id,
    )

    if not products:
        await callback.answer("Товаров нет")
        return

    await callback.message.edit_text(
        "📦 Выберите товар",
        reply_markup=products_list_keyboard(products, category_id),
    )

    await callback.answer()


@router.callback_query(F.data == "catalog_back")
async def catalog_back(
    callback: CallbackQuery,
    session: AsyncSession,
):
    categories = await repository.get_all(session=session)

    await callback.message.answer(
        "🏋️ Категории товаров",
        reply_markup=categories_keyboard(categories),
    )

    await callback.answer()


@router.callback_query(F.data == "catalog_categories")
async def catalog_categories(
    callback: CallbackQuery,
    session: AsyncSession,
):
    categories = await repository.get_all(session=session)

    await callback.message.edit_text(
        "🏋️ Категории товаров",
        reply_markup=categories_keyboard(categories),
    )

    await callback.answer()


@router.callback_query(F.data.startswith("product:"))
async def product_view(
    callback: CallbackQuery,
    session: AsyncSession,
):
    product_id = int(callback.data.split(":")[1])

    product = await session.get(Product, product_id)

    text = (
        f"📦 {product.name}\n\n"
        f"{product.description or ''}\n\n"
        f"💰 Цена: {product.price} ₽\n"
        f"📦 Остаток: {product.stock}\n\n"
    )

    await callback.message.delete()

    await callback.message.answer(
        text,
        reply_markup=product_card_keyboard(
            product.id,
            product.category_id,
        ),
    )

    await callback.answer()


@router.callback_query(F.data.startswith("cart:"))
async def add_to_cart(
    callback: CallbackQuery,
    session: AsyncSession,
):
    product_id = int(callback.data.split(":")[1])
    product = await session.get(Product, product_id)

    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return

    if product.stock <= 0:
        await callback.answer("Товар закончился", show_alert=True)
        return

    user = await user_repository.get_by_telegram_id(
        session=session,
        telegram_id=callback.from_user.id,
    )

    if user is None:
        await callback.answer("Сначала выполните /start", show_alert=True)
        return

    await cart_repository.add_product(
        session=session,
        user_id=user.id,
        product_id=product_id,
    )

    await callback.answer("Товар добавлен в корзину ✅")
