from html import escape
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def profile_link(username, telegram_id):
    return f"https://t.me/{username}" if username else f"tg://user?id={telegram_id}"

from html import escape

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_profile_link(username: str | None) -> str | None:
    if not username:
        return None

    return f"https://t.me/{username}"


async def send_lead_to_group(
    bot,
    group_chat_id: int,
    topic_id: int,
    lead: dict,
) -> None:
    username = lead.get("username")
    username_text = (
        f"@{escape(username)}"
        if username
        else "brak / немає / отсутствует / none"
    )

    text = (
        "🟢 <b>NOWA APLIKACJA / НОВАЯ ЗАЯВКА</b>\n\n"
        f"👤 <b>Imię / Имя:</b> {escape(lead['full_name'])}\n"
        f"📱 <b>Telefon:</b> {escape(lead['phone'])}\n"
        f"📧 <b>Email:</b> {escape(lead['email'])}\n"
        f"📍 <b>Miasto / Город:</b> Warszawa\n"
        f"🌐 <b>Język / Язык:</b> {escape(lead['language_name'])}\n\n"
        f"💬 <b>Telegram:</b> {username_text}\n"
        f"🆔 <b>Telegram ID:</b> <code>{lead['telegram_id']}</code>\n"
        f"📢 <b>Źródło / Источник:</b> {escape(lead['source'])}\n"
        f"🔖 <b>Start param:</b> {escape(lead['start_param'] or '-')}\n"
        f"🕓 <b>Data / Дата:</b> {escape(lead['submitted_at'])}"
    )

    profile_link = build_profile_link(username)

    reply_markup = None

    if profile_link:
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💬 Otwórz Telegram",
                        url=profile_link,
                    )
                ]
            ]
        )

    try:
        await bot.send_message(
            chat_id=group_chat_id,
            message_thread_id=topic_id,
            text=text,
            parse_mode="HTML",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )

    except Exception:
        import traceback

        print("\n========== TELEGRAM ERROR ==========")
        traceback.print_exc()
        print("====================================\n")

        raise
