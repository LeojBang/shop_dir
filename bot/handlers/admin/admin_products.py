from decimal import Decimal

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters.admin import AdminFilter
from bot.keyboards.admin_categories import categories_select_keyboard
from bot.keyboards.admin_products import products_list_keyboard
from bot.keyboards.cancel import cancel_keyboard
from bot.states.product import AddProductState
from repositories.category import CategoryRepository
from repositories.product import ProductRepository

router = Router()

# Фильтр на оба типа событий — иначе callback выбора категории не проходил
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())

product_repository = ProductRepository()
category_repository = CategoryRepository()


def progress_bar(step: int, total: int = 5) -> str:
    filled = "●" * step
    empty = "○" * (total - step)
    return f"{filled}{empty}  {step}/{total}"


# ── Список товаров ───────────────────────────────────────────────────────────


@router.callback_query(F.data == "products_list")
async def products_list(callback: CallbackQuery, session: AsyncSession):
    products = await product_repository.get_page(session=session, offset=0, limit=5)

    if not products:
        await callback.message.edit_text("Товаров пока нет")
        await callback.answer()
        return

    await callback.message.edit_text(
        "📦 Список товаров",
        reply_markup=products_list_keyboard(products, page=0),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("products_page:"))
async def products_page(callback: CallbackQuery, session: AsyncSession):
    page = int(callback.data.split(":")[1])

    products = await product_repository.get_page(
        session=session, offset=page * 5, limit=5
    )

    if not products:
        await callback.answer("Больше товаров нет")
        return

    await callback.message.edit_text(
        "📦 Список товаров",
        reply_markup=products_list_keyboard(products, page=page),
    )
    await callback.answer()


# ── Добавление товара — шаг 1: название ─────────────────────────────────────


@router.callback_query(F.data == "product_add")
async def product_add(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddProductState.waiting_name)

    await callback.message.answer(
        f"➕ <b>Новый товар</b>\n"
        f"{progress_bar(1)}\n\n"
        f"Введите <b>название</b> товара:",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


# ── Шаг 2: описание ──────────────────────────────────────────────────────────


@router.message(AddProductState.waiting_name)
async def add_product_name(message: Message, state: FSMContext):
    name = message.text.strip()

    if len(name) < 2:
        await message.answer("❌ Слишком короткое название. Попробуйте ещё раз:")
        return

    await state.update_data(name=name)
    await state.set_state(AddProductState.waiting_description)

    await message.answer(
        f"➕ <b>Новый товар</b>\n"
        f"{progress_bar(2)}\n\n"
        f"✅ Название: <b>{name}</b>\n\n"
        f"Введите <b>описание</b> товара\n"
        f"(или отправьте <code>-</code> чтобы пропустить):",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )


# ── Шаг 3: цена ──────────────────────────────────────────────────────────────


@router.message(AddProductState.waiting_description)
async def add_product_description(message: Message, state: FSMContext):
    description = None if message.text.strip() == "-" else message.text.strip()

    await state.update_data(description=description)
    await state.set_state(AddProductState.waiting_price)

    data = await state.get_data()

    await message.answer(
        f"➕ <b>Новый товар</b>\n"
        f"{progress_bar(3)}\n\n"
        f"✅ Название: <b>{data['name']}</b>\n"
        f"✅ Описание: {description or 'не указано'}\n\n"
        f"Введите <b>цену</b> в рублях (например: 2500):",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )


# ── Шаг 4: остаток ───────────────────────────────────────────────────────────


@router.message(AddProductState.waiting_price)
async def add_product_price(message: Message, state: FSMContext):
    try:
        price = Decimal(message.text.strip().replace(",", "."))
        if price <= 0:
            raise ValueError
    except Exception:
        await message.answer("❌ Введите корректную цену, например: 2500")
        return

    await state.update_data(price=price)
    await state.set_state(AddProductState.waiting_stock)

    data = await state.get_data()

    await message.answer(
        f"➕ <b>Новый товар</b>\n"
        f"{progress_bar(4)}\n\n"
        f"✅ Название: <b>{data['name']}</b>\n"
        f"✅ Описание: {data.get('description') or 'не указано'}\n"
        f"✅ Цена: <b>{price} ₽</b>\n\n"
        f"Введите <b>количество</b> на складе:",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )


# ── Шаг 5: категория ─────────────────────────────────────────────────────────


@router.message(AddProductState.waiting_stock)
async def add_product_stock(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    try:
        stock = int(message.text.strip())
        if stock < 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите целое число, например: 10")
        return

    await state.update_data(stock=stock)
    await state.set_state(AddProductState.waiting_category)

    data = await state.get_data()
    categories = await category_repository.get_all(session=session)

    await message.answer(
        f"➕ <b>Новый товар</b>\n"
        f"{progress_bar(5)}\n\n"
        f"✅ Название: <b>{data['name']}</b>\n"
        f"✅ Описание: {data.get('description') or 'не указано'}\n"
        f"✅ Цена: <b>{data['price']} ₽</b>\n"
        f"✅ Остаток: <b>{stock} шт.</b>\n\n"
        f"Выберите <b>категорию</b>:",
        parse_mode="HTML",
        reply_markup=categories_select_keyboard(categories),
    )


# ── Финал: сохранение ────────────────────────────────────────────────────────


@router.callback_query(
    AddProductState.waiting_category,
    F.data.startswith("select_category:"),
)
async def add_product_category(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    category_id = int(callback.data.split(":")[1])
    data = await state.get_data()

    product = await product_repository.create(
        session=session,
        name=data["name"],
        description=data.get("description"),
        price=data["price"],
        stock=data["stock"],
        category_id=category_id,
    )

    category = await category_repository.get_all(session=session)
    cat_name = next((c.name for c in category if c.id == category_id), "—")

    await callback.message.edit_text(
        f"✅ <b>Товар успешно создан!</b>\n\n"
        f"📦 <b>{product.name}</b>\n"
        f"📁 Категория: {cat_name}\n"
        f"💰 Цена: {product.price} ₽\n"
        f"🗃 Остаток: {product.stock} шт.\n"
        f"🆔 ID: {product.id}",
        parse_mode="HTML",
    )

    await state.clear()
    await callback.answer("✅ Товар создан")
