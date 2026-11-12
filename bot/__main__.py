"""Lokal ishga tushirish (polling). Vercel'da ishlatilmaydi — u yerda api/index.py ishlaydi.

Diqqat: polling ishlashi uchun webhook o'chiriladi. Keyin Vercel'dagi botni qayta ulash uchun
https://<sayt>/api/setup?secret=... manzilini yana bir marta oching.
"""

import asyncio
import logging

from aiogram.types import Update

from .app import dp, handle_update, make_bot, open_db

log = logging.getLogger("bot")


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    db = await open_db(create_schema=True)
    await db.close()

    bot = make_bot()
    await bot.delete_webhook()
    me = await bot.get_me()
    log.info("@%s lokal rejimda ishga tushdi (polling)", me.username)

    offset = None
    try:
        while True:
            updates: list[Update] = await bot.get_updates(
                offset=offset, timeout=30, allowed_updates=dp.resolve_used_update_types()
            )
            for update in updates:
                offset = update.update_id + 1
                try:
                    await handle_update(update.model_dump(mode="json", exclude_none=True, by_alias=True))
                except Exception:
                    log.exception("Update %s ni qayta ishlashda xatolik", update.update_id)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
