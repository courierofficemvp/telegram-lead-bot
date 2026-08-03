from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from app.keyboards import duplicate_keyboard, language_keyboard
from app.localization import t
from app.services.database import LeadRepository
from app.states import LeadForm

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext, repository: LeadRepository):
    await state.clear()
    parts = (message.text or "").split(maxsplit=1)
    await state.update_data(start_param=parts[1].strip() if len(parts) > 1 else "")
    if await repository.has_submitted(message.from_user.id):
        language = message.from_user.language_code or "ru"
        if language not in {"pl", "ua", "ru", "en"}:
            language = "ru"
        await state.update_data(language=language)
        await message.answer(t(language, "already"), reply_markup=duplicate_keyboard(language))
        return
    await state.set_state(LeadForm.language)
    await message.answer("Wybierz język / Оберіть мову / Выберите язык / Choose language",
                         reply_markup=language_keyboard())

@router.callback_query(F.data == "duplicate:again")
async def duplicate_again(callback: CallbackQuery, state: FSMContext):
    await state.set_state(LeadForm.language)
    await callback.message.edit_text(
        "Wybierz język / Оберіть мову / Выберите язык / Choose language",
        reply_markup=language_keyboard())
    await callback.answer()

@router.callback_query(F.data == "duplicate:cancel")
async def duplicate_cancel(callback: CallbackQuery, state: FSMContext):
    language = (await state.get_data()).get("language", "ru")
    await callback.message.edit_text(t(language, "cancelled"))
    await state.clear()
    await callback.answer()
