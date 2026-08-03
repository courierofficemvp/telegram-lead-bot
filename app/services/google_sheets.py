import asyncio
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials

class GoogleSheetsService:
    def __init__(self, service_account_file: Path, spreadsheet_id: str, sheet_name: str):
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_file(str(service_account_file), scopes=scopes)
        self.worksheet = gspread.authorize(credentials).open_by_key(spreadsheet_id).worksheet(sheet_name)

    async def append_row(self, values):
        await asyncio.to_thread(self.worksheet.append_row, list(values), value_input_option="USER_ENTERED")
