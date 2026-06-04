from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram import F

from bot.keyboards.admin_categories import categories_select_keyboard
from bot.keyboards.admin_products import (
    edit_product_keyboard, confirm_delete_keyboard, products_page_keyboard, product_manage_keyboard
)
from decimal import Decimal

from bot.keyboards.profile import profile_keyboard
from bot.states.product import (
    AddPhotoState,
    EditStockState, EditPriceState, AddProductState, EditNameState, EditDescriptionState
)
from bot.keyboards.admin_menu import admin_menu_keyboard
from bot.keyboards.admin_products import admin_products_keyboard
from bot.states.profile import EditProfileState
from models import User
from repositories.order import OrderRepository
from repositories.user import UserRepository
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from bot.utils.order_status import ORDER_STATUSES
from bot.keyboards.admin_orders import order_status_keyboard
from bot.filters.admin import AdminFilter
from aiogram.fsm.context import FSMContext
from repositories.product import ProductRepository
from repositories.category import CategoryRepository

router = Router()

order_repository = OrderRepository()
user_repository = UserRepository()
product_repository = ProductRepository()
category_repository = CategoryRepository()
router.message.filter(AdminFilter())


@router.callback_query(
    F.data == "admin_orders"
)
async def admin_orders_button(
        callback: CallbackQuery,
        session: AsyncSession,
):
    orders = await order_repository.get_new_orders(
        session=session,
    )

    if not orders:
        await callback.message.answer(
            "Новых заказов нет"
        )

        await callback.answer()
        return

    for order in orders:
        text = (
            f"📦 Заказ #{order.id}\n"
            f"Статус: {ORDER_STATUSES.get(order.status, order.status)}\n"
            f"Сумма: {order.total_price} ₽\n\n"
            f"Товары:\n"
        )

        for item in order.items:
            text += (
                f"• {item.product.name} "
                f"x {item.quantity}\n"
            )

        await callback.message.answer(
            text,
            reply_markup=order_status_keyboard(
                order.id
            )
        )

    await callback.answer()


@router.callback_query(
    F.data == "admin_stats"
)
async def admin_stats(
        callback: CallbackQuery,
        session: AsyncSession,
):
    orders = await order_repository.get_all_orders(
        session=session
    )

    total_orders = len(orders)

    total_revenue = sum(
        float(order.total_price)
        for order in orders
    )

    await callback.message.answer(
        f"📊 Статистика\n\n"
        f"Заказов всего: {total_orders}\n"
        f"Выручка: {total_revenue:.2f} ₽"
    )

    await callback.answer()




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
        reply_markup=categories_select_keyboard(
            categories
        )
    )

    await state.set_state(
        AddProductState.waiting_category
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
    F.data == "ignore"
)
async def ignore_callback(
        callback: CallbackQuery,
):
    await callback.answer()


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
        await callback.message.answer(
            "Товаров нет"
        )
        return

    for product in products:
        text = (
            f"📦 {product.name}\n\n"
            f"💰 Цена: {product.price} ₽\n"
            f"📦 Остаток: {product.stock}\n"
            f"🆔 ID: {product.id}"
        )

        await callback.message.answer(
            text,
            reply_markup=product_manage_keyboard(
                product.id
            )
        )

    await callback.message.answer(
        "Страница 1",
        reply_markup=products_page_keyboard(
            page=0
        )
    )

    await callback.answer()



