"""Bot, dispatcher va bitta update'ni qayta ishlash (Vercel webhook va lokal polling uchun umumiy)."""

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, Update

from .config import config
from .db import DB, current_db
from .handlers import routers
from .storage import PostgresStorage

log = logging.getLogger("bot")

dp = Dispatcher(storage=PostgresStorage())
dp.include_routers(*routers)

COMMANDS = [
    BotCommand(command="start", description="Asosiy menyu / Главное меню"),
    BotCommand(command="new", description="Murojaat yuborish / Оставить обращение"),
    BotCommand(command="cancel", description="Bekor qilish / Отменить"),
]


def make_bot() -> Bot:
    return Bot(config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def open_db(create_schema: bool = False) -> DB:
    db = DB(config.database_url)
    await db.connect(create_schema=create_schema)
    current_db.set(db)
    return db


async def handle_update(payload: dict) -> None:
    """Telegram'dan kelgan bitta update'ni qayta ishlaydi."""
    bot = make_bot()
    db = await open_db()
    try:
        update = Update.model_validate(payload, context={"bot": bot})
        await dp.feed_update(bot, update, db=db)
    finally:
        await db.close()
        await bot.session.close()


async def setup_webhook(url: str) -> dict:
    """Bazada jadvallarni yaratadi, webhook va bot buyruqlarini o‘rnatadi."""
    bot = make_bot()
    db = await open_db(create_schema=True)
    try:
        await bot.set_webhook(
            url,
            secret_token=config.webhook_secret or None,
            max_connections=1,  # update'lar ketma-ket keladi — albomlar va holatlar aralashmaydi
            allowed_updates=dp.resolve_used_update_types(),
        )
        await bot.set_my_commands(COMMANDS, scope=BotCommandScopeAllPrivateChats())
        me = await bot.get_me()
        info = await bot.get_webhook_info()
        return {
            "ok": True,
            "bot": f"@{me.username}",
            "webhook": info.url,
            "group_chat_id": config.group_chat_id,
            "pending_updates": info.pending_update_count,
        }
    finally:
        await db.close()
        await bot.session.close()
