from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from app.localization import t

def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇵🇱 Polski", callback_data="lang:pl"),
         InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang:ua")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
         InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en")],
    ])

def phone_keyboard(language):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(language, "share_phone"), request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True,
    )

def city_keyboard(language):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(language, "city"))]],
        resize_keyboard=True, one_time_keyboard=True,
    )

def duplicate_keyboard(language):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(language, "again"), callback_data="duplicate:again")],
        [InlineKeyboardButton(text=t(language, "cancel"), callback_data="duplicate:cancel")],
    ])