@router.callback_query(lambda c: c.data.startswith("order_done:"))
async def order_done(
        callback: CallbackQuery,
        session,
):
    order_id = int(
        callback.data.split(":")[1]
    )
    order = await order_repository.get_order(
        session=session,
        order_id=order_id,
    )
    user = await session.get(
        User,
        order.user_id,
    )

    await order_repository.update_status(
        session=session,
        order_id=order_id,
        status="completed",
    )
    await callback.bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f"✅ Ваш заказ №{order.id} подтвержден!\n\n"
            f"Скоро мы свяжемся с вами."
        )
    )
    await callback.message.edit_text(
        f"📦 Заказ #{order_id}\n"
        f"Статус: ✅ Выполнен"
    )

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("order_cancel:"))
async def order_cancel(
        callback: CallbackQuery,
        session,
):
    order_id = int(
        callback.data.split(":")[1]
    )
    order = await order_repository.get_order(
        session=session,
        order_id=order_id,
    )

    user = await session.get(
        User,
        order.user_id,
    )

    await order_repository.update_status(
        session=session,
        order_id=order_id,
        status="cancelled",
    )

    await callback.bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f"❌ Ваш заказ №{order.id} отменен.\n\n"
            f"Свяжитесь с администратором для уточнения."
        )
    )

    await callback.message.edit_text(
        f"📦 Заказ #{order_id}\n"
        f"Статус: ❌ Отменен"
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

    text = "📦 Список товаров\n\n"

    for product in products:
        text += (
            f"ID: {product.id}\n"
            f"{product.name}\n"
            f"Цена: {product.price} ₽\n"
            f"Остаток: {product.stock}\n\n"
        )

    await callback.message.edit_text(
        text,
        reply_markup=products_page_keyboard(
            page=page
        )
    )

    await callback.answer()

@router.message(F.text == "👤 Профиль")
async def profile(
    message: Message,
    session: AsyncSession,
):
    user = await user_repository.get_by_telegram_id(
        session=session,
        telegram_id=message.from_user.id,
    )

    text = (
        f"👤 Имя: {user.first_name or 'не указано'}\n"
        f"📱 Телефон: {user.phone or 'не указан'}\n"
        f"🏠 Адрес: {user.address or 'не указан'}"
    )

    await message.answer(
        text,
        reply_markup=profile_keyboard(),
    )

@router.message(F.text == "☎️ Поддержка")
async def support(
    message: Message,
):
    await message.answer(
        "Для связи с менеджером нажмите:\n"
        "https://t.me/your_manager"
    )


@router.callback_query(F.data == "edit_name")
async def edit_name(
        callback: CallbackQuery,
        state: FSMContext,
):
    await state.set_state(
        EditProfileState.waiting_name
    )

    await callback.message.answer(
        "Введите ваше имя:"
    )

    await callback.answer()

@router.message(
    EditProfileState.waiting_name
)
async def save_name(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
):
    user = await user_repository.get_by_telegram_id(
        session=session,
        telegram_id=message.from_user.id,
    )

    await user_repository.update_name(
        session=session,
        user_id=user.id,
        first_name=message.text,
    )

    await message.answer(
        "✅ Имя сохранено"
    )

    await state.clear()

@router.callback_query(F.data == "edit_phone")
async def edit_phone(
        callback: CallbackQuery,
        state: FSMContext,
):
    await state.set_state(
        EditProfileState.waiting_phone
    )

    await callback.message.answer(
        "Введите телефон:"
    )

    await callback.answer()

@router.message(
    EditProfileState.waiting_phone
)
async def save_phone(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
):
    user = await user_repository.get_by_telegram_id(
        session=session,
        telegram_id=message.from_user.id,
    )

    await user_repository.update_phone(
        session=session,
        user_id=user.id,
        phone=message.text,
    )

    await message.answer(
        "✅ Телефон сохранён"
    )

    await state.clear()

@router.callback_query(F.data == "edit_address")
async def edit_address(
        callback: CallbackQuery,
        state: FSMContext,
):
    await state.set_state(
        EditProfileState.waiting_address
    )

    await callback.message.answer(
        "Введите адрес доставки:"
    )

    await callback.answer()


@router.message(
    EditProfileState.waiting_address
)
async def save_address(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
):
    user = await user_repository.get_by_telegram_id(
        session=session,
        telegram_id=message.from_user.id,
    )

    await user_repository.update_address(
        session=session,
        user_id=user.id,
        address=message.text,
    )

    await message.answer(
        "✅ Адрес сохранён"
    )

    await state.clear()

@router.callback_query(
    F.data.startswith("confirm_payment:")
)
async def confirm_payment(
        callback: CallbackQuery,
        session: AsyncSession,
):
    order_id = int(
        callback.data.split(":")[1]
    )

    order = await order_repository.get_order(
        session=session,
        order_id=order_id,
    )

    await order_repository.update_status(
        session=session,
        order_id=order_id,
        status="paid",
    )
    user = await session.get(
        User,
        order.user_id,
    )
    await callback.bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f"✅ Оплата заказа №{order.id} подтверждена.\n\n"
            f"Заказ передан в обработку."
        )
    )
    await callback.message.edit_text(
        f"💰 Заказ №{order.id}\n"
        f"Оплата подтверждена"
    )
    await callback.answer()

@router.callback_query(
    F.data.startswith("reject_payment:")
)
async def reject_payment(
        callback: CallbackQuery,
        session: AsyncSession,
):
    order_id = int(
        callback.data.split(":")[1]
    )

    order = await order_repository.get_order(
        session=session,
        order_id=order_id,
    )

    user = await session.get(
        User,
        order.user_id,
    )

    await callback.bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f"❌ Оплата заказа №{order.id} не найдена.\n\n"
            f"Если вы уже оплатили заказ, "
            f"свяжитесь с поддержкой."
        )
    )

    await callback.message.edit_text(
        f"❌ Заказ №{order.id}\n"
        f"Оплата отклонена"
    )

    await callback.answer()