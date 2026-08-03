import re
from datetime import datetime
from zoneinfo import ZoneInfo
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from app.keyboards import city_keyboard, phone_keyboard
from app.localization import LANGUAGE_NAMES, t
from app.services.notifier import profile_link, send_lead_to_group
from app.states import LeadForm

router = Router()
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

@router.callback_query(LeadForm.language, F.data.startswith("lang:"))
async def select_language(callback: CallbackQuery, state: FSMContext):
    language = callback.data.split(":", 1)[1]
    await state.update_data(language=language)
    await state.set_state(LeadForm.full_name)
    await callback.message.edit_text(t(language, "welcome"))
    await callback.message.answer(t(language, "ask_name"))
    await callback.answer()

@router.message(LeadForm.full_name)
async def receive_name(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data["language"]
    full_name = (message.text or "").strip()
    if len(full_name.split()) < 2 or len(full_name) < 4:
        await message.answer(t(language, "name_invalid"))
        return
    await state.update_data(full_name=full_name)
    await state.set_state(LeadForm.phone)
    await message.answer(t(language, "ask_phone"), reply_markup=phone_keyboard(language))

@router.message(LeadForm.phone, F.contact)
async def receive_phone(message: Message, state: FSMContext):
    language = (await state.get_data())["language"]
    if message.contact.user_id and message.contact.user_id != message.from_user.id:
        await message.answer(t(language, "phone_invalid"))
        return
    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(LeadForm.email)
    await message.answer(t(language, "ask_email"), reply_markup=ReplyKeyboardRemove())

@router.message(LeadForm.phone)
async def invalid_phone(message: Message, state: FSMContext):
    language = (await state.get_data())["language"]
    await message.answer(t(language, "phone_invalid"), reply_markup=phone_keyboard(language))

@router.message(LeadForm.email)
async def receive_email(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data["language"]
    email = (message.text or "").strip().lower()
    if not EMAIL_RE.fullmatch(email):
        await message.answer(t(language, "email_invalid"))
        return
    await state.update_data(email=email)
    await state.set_state(LeadForm.city)
    await message.answer(t(language, "ask_city"), reply_markup=city_keyboard(language))

@router.message(LeadForm.city)
async def receive_city(message: Message, state: FSMContext, bot, config, sheets, repository):
    data = await state.get_data()
    language = data["language"]
    if (message.text or "").strip() not in {t(code, "city") for code in LANGUAGE_NAMES}:
        await message.answer(t(language, "ask_city"), reply_markup=city_keyboard(language))
        return
    submitted_at = datetime.now(ZoneInfo(config.timezone)).strftime("%d.%m.%Y %H:%M:%S")
    username = message.from_user.username
    start_param = data.get("start_param", "")
    lead = {
        "submitted_at": submitted_at, "full_name": data["full_name"],
        "phone": data["phone"], "email": data["email"], "city": "Warszawa",
        "language_name": LANGUAGE_NAMES[language], "username": username,
        "telegram_id": message.from_user.id,
        "source": "Telegram Ads" if start_param else "Telegram",
        "start_param": start_param,
    }
    try:
        await sheets.append_row([
            submitted_at, lead["full_name"], lead["phone"], lead["email"], "Warszawa",
            lead["language_name"], f"@{username}" if username else "",
            str(lead["telegram_id"]), profile_link(username, lead["telegram_id"]),
            lead["source"], start_param,
        ])
        await send_lead_to_group(bot, config.group_chat_id, config.topic_id, lead)
        await repository.mark_submitted(message.from_user.id, submitted_at)
    except Exception:
        await message.answer(t(language, "error"), reply_markup=ReplyKeyboardRemove())
        return
    await message.answer(t(language, "success"), reply_markup=ReplyKeyboardRemove())
    await state.clear()
