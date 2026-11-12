import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from .config import config
from .db import DB
from .handlers import routers

log = logging.getLogger("bot")


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    db = DB(config.db_path)
    await db.connect()

    bot = Bot(config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage(), db=db)
    dp.include_routers(*routers)

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Asosiy menyu / Главное меню"),
            BotCommand(command="new", description="Murojaat yuborish / Оставить обращение"),
            BotCommand(command="cancel", description="Bekor qilish / Отменить"),
        ],
        scope=BotCommandScopeAllPrivateChats(),
    )

    me = await bot.get_me()
    if config.group_chat_id:
        log.info("@%s ishga tushdi. Murojaatlar guruhi: %s", me.username, config.group_chat_id)
    else:
        log.warning(
            "@%s ishga tushdi, lekin GROUP_CHAT_ID sozlanmagan! Botni guruhga qo'shing — "
            "u guruh ID'sini o'zi yozib beradi.", me.username,
        )

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
