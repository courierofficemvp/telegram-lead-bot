from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards import duplicate_keyboard, language_keyboard
from app.localization import normalize_language_code, t
from app.services.database import LeadRepository
from app.states import LeadForm

router = Router()


async def safe_delete_message(bot, chat_id: int, message_id: int | None) -> None:
    if not message_id:
        return
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except (TelegramBadRequest, TelegramForbiddenError):
        pass


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext, repository: LeadRepository):
    await state.clear()

    parts = (message.text or "").split(maxsplit=1)
    start_param = parts[1].strip() if len(parts) > 1 else ""
    language = normalize_language_code(
        message.from_user.language_code if message.from_user else None
    )

    await state.update_data(start_param=start_param, language=language)

    if message.from_user and await repository.has_submitted(message.from_user.id):
        sent = await message.answer(
            t(language, "already"),
            reply_markup=duplicate_keyboard(language),
        )
        await state.update_data(last_bot_message_id=sent.message_id, duplicate_mode=True)
        return

    await state.set_state(LeadForm.language)

    sent = await message.answer(
        t(language, "start_greeting"),
        reply_markup=language_keyboard(),
    )
    await state.update_data(last_bot_message_id=sent.message_id, duplicate_mode=False)


@router.message(F.text.in_({t(code, "again") for code in ("pl", "ua", "ru", "en")}))
async def duplicate_again(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get("duplicate_mode"):
        return

    await safe_delete_message(message.bot, message.chat.id, data.get("last_bot_message_id"))
    try:
        await message.delete()
    except (TelegramBadRequest, TelegramForbiddenError):
        pass

    await state.update_data(duplicate_mode=False)
    await state.set_state(LeadForm.language)

    language = data.get("language", "ru")
    sent = await message.answer(
        t(language, "start_greeting"),
        reply_markup=language_keyboard(),
    )
    await state.update_data(last_bot_message_id=sent.message_id)


@router.message(F.text.in_({t(code, "cancel") for code in ("pl", "ua", "ru", "en")}))
async def duplicate_cancel(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get("duplicate_mode"):
        return

    language = data.get("language", "ru")

    await safe_delete_message(message.bot, message.chat.id, data.get("last_bot_message_id"))
    try:
        await message.delete()
    except (TelegramBadRequest, TelegramForbiddenError):
        pass

    await state.clear()
    await message.answer(t(language, "cancelled"))
