import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import load_config
from app.handlers import routers
from app.services.database import LeadRepository
from app.services.google_sheets import GoogleSheetsService

async def main():
    logging.basicConfig(level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    config = load_config()
    repository = LeadRepository(config.database_path)
    await repository.init()
    sheets = GoogleSheetsService(
        config.service_account_file, config.spreadsheet_id, config.sheet_name)
    bot = Bot(token=config.bot_token)
    dispatcher = Dispatcher(storage=MemoryStorage())
    for router in routers:
        dispatcher.include_router(router)
    dispatcher["config"] = config
    dispatcher["sheets"] = sheets
    dispatcher["repository"] = repository
    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
