from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.profile import profile_keyboard
from bot.states.profile import EditProfileState
from repositories.user import UserRepository

router = Router()

user_repository = UserRepository()

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

    await user_repository.update_fields(
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

    await user_repository.update_fields(
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

    await user_repository.update_fields(
        session=session,
        user_id=user.id,
        address=message.text,
    )

    await message.answer(
        "✅ Адрес сохранён"
    )

    await state.clear()
