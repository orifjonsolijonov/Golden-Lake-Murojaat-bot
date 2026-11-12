"""aiogram FSM holatini Postgres'da saqlash (Vercel'da xotira so'rovlar orasida saqlanmaydi)."""

from typing import Any

from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey

from .db import current_db


def _key(key: StorageKey) -> str:
    return ":".join(
        str(x) for x in (key.bot_id, key.chat_id, key.user_id, key.thread_id or "", key.destiny)
    )


class PostgresStorage(BaseStorage):
    @property
    def db(self):
        return current_db.get()

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        value = state.state if isinstance(state, State) else state
        await self.db.fsm_set_state(_key(key), value)

    async def get_state(self, key: StorageKey) -> str | None:
        state, _ = await self.db.fsm_get(_key(key))
        return state

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        await self.db.fsm_set_data(_key(key), dict(data))

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        _, data = await self.db.fsm_get(_key(key))
        return data

    async def close(self) -> None:
        pass
