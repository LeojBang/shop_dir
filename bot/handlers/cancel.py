from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

router = Router()


async def cancel_fsm(state: FSMContext):
    """Сбрасывает FSM если активно."""
    current = await state.get_state()
    if current is not None:
        await state.clear()
        return True
    return False


@router.message(Command("cancel"))
async def cancel_command(message: Message, state: FSMContext):
    cleared = await cancel_fsm(state)
    if cleared:
        await message.answer("❌ Действие отменено.")
    else:
        await message.answer("Нечего отменять.")


@router.callback_query(F.data == "cancel_fsm")
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    await cancel_fsm(state)
    await callback.message.delete()
    await callback.answer("❌ Отменено")