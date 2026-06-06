import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters.admin import AdminFilter
from bot.keyboards.cancel import cancel_keyboard
from bot.states.payment import EditPaymentState
from repositories.payment_settings import PaymentSettingsRepository

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())

payment_repo = PaymentSettingsRepository()

# Номер карты: 16 цифр (можно с пробелами по 4)
CARD_REGEX = re.compile(r"^\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}$")


def payment_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏦 Изменить банк", callback_data="edit_payment_bank")],
            [InlineKeyboardButton(text="👤 Изменить получателя", callback_data="edit_payment_recipient")],
            [InlineKeyboardButton(text="💳 Изменить номер карты", callback_data="edit_payment_card")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back")],
        ]
    )


@router.callback_query(F.data == "admin_payment_settings")
async def payment_settings_menu(
        callback: CallbackQuery,
        session: AsyncSession,
):
    record = await payment_repo.get_or_default(session)

    await callback.message.edit_text(
        f"💳 <b>Текущие реквизиты оплаты:</b>\n\n"
        f"🏦 Банк: {record.bank_name}\n"
        f"👤 Получатель: {record.recipient}\n"
        f"💳 Карта: <code>{record.card_number}</code>\n\n"
        f"Выберите что изменить:",
        reply_markup=payment_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


# ── Изменить банк ────────────────────────────────────────────────────────────

@router.callback_query(F.data == "edit_payment_bank")
async def edit_bank(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPaymentState.waiting_bank)
    await callback.message.answer("🏦 Введите название банка (например: OZON BANK):")
    await callback.answer()


@router.message(EditPaymentState.waiting_bank)
async def save_bank(message: Message, state: FSMContext, session: AsyncSession):
    bank = message.text.strip()

    if len(bank) < 2:
        await message.answer("❌ Слишком короткое название. Попробуйте ещё раз:")
        return

    record = await payment_repo.update(session=session, bank_name=bank)
    await message.answer(f"✅ Банк обновлён: {record.bank_name}")
    await state.clear()


# ── Изменить получателя ──────────────────────────────────────────────────────

@router.callback_query(F.data == "edit_payment_recipient")
async def edit_recipient(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPaymentState.waiting_recipient)
    await callback.message.answer("👤 Введите имя получателя (Фамилия Имя):")
    await callback.answer()


@router.message(EditPaymentState.waiting_recipient)
async def save_recipient(message: Message, state: FSMContext, session: AsyncSession):
    recipient = message.text.strip()

    if len(recipient) < 3:
        await message.answer("❌ Слишком короткое имя. Попробуйте ещё раз:")
        return

    record = await payment_repo.update(session=session, recipient=recipient)
    await message.answer(f"✅ Получатель обновлён: {record.recipient}")
    await state.clear()


# ── Изменить номер карты ─────────────────────────────────────────────────────

@router.callback_query(F.data == "edit_payment_card")
async def edit_card(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPaymentState.waiting_card)
    await callback.message.answer(
        "💳 Введите номер карты (16 цифр):\n\n"
        "Пример: 2204320905741320",
        reply_markup = cancel_keyboard()
    )
    await callback.answer()


@router.message(EditPaymentState.waiting_card)
async def save_card(message: Message, state: FSMContext, session: AsyncSession):
    card = message.text.strip()

    if not CARD_REGEX.match(card):
        await message.answer(
            "❌ Неверный формат.\n"
            "Введите 16 цифр номера карты, например:\n"
            "2204320905741320"
        )
        return

    # Убираем пробелы/дефисы — храним только цифры
    card_clean = re.sub(r"[\s\-]", "", card)

    record = await payment_repo.update(session=session, card_number=card_clean)
    await message.answer(
        f"✅ Номер карты обновлён:\n<code>{record.card_number}</code>",
        parse_mode="HTML",
    )
    await state.clear()