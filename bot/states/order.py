from aiogram.fsm.state import State, StatesGroup


class TrackingState(StatesGroup):
    waiting_tracking_number = State()
