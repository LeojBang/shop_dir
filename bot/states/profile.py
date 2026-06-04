from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class EditProfileState(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_address = State()