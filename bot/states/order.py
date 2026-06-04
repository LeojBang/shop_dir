from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class TrackingState(StatesGroup):
    waiting_tracking_number = State()
