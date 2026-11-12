"""Guruh tomoni: murojaat holatini o‘zgartirish va mijozga javob berish."""

import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramMigrateToChat
from aiogram.filters import ChatMemberUpdatedFilter, Command, JOIN_TRANSITION
from aiogram.types import CallbackQuery, ChatMemberUpdated, Message, ReactionTypeEmoji

from .. import keyboards as kb
from ..card import escape, STATUS, render_card, ticket_no
from ..config import config
from ..db import DB
from ..texts import t

log = logging.getLogger(__name__)
router = Router(name="group")
router.message.filter(F.chat.type.in_({"group", "supergroup"}))

CAPTION_TYPES = ("photo", "video", "document", "audio", "animation", "voice")


def is_work_group(chat_id: int) -> bool:
    return config.group_chat_id is not None and chat_id == config.group_chat_id


# ---------------------------------------------------------------- setup helpers

def setup_text(chat_id: int) -> str:
    if is_work_group(chat_id):
        return "✅ Bot ulandi. Yangi murojaatlar shu guruhga tushadi."
    return (
        "👋 Salom! Murojaatlarni shu guruhga yuborishim uchun <b>.env</b> fayliga quyidagini yozing:\n\n"
        f"<code>GROUP_CHAT_ID={chat_id}</code>\n\n"
        "va botni qayta ishga tushiring."
    )


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def bot_added(event: ChatMemberUpdated, bot: Bot) -> None:
    if event.chat.type not in ("group", "supergroup"):
        return
    try:
        await bot.send_message(event.chat.id, setup_text(event.chat.id))
    except TelegramMigrateToChat as e:  # guruh supergroup'ga aylangan
        await bot.send_message(e.migrate_to_chat_id, setup_text(e.migrate_to_chat_id))


@router.message(F.migrate_to_chat_id)
async def group_migrated(message: Message, bot: Bot) -> None:
    """Oddiy guruh supergroup'ga aylanganda ID o‘zgaradi — yangisini yozib beramiz."""
    new_id = message.migrate_to_chat_id
    log.warning("Guruh %s -> %s ga ko‘chdi. GROUP_CHAT_ID ni yangilang!", message.chat.id, new_id)
    await bot.send_message(new_id, setup_text(new_id))


@router.message(Command("chatid"))
async def cmd_chatid(message: Message) -> None:
    text = f"Guruh ID: <code>{message.chat.id}</code>"
    if message.message_thread_id and message.is_topic_message:
        text += f"\nMavzu (topic) ID: <code>{message.message_thread_id}</code>"
    await message.reply(text)


@router.message(Command("stats"), F.chat.func(lambda c: is_work_group(c.id)))
async def cmd_stats(message: Message, db: DB) -> None:
    s = await db.stats()
    total = sum(v for k, v in s.items() if not k.startswith("_"))
    lines = ["📊 <b>Murojaatlar statistikasi</b>\n"]
    for key, (emoji, name) in STATUS.items():
        lines.append(f"{emoji} {name}: <b>{s.get(key, 0)}</b>")
    lines.append(f"\n📥 Jami: <b>{total}</b>\n🕒 So‘nggi 24 soatda: <b>{s['_today']}</b>")
    await message.reply("\n".join(lines))


# ---------------------------------------------------------------- status buttons

async def refresh_card(bot: Bot, ticket) -> None:
    try:
        await bot.edit_message_text(
            render_card(ticket),
            chat_id=ticket["card_chat_id"],
            message_id=ticket["card_message_id"],
            reply_markup=kb.ticket_admin_kb(ticket["id"], ticket["status"]),
            disable_web_page_preview=True,
        )
    except Exception as e:  # "message is not modified" va h.k.
        log.warning("Kartochkani yangilab bo‘lmadi (ticket %s): %s", ticket["id"], e)


@router.callback_query(F.data.startswith("st:"))
async def cb_status(call: CallbackQuery, db: DB, bot: Bot) -> None:
    _, ticket_id, status = call.data.split(":")
    ticket = await db.get_ticket(int(ticket_id))
    if not ticket:
        await call.answer("Murojaat topilmadi", show_alert=True)
        return
    if ticket["status"] == status:
        await call.answer("Holat allaqachon shunday")
        return

    await db.set_status(ticket["id"], status, call.from_user.full_name)
    ticket = await db.get_ticket(ticket["id"])
    await refresh_card(bot, ticket)

    no = ticket_no(ticket["id"])
    if status in ("in_progress", "done"):
        try:
            await bot.send_message(ticket["user_id"], t(ticket["lang"], f"status_{status}", ticket=no))
        except Exception as e:
            log.warning("Mijozga holat xabarini yuborib bo‘lmadi (ticket %s): %s", no, e)

    emoji, name = STATUS[status]
    await call.answer(f"#{no}: {emoji} {name}")


# ---------------------------------------------------------------- replies to the client

@router.message(F.reply_to_message, F.chat.func(lambda c: is_work_group(c.id)))
async def admin_reply(message: Message, db: DB, bot: Bot) -> None:
    replied = message.reply_to_message
    if not replied.from_user or replied.from_user.id != bot.id:
        return
    if message.text and message.text.startswith("/"):
        return
    ticket_id = await db.ticket_by_message(message.chat.id, replied.message_id)
    ticket = await db.get_ticket(ticket_id) if ticket_id else None
    if not ticket:
        return

    lang, no = ticket["lang"], ticket_no(ticket["id"])
    header = t(lang, "admin_reply_header", ticket=no)
    hint = t(lang, "reply_hint")
    user_id = ticket["user_id"]

    try:
        if message.text:
            sent = [await bot.send_message(user_id, f"{header}\n\n{message.html_text}\n\n{hint}")]
        elif message.content_type in CAPTION_TYPES:
            caption = f"{header}\n\n{message.html_text}\n\n{hint}" if message.caption else f"{header}\n\n{hint}"
            sent = [await bot.copy_message(user_id, message.chat.id, message.message_id, caption=caption[:1024])]
        else:  # stiker, video-xabar va h.k.
            head = await bot.send_message(user_id, f"{header}\n\n{hint}")
            copied = await bot.copy_message(user_id, message.chat.id, message.message_id)
            sent = [head, copied]
    except Exception as e:
        log.warning("Javobni mijozga yuborib bo‘lmadi (ticket %s): %s", no, e)
        await message.reply(
            "⚠️ Javob mijozga yetkazilmadi — ehtimol, u botni bloklagan.\n"
            f"Telefon orqali bog‘laning: {escape(ticket['phone'])}"
        )
        return

    for m in sent:
        await db.link(user_id, m.message_id, ticket["id"])
    await db.link(message.chat.id, message.message_id, ticket["id"])

    # Birinchi javobda murojaat avtomatik "Jarayonda" holatiga o‘tadi
    if ticket["status"] == "new":
        await db.set_status(ticket["id"], "in_progress", message.from_user.full_name)
        await refresh_card(bot, await db.get_ticket(ticket["id"]))

    try:
        await message.react([ReactionTypeEmoji(emoji="👍")])
    except Exception:
        await message.reply(f"✅ Javob mijozga yuborildi (#{no}).")
