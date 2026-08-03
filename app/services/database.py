from pathlib import Path
import aiosqlite

class LeadRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    async def init(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS submitted_users (
                telegram_id INTEGER PRIMARY KEY,
                last_submission_at TEXT NOT NULL
            )""")
            await db.commit()

    async def has_submitted(self, telegram_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT 1 FROM submitted_users WHERE telegram_id = ?", (telegram_id,))
            return await cursor.fetchone() is not None

    async def mark_submitted(self, telegram_id: int, submitted_at: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""INSERT INTO submitted_users VALUES (?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET last_submission_at=excluded.last_submission_at""",
                (telegram_id, submitted_at))
            await db.commit()
