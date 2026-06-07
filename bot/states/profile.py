from aiogram.fsm.state import State, StatesGroup


class EditProfileState(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_address = State()
