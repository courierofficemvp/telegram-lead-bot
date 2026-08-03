from aiogram.fsm.state import State, StatesGroup

class LeadForm(StatesGroup):
    language = State()
    full_name = State()
    phone = State()
    email = State()
    city = State()
