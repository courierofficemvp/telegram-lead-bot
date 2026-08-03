from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    bot_token: str
    group_chat_id: int
    topic_id: int
    spreadsheet_id: str
    sheet_name: str
    service_account_file: Path
    timezone: str
    database_path: Path

def load_config() -> Config:
    names = ["BOT_TOKEN", "GROUP_CHAT_ID", "TOPIC_ID", "SPREADSHEET_ID", "GOOGLE_SERVICE_ACCOUNT_FILE"]
    missing = [name for name in names if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")
    return Config(
        bot_token=os.environ["BOT_TOKEN"],
        group_chat_id=int(os.environ["GROUP_CHAT_ID"]),
        topic_id=int(os.environ["TOPIC_ID"]),
        spreadsheet_id=os.environ["SPREADSHEET_ID"],
        sheet_name=os.getenv("SHEET_NAME", "Telegram Ads"),
        service_account_file=Path(os.environ["GOOGLE_SERVICE_ACCOUNT_FILE"]),
        timezone=os.getenv("TIMEZONE", "Europe/Warsaw"),
        database_path=Path("data/leads.db"),
    )
