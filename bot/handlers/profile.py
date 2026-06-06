import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.cancel import cancel_keyboard
from bot.keyboards.profile import profile_keyboard
from bot.states.profile import EditProfileState
from repositories.user import UserRepository

router = Router()

user_repository = UserRepository()

# Принимает форматы: +79991234567, 89991234567, +7 999 123-45-67 и т.п.
PHONE_REGEX = re.compile(
    r"^(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$"
)


def normalize_phone(phone: str) -> str:
    """Приводит любой формат к единому: +79991234567"""
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("8"):
        digits = "7" + digits[1:]
    return "+" + digits


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
        f"📍 Пункт выдачи OZON: {user.address or 'не указан'}"
    )

    await message.answer(
        text,
        reply_markup=profile_keyboard(),
    )


@router.callback_query(F.data == "edit_name")
async def edit_name(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.set_state(EditProfileState.waiting_name)
    await callback.message.answer("Введите ваше имя:", reply_markup=cancel_keyboard())
    await callback.answer()


@router.message(EditProfileState.waiting_name)
async def save_name(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    name = message.text.strip()

    if len(name) < 2:
        await message.answer("❌ Имя слишком короткое. Попробуйте ещё раз:")
        return

    user = await user_repository.get_by_telegram_id(
        session=session,
        telegram_id=message.from_user.id,
    )

    await user_repository.update_fields(
        session=session,
        user_id=user.id,
        first_name=name,
    )

    await message.answer("✅ Имя сохранено")
    await state.clear()


@router.callback_query(F.data == "edit_phone")
async def edit_phone(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.set_state(EditProfileState.waiting_phone)
    await callback.message.answer(
        "📱 Введите номер телефона:\n\n"
        "Допустимые форматы:\n"
        "+79991234567\n"
        "89991234567\n"
        "+7 999 123-45-67",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(EditProfileState.waiting_phone)
async def save_phone(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    raw = message.text.strip()

    if not PHONE_REGEX.match(raw):
        await message.answer(
            "❌ Неверный формат номера.\n\n"
            "Введите российский номер, например:\n"
            "+79991234567 или 89991234567"
        )
        return  # состояние не сбрасываем — ждём правильный ввод

    phone = normalize_phone(raw)

    user = await user_repository.get_by_telegram_id(
        session=session,
        telegram_id=message.from_user.id,
    )

    await user_repository.update_fields(
        session=session,
        user_id=user.id,
        phone=phone,
    )

    await message.answer(f"✅ Телефон сохранён: {phone}")
    await state.clear()


@router.callback_query(F.data == "edit_address")
async def edit_address(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.set_state(EditProfileState.waiting_address)
    await callback.message.answer(
        "📍 Введите адрес ближайшего пункта выдачи OZON:\n\n"
        "Найти пункт выдачи: ozon.ru/my/servicepoints\n\n"
        "Пример:\n"
        "г. Москва, ул. Ленина 15, ПВЗ Ozon",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(EditProfileState.waiting_address)
async def save_address(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    address = message.text.strip()

    if len(address) < 10:
        await message.answer(
            "❌ Адрес слишком короткий.\n" "Укажите город, улицу и номер дома:"
        )
        return

    user = await user_repository.get_by_telegram_id(
        session=session,
        telegram_id=message.from_user.id,
    )

    await user_repository.update_fields(
        session=session,
        user_id=user.id,
        address=address,
    )

    await message.answer("✅ Адрес сохранён")
    await state.clear()
