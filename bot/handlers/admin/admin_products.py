from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram import F
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.admin_categories import categories_select_keyboard
from bot.keyboards.admin_products import products_page_keyboard, product_manage_keyboard, products_list_keyboard
from bot.states.product import AddProductState
from repositories.category import CategoryRepository
from repositories.product import ProductRepository
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router()

product_repository = ProductRepository()
category_repository = CategoryRepository()


@router.callback_query(
    F.data == "products_list"
)
async def products_list(
        callback: CallbackQuery,
        session: AsyncSession,
):
    products = await product_repository.get_page(
        session=session,
        offset=0,
        limit=5,
    )

    if not products:
        await callback.message.edit_text(
            "Товаров нет"
        )
        return

    await callback.message.edit_text(
        "📦 Список товаров",
        reply_markup=products_list_keyboard(
            products,
            page=0,
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("products_page:")
)
async def products_page(
        callback: CallbackQuery,
        session: AsyncSession,
):
    page = int(
        callback.data.split(":")[1]
    )

    products = await product_repository.get_page(
        session=session,
        offset=page * 5,
        limit=5,
    )

    if not products:
        await callback.answer(
            "Больше товаров нет"
        )
        return

    await callback.message.edit_text(
        "📦 Список товаров",
        reply_markup=products_list_keyboard(
            products,
            page=page,
        )
    )

    await callback.answer()


@router.callback_query(
    F.data == "product_add"
)
async def product_add(
        callback: CallbackQuery,
        state: FSMContext,
):
    await state.set_state(
        AddProductState.waiting_name
    )

    await callback.message.answer(
        "Введите название товара:"
    )

    await callback.answer()


@router.message(
    AddProductState.waiting_name
)
async def add_product_name(
        message: Message,
        state: FSMContext,
):
    await state.update_data(
        name=message.text
    )

    await state.set_state(
        AddProductState.waiting_description
    )

    await message.answer(
        "Введите описание товара:"
    )


@router.message(
    AddProductState.waiting_description
)
async def add_product_description(
        message: Message,
        state: FSMContext,
):
    await state.update_data(
        description=message.text
    )

    await state.set_state(
        AddProductState.waiting_price
    )

    await message.answer(
        "Введите цену:"
    )


@router.message(
    AddProductState.waiting_price
)
async def add_product_price(
        message: Message,
        state: FSMContext,
):
    try:
        price = float(message.text)
    except ValueError:
        await message.answer(
            "Введите число"
        )
        return

    await state.update_data(
        price=price
    )

    await state.set_state(
        AddProductState.waiting_stock
    )

    await message.answer(
        "Введите остаток:"
    )


@router.message(
    AddProductState.waiting_stock
)
async def add_product_stock(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
):
    try:
        stock = int(message.text)
    except ValueError:
        await message.answer(
            "Введите целое число"
        )
        return

    await state.update_data(
        stock=stock
    )

    categories = await category_repository.get_all(
        session=session
    )

    await state.set_state(
        AddProductState.waiting_category
    )

    await message.answer(
        "Выберите категорию:",
        reply_markup=categories_select_keyboard(categories)
    )


@router.callback_query(
    AddProductState.waiting_category,
    F.data.startswith("select_category:")
)
async def add_product_category(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
):
    category_id = int(
        callback.data.split(":")[1]
    )

    data = await state.get_data()

    product = await product_repository.create(
        session=session,
        name=data["name"],
        description=data["description"],
        price=data["price"],
        stock=data["stock"],
        category_id=category_id,
    )

    await callback.message.answer(
        f"✅ Товар создан\n\n"
        f"ID: {product.id}\n"
        f"Название: {product.name}"
    )

    await state.clear()

    await callback.answer()
