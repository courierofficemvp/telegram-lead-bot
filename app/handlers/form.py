import re
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from app.keyboards import city_keyboard, language_keyboard, phone_keyboard
from app.localization import LANGUAGE_BUTTONS, LANGUAGE_NAMES, t
from app.services.notifier import profile_link, send_lead_to_group
from app.states import LeadForm

router = Router()
EMAIL_RE = re.compile(r"^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$")


async def safe_delete_message(bot, chat_id: int, message_id: int | None) -> None:
    if not message_id:
        return
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except (TelegramBadRequest, TelegramForbiddenError):
        pass


async def delete_answer_and_previous_prompt(message: Message, state: FSMContext) -> None:
    data = await state.get_data()

    await safe_delete_message(
        message.bot,
        message.chat.id,
        data.get("last_bot_message_id"),
    )

    try:
        await message.delete()
    except (TelegramBadRequest, TelegramForbiddenError):
        pass


async def send_prompt(
    message: Message,
    state: FSMContext,
    text: str,
    reply_markup=None,
) -> None:
    sent = await message.answer(text, reply_markup=reply_markup)
    await state.update_data(last_bot_message_id=sent.message_id)


LANGUAGE_BY_BUTTON = {
    button_text: code
    for code, button_text in LANGUAGE_BUTTONS.items()
}


@router.message(LeadForm.language)
async def select_language(message: Message, state: FSMContext):
    button_text = (message.text or "").strip()
    language = LANGUAGE_BY_BUTTON.get(button_text)

    if not language:
        data = await state.get_data()
        current_language = data.get("language", "ru")

        await delete_answer_and_previous_prompt(message, state)

        sent = await message.answer(
            t(current_language, "choose_language"),
            reply_markup=language_keyboard(),
        )
        await state.update_data(last_bot_message_id=sent.message_id)
        return

    await delete_answer_and_previous_prompt(message, state)

    await state.update_data(language=language)
    await state.set_state(LeadForm.full_name)

    await send_prompt(
        message,
        state,
        t(language, "ask_name"),
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(LeadForm.full_name)
async def receive_name(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data["language"]
    full_name = (message.text or "").strip()

    if len(full_name.split()) < 2 or len(full_name) < 4:
        await delete_answer_and_previous_prompt(message, state)
        await send_prompt(
            message,
            state,
            f'{t(language, "name_invalid")}\\n\\n{t(language, "ask_name")}',
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    await delete_answer_and_previous_prompt(message, state)
    await state.update_data(full_name=full_name)
    await state.set_state(LeadForm.phone)

    await send_prompt(
        message,
        state,
        t(language, "ask_phone"),
        reply_markup=phone_keyboard(language),
    )


@router.message(LeadForm.phone, F.contact)
async def receive_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data["language"]

    if message.contact.user_id and message.contact.user_id != message.from_user.id:
        await delete_answer_and_previous_prompt(message, state)
        await send_prompt(
            message,
            state,
            t(language, "phone_invalid"),
            reply_markup=phone_keyboard(language),
        )
        return

    await delete_answer_and_previous_prompt(message, state)

    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(LeadForm.email)

    await send_prompt(
        message,
        state,
        t(language, "ask_email"),
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(LeadForm.phone)
async def invalid_phone(message: Message, state: FSMContext):
    language = (await state.get_data())["language"]

    await delete_answer_and_previous_prompt(message, state)

    await send_prompt(
        message,
        state,
        t(language, "phone_invalid"),
        reply_markup=phone_keyboard(language),
    )


@router.message(LeadForm.email)
async def receive_email(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data["language"]
    email = (message.text or "").strip().lower()

    if not EMAIL_RE.fullmatch(email):
        await delete_answer_and_previous_prompt(message, state)
        await send_prompt(
            message,
            state,
            f'{t(language, "email_invalid")}\\n\\n{t(language, "ask_email")}',
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    await delete_answer_and_previous_prompt(message, state)

    await state.update_data(email=email)
    await state.set_state(LeadForm.city)

    await send_prompt(
        message,
        state,
        t(language, "ask_city"),
        reply_markup=city_keyboard(language),
    )


@router.message(LeadForm.city)
async def receive_city(message: Message, state: FSMContext, bot, config, sheets, repository):
    data = await state.get_data()
    language = data["language"]

    valid_city_buttons = {t(code, "city") for code in LANGUAGE_NAMES}

    if (message.text or "").strip() not in valid_city_buttons:
        await delete_answer_and_previous_prompt(message, state)
        await send_prompt(
            message,
            state,
            t(language, "ask_city"),
            reply_markup=city_keyboard(language),
        )
        return

    await delete_answer_and_previous_prompt(message, state)

    submitted_at = datetime.now(
        ZoneInfo(config.timezone)
    ).strftime("%d.%m.%Y %H:%M:%S")

    username = message.from_user.username
    start_param = data.get("start_param", "")

    lead = {
        "submitted_at": submitted_at,
        "full_name": data["full_name"],
        "phone": data["phone"],
        "email": data["email"],
        "city": "Warszawa",
        "language_name": LANGUAGE_NAMES[language],
        "username": username,
        "telegram_id": message.from_user.id,
        "source": "Telegram Ads" if start_param else "Telegram",
        "start_param": start_param,
    }

    try:
        await sheets.append_row([
            submitted_at,
            lead["full_name"],
            lead["phone"],
            lead["email"],
            "Warszawa",
            lead["language_name"],
            f"@{username}" if username else "",
            str(lead["telegram_id"]),
            profile_link(username, lead["telegram_id"]),
            lead["source"],
            start_param,
        ])

        await send_lead_to_group(
            bot,
            config.group_chat_id,
            config.topic_id,
            lead,
        )

        await repository.mark_submitted(
            message.from_user.id,
            submitted_at,
        )

    except Exception:
        sent = await message.answer(
            t(language, "error"),
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.update_data(last_bot_message_id=sent.message_id)
        return

    await state.clear()

    await message.answer(
        t(language, "success"),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
