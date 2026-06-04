from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


# class AddPhotoState(StatesGroup):
#     waiting_photo = State()


class EditStockState(StatesGroup):
    waiting_stock = State()


class EditPriceState(StatesGroup):
    waiting_price = State()


class AddProductState(StatesGroup):
    waiting_name = State()
    waiting_description = State()
    waiting_price = State()
    waiting_stock = State()
    waiting_category = State()


class EditProductCategory(StatesGroup):
    change_category = State()

class EditNameState(StatesGroup):
    waiting_name = State()


class EditDescriptionState(StatesGroup):
    waiting_description = State()

