from decimal import Decimal

from aiogram.fsm.context import FSMContext

from bot.keyboards.admin_categories import categories_select_keyboard
from bot.keyboards.admin_products import edit_product_keyboard, confirm_delete_keyboard
from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram import F
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states.product import EditPriceState, EditStockState, EditNameState, EditDescriptionState, AddPhotoState
from repositories.category import CategoryRepository
from repositories.product import ProductRepository

router = Router()

product_repository = ProductRepository()
category_repository = CategoryRepository()


@router.callback_query(
    F.data.startswith("edit_product:")
)
async def edit_product(
        callback: CallbackQuery,
        session: AsyncSession,
):
    product_id = int(
        callback.data.split(":")[1]
    )

    product = await product_repository.get_by_id(
        session=session,
        product_id=product_id,
    )

    if not product:
        await callback.answer(
            "Товар не найден",
            show_alert=True,
        )
        return

    text = (
        f"📦 {product.name}\n\n"
        f"💰 Цена: {product.price} ₽\n"
        f"📦 Остаток: {product.stock}\n"
        f"🆔 ID: {product.id}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=edit_product_keyboard(
            product.id
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("price:")
)
async def price_edit(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
):
    product_id = int(
        callback.data.split(":")[1]
    )

    product = await product_repository.get_by_id(
        session=session,
        product_id=product_id,
    )

    if not product:
        await callback.answer(
            "Товар не найден",
            show_alert=True,
        )
        return

    await state.update_data(
        product_id=product_id
    )

    await state.set_state(
        EditPriceState.waiting_price
    )

    await callback.message.answer(
        f"Введите новую цену для товара:\n\n"
        f"{product.name}\n"
        f"Текущая цена: {product.price} ₽"
    )

    await callback.answer()


@router.message(
    EditPriceState.waiting_price
)
async def save_price(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
):
    try:
        price = Decimal(
            message.text.replace(",", ".")
        )
    except Exception:
        await message.answer(
            "Введите корректную цену"
        )
        return

    data = await state.get_data()

    product_id = data["product_id"]

    product = await product_repository.update_price(
        session=session,
        product_id=product_id,
        price=price,
    )

    await message.answer(
        f"✅ Цена обновлена\n\n"
        f"{product.name}\n"
        f"Новая цена: {product.price} ₽"
    )

    await state.clear()


@router.callback_query(
    F.data.startswith("stock:")
)
async def stock_edit(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
):
    product_id = int(
        callback.data.split(":")[1]
    )

    product = await product_repository.get_by_id(
        session=session,
        product_id=product_id,
    )

    if not product:
        await callback.answer(
            "Товар не найден",
            show_alert=True,
        )
        return

    await state.update_data(
        product_id=product_id
    )

    await state.set_state(
        EditStockState.waiting_stock
    )

    await callback.message.answer(
        f"Введите новый остаток для товара:\n\n"
        f"{product.name}\n"
        f"Текущий остаток: {product.stock}"
    )

    await callback.answer()


@router.message(
    EditStockState.waiting_stock
)
async def save_stock(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
):
    if not message.text.isdigit():
        await message.answer(
            "Введите число"
        )
        return

    stock = int(message.text)

    data = await state.get_data()

    product_id = data["product_id"]

    product = await product_repository.update_stock(
        session=session,
        product_id=product_id,
        stock=stock,
    )

    await message.answer(
        f"✅ Остаток обновлен\n\n"
        f"{product.name}\n"
        f"Новый остаток: {product.stock}"
    )

    await state.clear()


@router.callback_query(
    F.data.startswith("name:")
)
async def name_edit(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
):
    product_id = int(
        callback.data.split(":")[1]
    )

    product = await product_repository.get_by_id(
        session=session,
        product_id=product_id,
    )

    await state.update_data(
        product_id=product_id
    )

    await state.set_state(
        EditNameState.waiting_name
    )

    await callback.message.answer(
        f"Введите новое название\n\n"
        f"Текущее:\n{product.name}"
    )

    await callback.answer()


@router.message(
    EditNameState.waiting_name
)
async def save_name(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
):
    data = await state.get_data()

    product = await product_repository.update_name(
        session=session,
        product_id=data["product_id"],
        name=message.text,
    )

    await message.answer(
        f"✅ Название обновлено\n\n"
        f"{product.name}"
    )

    await state.clear()


@router.callback_query(
    F.data.startswith("description:")
)
async def description_edit(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
):
    product_id = int(
        callback.data.split(":")[1]
    )

    product = await product_repository.get_by_id(
        session=session,
        product_id=product_id,
    )

    await state.update_data(
        product_id=product_id
    )

    await state.set_state(
        EditDescriptionState.waiting_description
    )

    await callback.message.answer(
        f"Введите новое описание\n\n"
        f"Текущее:\n{product.description}"
    )

    await callback.answer()


@router.message(
    EditDescriptionState.waiting_description
)
async def save_description(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
):
    data = await state.get_data()

    product = await product_repository.update_description(
        session=session,
        product_id=data["product_id"],
        description=message.text,
    )

    await message.answer(
        "✅ Описание обновлено"
    )

    await state.clear()


@router.callback_query(
    F.data.startswith("photo:")
)
async def photo_edit(
        callback: CallbackQuery,
        state: FSMContext,
):
    product_id = int(
        callback.data.split(":")[1]
    )

    await state.update_data(
        product_id=product_id
    )

    await state.set_state(
        AddPhotoState.waiting_photo
    )

    await callback.message.answer(
        "Отправьте новое фото товара"
    )

    await callback.answer()


@router.message(
    AddPhotoState.waiting_photo,
    F.photo
)
async def save_product_photo(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
):
    data = await state.get_data()

    product_id = data["product_id"]

    image_id = message.photo[-1].file_id

    product = await product_repository.update_image(
        session=session,
        product_id=product_id,
        image_id=image_id,
    )

    if not product:
        await message.answer(
            "Товар не найден"
        )
        await state.clear()
        return

    await message.answer(
        f"✅ Фото сохранено для товара {product.name}"
    )

    await state.clear()


@router.callback_query(
    F.data.startswith("change_category:")
)
async def change_category(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
):
    product_id = int(
        callback.data.split(":")[1]
    )

    await state.update_data(
        product_id=product_id
    )

    categories = await category_repository.get_all(
        session=session
    )

    await callback.message.answer(
        "Выберите категорию:",
        reply_markup=categories_select_keyboard(
            categories
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("set_category:")
)
async def save_category(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
):
    category_id = int(
        callback.data.split(":")[1]
    )

    data = await state.get_data()

    product_id = data["product_id"]

    product = await product_repository.update_category(
        session=session,
        product_id=product_id,
        category_id=category_id,
    )

    await callback.message.edit_text(
        f"✅ Категория обновлена\n\n"
        f"{product.name}"
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("delete_product:")
)
async def delete_product(
        callback: CallbackQuery,
):
    product_id = int(
        callback.data.split(":")[1]
    )

    await callback.message.edit_text(
        "⚠️ Вы уверены, что хотите удалить товар?",
        reply_markup=confirm_delete_keyboard(
            product_id
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("confirm_delete:")
)
async def confirm_delete_product(
        callback: CallbackQuery,
        session: AsyncSession,
):
    product_id = int(
        callback.data.split(":")[1]
    )

    success = await product_repository.delete(
        session=session,
        product_id=product_id,
    )

    if not success:
        await callback.answer(
            "Товар не найден",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        "✅ Товар удалён"
    )

    await callback.answer()



