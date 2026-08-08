from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.localization import LANGUAGE_BUTTONS, t


def language_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=LANGUAGE_BUTTONS["pl"]),
                KeyboardButton(text=LANGUAGE_BUTTONS["ua"]),
            ],
            [
                KeyboardButton(text=LANGUAGE_BUTTONS["ru"]),
                KeyboardButton(text=LANGUAGE_BUTTONS["en"]),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Wybierz język / Оберіть мову / Выберите язык / Choose language",
    )


def phone_keyboard(language):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(language, "share_phone"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def city_keyboard(language):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(language, "city"))]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def duplicate_keyboard(language):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(language, "again"))],
            [KeyboardButton(text=t(language, "cancel"))],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
