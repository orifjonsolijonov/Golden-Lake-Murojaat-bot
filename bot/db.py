import os
import time

import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY,
    lang        TEXT,
    full_name   TEXT,
    phone       TEXT,
    username    TEXT,
    created_at  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS tickets (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    category        TEXT NOT NULL,
    full_name       TEXT NOT NULL,
    phone           TEXT NOT NULL,
    lang            TEXT NOT NULL,
    username        TEXT,
    body            TEXT NOT NULL DEFAULT '',
    attachments     INTEGER NOT NULL DEFAULT 0,
    status          TEXT NOT NULL DEFAULT 'new',
    status_by       TEXT,
    card_chat_id    INTEGER,
    card_message_id INTEGER,
    created_at      INTEGER NOT NULL,
    updated_at      INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tickets_user ON tickets(user_id, created_at);

-- Qaysi xabar qaysi murojaatga tegishli (reply orqali javob berish uchun)
CREATE TABLE IF NOT EXISTS message_links (
    chat_id     INTEGER NOT NULL,
    message_id  INTEGER NOT NULL,
    ticket_id   INTEGER NOT NULL,
    PRIMARY KEY (chat_id, message_id)
);
"""


class DB:
    def __init__(self, path: str):
        self.path = path
        self.conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        self.conn = await aiosqlite.connect(self.path)
        self.conn.row_factory = aiosqlite.Row
        await self.conn.execute("PRAGMA journal_mode=WAL")
        await self.conn.executescript(SCHEMA)
        await self.conn.commit()

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()

    # --- users ---
    async def get_user(self, user_id: int) -> aiosqlite.Row | None:
        cur = await self.conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return await cur.fetchone()

    async def upsert_user(self, user_id: int, username: str | None, **fields) -> None:
        await self.conn.execute(
            "INSERT INTO users (user_id, username, created_at) VALUES (?, ?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET username = excluded.username",
            (user_id, username, int(time.time())),
        )
        for key in ("lang", "full_name", "phone"):
            if key in fields:
                await self.conn.execute(
                    f"UPDATE users SET {key} = ? WHERE user_id = ?", (fields[key], user_id)
                )
        await self.conn.commit()

    async def get_lang(self, user_id: int) -> str | None:
        row = await self.get_user(user_id)
        return row["lang"] if row else None

    # --- tickets ---
    async def create_ticket(
        self,
        user_id: int,
        username: str | None,
        category: str,
        full_name: str,
        phone: str,
        lang: str,
        body: str,
        attachments: int,
    ) -> int:
        now = int(time.time())
        cur = await self.conn.execute(
            "INSERT INTO tickets (user_id, username, category, full_name, phone, lang, body, attachments, "
            "created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, username, category, full_name, phone, lang, body, attachments, now, now),
        )
        await self.conn.commit()
        return cur.lastrowid

    async def delete_ticket(self, ticket_id: int) -> None:
        await self.conn.execute("DELETE FROM message_links WHERE ticket_id = ?", (ticket_id,))
        await self.conn.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
        await self.conn.commit()

    async def get_ticket(self, ticket_id: int) -> aiosqlite.Row | None:
        cur = await self.conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        return await cur.fetchone()

    async def set_card(self, ticket_id: int, chat_id: int, message_id: int) -> None:
        await self.conn.execute(
            "UPDATE tickets SET card_chat_id = ?, card_message_id = ? WHERE id = ?",
            (chat_id, message_id, ticket_id),
        )
        await self.conn.commit()

    async def set_status(self, ticket_id: int, status: str, by: str) -> None:
        await self.conn.execute(
            "UPDATE tickets SET status = ?, status_by = ?, updated_at = ? WHERE id = ?",
            (status, by, int(time.time()), ticket_id),
        )
        await self.conn.commit()

    async def last_ticket_time(self, user_id: int) -> int | None:
        cur = await self.conn.execute(
            "SELECT MAX(created_at) AS t FROM tickets WHERE user_id = ?", (user_id,)
        )
        row = await cur.fetchone()
        return row["t"] if row else None

    async def stats(self) -> dict[str, int]:
        cur = await self.conn.execute("SELECT status, COUNT(*) AS c FROM tickets GROUP BY status")
        result = {row["status"]: row["c"] for row in await cur.fetchall()}
        day_ago = int(time.time()) - 86400
        cur = await self.conn.execute("SELECT COUNT(*) AS c FROM tickets WHERE created_at >= ?", (day_ago,))
        result["_today"] = (await cur.fetchone())["c"]
        return result

    # --- message links ---
    async def link(self, chat_id: int, message_id: int, ticket_id: int) -> None:
        await self.conn.execute(
            "INSERT OR REPLACE INTO message_links (chat_id, message_id, ticket_id) VALUES (?, ?, ?)",
            (chat_id, message_id, ticket_id),
        )
        await self.conn.commit()

    async def ticket_by_message(self, chat_id: int, message_id: int) -> int | None:
        cur = await self.conn.execute(
            "SELECT ticket_id FROM message_links WHERE chat_id = ? AND message_id = ?",
            (chat_id, message_id),
        )
        row = await cur.fetchone()
        return row["ticket_id"] if row else None
