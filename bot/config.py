import os
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()


def _int_or_none(value: str | None) -> int | None:
    value = (value or "").strip()
    return int(value) if value else None


@dataclass(frozen=True)
class Config:
    bot_token: str
    group_chat_id: int | None
    group_thread_id: int | None
    tz: ZoneInfo
    db_path: str


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN topilmadi. .env faylini to'ldiring (.env.example ga qarang).")
    return Config(
        bot_token=token,
        group_chat_id=_int_or_none(os.getenv("GROUP_CHAT_ID")),
        group_thread_id=_int_or_none(os.getenv("GROUP_THREAD_ID")),
        tz=ZoneInfo(os.getenv("TIMEZONE", "Asia/Tashkent")),
        db_path=os.getenv("DB_PATH", "data/bot.db"),
    )


config = load_config()
