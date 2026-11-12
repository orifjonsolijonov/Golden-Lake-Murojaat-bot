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
    database_url: str
    webhook_secret: str


def _require(name: str, hint: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} topilmadi ({hint}). Vercel → Settings → Environment Variables ga qo'shing.")
    return value


def load_config() -> Config:
    return Config(
        bot_token=_require("BOT_TOKEN", "@BotFather tokeni"),
        group_chat_id=_int_or_none(os.getenv("GROUP_CHAT_ID")),
        group_thread_id=_int_or_none(os.getenv("GROUP_THREAD_ID")),
        tz=ZoneInfo(os.getenv("TIMEZONE", "Asia/Tashkent")),
        database_url=_require("DATABASE_URL", "Neon'dan olingan Postgres manzili"),
        webhook_secret=os.getenv("WEBHOOK_SECRET", "").strip(),
    )


config = load_config()
