"""Postgres (Neon) bilan ishlash. Vercel'da fayl tizimi saqlanmagani uchun barcha ma’lumot shu yerda."""

import json
import time
from contextvars import ContextVar
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import asyncpg

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id     BIGINT PRIMARY KEY,
    lang        TEXT,
    full_name   TEXT,
    phone       TEXT,
    username    TEXT,
    created_at  BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS tickets (
    id              SERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    category        TEXT NOT NULL,
    full_name       TEXT NOT NULL,
    phone           TEXT NOT NULL,
    lang            TEXT NOT NULL,
    username        TEXT,
    body            TEXT NOT NULL DEFAULT '',
    attachments     INTEGER NOT NULL DEFAULT 0,
    status          TEXT NOT NULL DEFAULT 'new',
    status_by       TEXT,
    card_chat_id    BIGINT,
    card_message_id BIGINT,
    created_at      BIGINT NOT NULL,
    updated_at      BIGINT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tickets_user ON tickets(user_id, created_at);

-- Qaysi xabar qaysi murojaatga tegishli (reply orqali javob berish uchun)
CREATE TABLE IF NOT EXISTS message_links (
    chat_id     BIGINT NOT NULL,
    message_id  BIGINT NOT NULL,
    ticket_id   INTEGER NOT NULL,
    PRIMARY KEY (chat_id, message_id)
);

-- Mijoz murojaat yozish jarayonining qaysi bosqichida turgani (FSM)
CREATE TABLE IF NOT EXISTS fsm (
    key     TEXT PRIMARY KEY,
    state   TEXT,
    data    TEXT NOT NULL DEFAULT '{}'
);
"""


def clean_dsn(dsn: str) -> str:
    """Neon beradigan `channel_binding` parametrini asyncpg tushunmaydi — olib tashlaymiz."""
    parts = urlsplit(dsn)
    query = [(k, v) for k, v in parse_qsl(parts.query) if k != "channel_binding"]
    return urlunsplit(parts._replace(query=urlencode(query)))


class DB:
    def __init__(self, dsn: str):
        self.dsn = clean_dsn(dsn)
        self.conn: asyncpg.Connection | None = None

    async def connect(self, create_schema: bool = True) -> None:
        self.conn = await asyncpg.connect(self.dsn, statement_cache_size=0)
        if create_schema:
            await self.conn.execute(SCHEMA)

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()
            self.conn = None

    # --- users ---
    async def get_user(self, user_id: int):
        return await self.conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)

    async def upsert_user(self, user_id: int, username: str | None, **fields) -> None:
        await self.conn.execute(
            "INSERT INTO users (user_id, username, created_at) VALUES ($1, $2, $3) "
            "ON CONFLICT (user_id) DO UPDATE SET username = EXCLUDED.username",
            user_id, username, int(time.time()),
        )
        for key in ("lang", "full_name", "phone"):
            if key in fields:
                await self.conn.execute(f"UPDATE users SET {key} = $1 WHERE user_id = $2", fields[key], user_id)

    async def get_lang(self, user_id: int) -> str | None:
        return await self.conn.fetchval("SELECT lang FROM users WHERE user_id = $1", user_id)

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
        return await self.conn.fetchval(
            "INSERT INTO tickets (user_id, username, category, full_name, phone, lang, body, attachments, "
            "created_at, updated_at) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $9) RETURNING id",
            user_id, username, category, full_name, phone, lang, body, attachments, now,
        )

    async def delete_ticket(self, ticket_id: int) -> None:
        await self.conn.execute("DELETE FROM message_links WHERE ticket_id = $1", ticket_id)
        await self.conn.execute("DELETE FROM tickets WHERE id = $1", ticket_id)

    async def get_ticket(self, ticket_id: int):
        return await self.conn.fetchrow("SELECT * FROM tickets WHERE id = $1", ticket_id)

    async def set_card(self, ticket_id: int, chat_id: int, message_id: int) -> None:
        await self.conn.execute(
            "UPDATE tickets SET card_chat_id = $1, card_message_id = $2 WHERE id = $3",
            chat_id, message_id, ticket_id,
        )

    async def set_status(self, ticket_id: int, status: str, by: str) -> None:
        await self.conn.execute(
            "UPDATE tickets SET status = $1, status_by = $2, updated_at = $3 WHERE id = $4",
            status, by, int(time.time()), ticket_id,
        )

    async def last_ticket_time(self, user_id: int) -> int | None:
        return await self.conn.fetchval("SELECT MAX(created_at) FROM tickets WHERE user_id = $1", user_id)

    async def stats(self) -> dict[str, int]:
        rows = await self.conn.fetch("SELECT status, COUNT(*) AS c FROM tickets GROUP BY status")
        result = {row["status"]: row["c"] for row in rows}
        result["_today"] = await self.conn.fetchval(
            "SELECT COUNT(*) FROM tickets WHERE created_at >= $1", int(time.time()) - 86400
        )
        return result

    # --- message links ---
    async def link(self, chat_id: int, message_id: int, ticket_id: int) -> None:
        await self.conn.execute(
            "INSERT INTO message_links (chat_id, message_id, ticket_id) VALUES ($1, $2, $3) "
            "ON CONFLICT (chat_id, message_id) DO UPDATE SET ticket_id = EXCLUDED.ticket_id",
            chat_id, message_id, ticket_id,
        )

    async def ticket_by_message(self, chat_id: int, message_id: int) -> int | None:
        return await self.conn.fetchval(
            "SELECT ticket_id FROM message_links WHERE chat_id = $1 AND message_id = $2", chat_id, message_id
        )

    # --- FSM ---
    async def fsm_get(self, key: str) -> tuple[str | None, dict]:
        row = await self.conn.fetchrow("SELECT state, data FROM fsm WHERE key = $1", key)
        if not row:
            return None, {}
        return row["state"], json.loads(row["data"])

    async def fsm_set_state(self, key: str, state: str | None) -> None:
        await self.conn.execute(
            "INSERT INTO fsm (key, state) VALUES ($1, $2) ON CONFLICT (key) DO UPDATE SET state = EXCLUDED.state",
            key, state,
        )

    async def fsm_set_data(self, key: str, data: dict) -> None:
        await self.conn.execute(
            "INSERT INTO fsm (key, data) VALUES ($1, $2) ON CONFLICT (key) DO UPDATE SET data = EXCLUDED.data",
            key, json.dumps(data, ensure_ascii=False),
        )


# Har bir so‘rov (update) uchun alohida ulanish — FSM storage uni shu yerdan oladi
current_db: ContextVar[DB] = ContextVar("current_db")
