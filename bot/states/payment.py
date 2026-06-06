from aiogram.fsm.state import State, StatesGroup


class EditPaymentState(StatesGroup):
    waiting_bank = State()
    waiting_recipient = State()
    waiting_card = State()