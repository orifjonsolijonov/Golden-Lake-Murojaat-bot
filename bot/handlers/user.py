"""Foydalanuvchi (shaxsiy chat) tomoni: menyu va murojaat yuborish oqimi."""

import asyncio
import logging
import time
from collections import defaultdict

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramMigrateToChat, TelegramRetryAfter
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ReplyParameters

from .. import keyboards as kb
from ..card import escape, body_fits, join_texts, render_card, ticket_no
from ..config import config
from ..db import DB
from ..texts import all_variants, category_name, t

log = logging.getLogger(__name__)
router = Router(name="user")
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")

MAX_PARTS = 10          # bitta murojaatdagi xabarlar soni
COOLDOWN_SEC = 30       # ketma-ket murojaatlar orasidagi minimal vaqt
_locks: defaultdict[int, asyncio.Lock] = defaultdict(asyncio.Lock)


class Form(StatesGroup):
    category = State()
    collect = State()
    confirm = State()


# ---------------------------------------------------------------- helpers

async def get_lang(db: DB, user_id: int) -> str:
    return await db.get_lang(user_id) or "uz"


def message_text(msg: Message) -> str:
    return msg.text or msg.caption or ""


async def show_menu(message: Message, lang: str, key: str = "menu") -> None:
    await message.answer(t(lang, key), reply_markup=kb.main_menu(lang))


async def ask_message_step(message: Message, state: FSMContext, lang: str) -> None:
    await state.update_data(parts=[], last_album=None)
    await state.set_state(Form.collect)
    await message.answer(t(lang, "ask_message"), reply_markup=kb.collect_kb(lang))


# ---------------------------------------------------------------- start / menu

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db: DB) -> None:
    await state.clear()
    user = message.from_user
    await db.upsert_user(user.id, user.username)
    lang = await db.get_lang(user.id)
    if not lang:
        await message.answer(t("uz", "choose_lang"), reply_markup=kb.lang_kb())
        return
    await message.answer(t(lang, "welcome", name=escape(user.first_name or "")), reply_markup=kb.main_menu(lang))


@router.callback_query(F.data.startswith("lang:"))
async def cb_lang(call: CallbackQuery, state: FSMContext, db: DB) -> None:
    lang = call.data.split(":", 1)[1]
    first_time = not await db.get_lang(call.from_user.id)
    await db.upsert_user(call.from_user.id, call.from_user.username, lang=lang)
    await state.clear()
    await call.message.delete()
    if first_time:
        await call.message.answer(
            t(lang, "welcome", name=escape(call.from_user.first_name or "")), reply_markup=kb.main_menu(lang)
        )
    else:
        await show_menu(call.message, lang)
    await call.answer()


@router.message(F.text.in_(all_variants("btn_lang")))
async def btn_lang(message: Message) -> None:
    await message.answer(t("uz", "choose_lang"), reply_markup=kb.lang_kb())


@router.message(F.text.in_(all_variants("btn_contacts")))
async def btn_contacts(message: Message, db: DB) -> None:
    await message.answer(t(await get_lang(db, message.from_user.id), "contacts"), disable_web_page_preview=True)


@router.message(Command("cancel"))
@router.message(F.text.in_(all_variants("btn_cancel")))
async def btn_cancel(message: Message, state: FSMContext, db: DB) -> None:
    await state.clear()
    await show_menu(message, await get_lang(db, message.from_user.id), "cancelled")


@router.callback_query(F.data == "flow:cancel")
async def cb_cancel(call: CallbackQuery, state: FSMContext, db: DB) -> None:
    await state.clear()
    await call.message.delete()
    await show_menu(call.message, await get_lang(db, call.from_user.id), "cancelled")
    await call.answer()


# ---------------------------------------------------------------- 1. mavzu

@router.message(Command("new"))
@router.message(F.text.in_(all_variants("btn_new")))
async def btn_new(message: Message, state: FSMContext, db: DB) -> None:
    user = message.from_user
    await db.upsert_user(user.id, user.username)
    lang = await get_lang(db, user.id)

    last = await db.last_ticket_time(user.id)
    if last and time.time() - last < COOLDOWN_SEC:
        await message.answer(t(lang, "too_fast", sec=int(COOLDOWN_SEC - (time.time() - last)) + 1))
        return

    await state.clear()
    await state.set_state(Form.category)
    await message.answer(t(lang, "ask_category"), reply_markup=kb.category_kb(lang))


@router.callback_query(Form.category, F.data.startswith("cat:"))
async def cb_category(call: CallbackQuery, state: FSMContext, db: DB) -> None:
    lang = await get_lang(db, call.from_user.id)
    category = call.data.split(":", 1)[1]
    await state.update_data(category=category)
    await call.message.edit_text(f"{t(lang, 'ask_category')}\n\n✔️ <b>{escape(category_name(category, lang))}</b>")
    await call.answer()
    await ask_message_step(call.message, state, lang)


# ---------------------------------------------------------------- 2. murojaat matni

@router.message(StateFilter(Form.collect, Form.confirm), F.text.in_(all_variants("btn_done")))
async def step_done(message: Message, state: FSMContext, db: DB) -> None:
    lang = await get_lang(db, message.from_user.id)
    async with _locks[message.from_user.id]:
        data = await state.get_data()
    parts = data.get("parts", [])
    if not parts:
        await message.answer(t(lang, "msg_empty"))
        return

    text = join_texts([p["text"] for p in parts])
    files = sum(1 for p in parts if p["kind"] != "text")
    preview = ""
    if text:
        short = text if len(text) <= 300 else text[:300].rstrip() + "…"
        preview += f"<blockquote>{escape(short)}</blockquote>\n"
    if files:
        preview += t(lang, "files_count", count=files) + "\n"

    await state.set_state(Form.confirm)
    await message.answer(
        t(
            lang,
            "confirm",
            category=escape(category_name(data["category"], lang)),
            preview=preview,
        ),
        reply_markup=kb.confirm_kb(lang),
    )


SUPPORTED = (
    F.text | F.photo | F.video | F.document | F.voice | F.audio | F.video_note | F.animation | F.location
)


@router.message(StateFilter(Form.collect, Form.confirm), SUPPORTED)
async def step_collect(message: Message, state: FSMContext, db: DB) -> None:
    lang = await get_lang(db, message.from_user.id)
    if message.text and message.text.startswith("/"):
        await message.answer(t(lang, "msg_unsupported"))
        return

    # Albom (bir nechta rasm) bir vaqtda keladi — holatni ketma-ket yangilash uchun lock
    async with _locks[message.from_user.id]:
        data = await state.get_data()
        parts = data.get("parts", [])
        album = message.media_group_id
        if len(parts) >= MAX_PARTS:
            if not album or album != data.get("last_album"):
                await message.answer(t(lang, "msg_limit", max=MAX_PARTS))
            return
        parts.append(
            {"id": message.message_id, "kind": "text" if message.text else "media", "text": message_text(message)}
        )
        same_album = album is not None and album == data.get("last_album")
        await state.update_data(parts=parts, last_album=album)
        await state.set_state(Form.collect)

    if not same_album:
        await message.answer(
            t(lang, "msg_added", count=len(parts), max=MAX_PARTS), reply_markup=kb.collect_kb(lang)
        )


@router.message(StateFilter(Form.collect, Form.confirm))
async def step_collect_unsupported(message: Message, db: DB) -> None:
    await message.answer(t(await get_lang(db, message.from_user.id), "msg_unsupported"))


# ---------------------------------------------------------------- confirm & send

@router.callback_query(Form.confirm, F.data.startswith("confirm:"))
async def cb_confirm(call: CallbackQuery, state: FSMContext, db: DB, bot: Bot) -> None:
    lang = await get_lang(db, call.from_user.id)
    action = call.data.split(":", 1)[1]

    if action == "cancel":
        await state.clear()
        await call.message.edit_reply_markup(reply_markup=None)
        await show_menu(call.message, lang, "cancelled")
        await call.answer()
        return

    if action == "edit":
        await state.clear()
        await state.set_state(Form.category)
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(t(lang, "ask_category"), reply_markup=kb.category_kb(lang))
        await call.answer()
        return

    # action == "send": ikki marta bosilishdan himoya
    async with _locks[call.from_user.id]:
        if await state.get_state() != Form.confirm.state:
            await call.answer()
            return
        data = await state.get_data()
        await state.clear()

    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer()

    ticket_id = await submit_ticket(bot, db, call.from_user, data, lang)
    if ticket_id is None:
        await show_menu(call.message, lang, "send_failed")
        return
    await call.message.answer(t(lang, "sent", ticket=ticket_no(ticket_id)), reply_markup=kb.main_menu(lang))


async def submit_ticket(bot: Bot, db: DB, user, data: dict, lang: str) -> int | None:
    """Murojaatni bazaga yozadi va guruhga yuboradi. Xatolik bo‘lsa None."""
    if not config.group_chat_id:
        log.error("GROUP_CHAT_ID sozlanmagan — murojaat guruhga yuborilmadi")
        return None

    parts = data["parts"]
    text_parts = [p for p in parts if p["kind"] == "text"]
    media_parts = [p for p in parts if p["kind"] != "text"]
    body = join_texts([p["text"] for p in text_parts])

    ticket_id = await db.create_ticket(
        user_id=user.id,
        category=data["category"],
        lang=lang,
        body=body,
        attachments=len(media_parts),
    )
    ticket = await db.get_ticket(ticket_id)
    chat_id = config.group_chat_id

    async def send_card(target: int):
        return await bot.send_message(
            target,
            render_card(ticket),
            message_thread_id=config.group_thread_id,
            reply_markup=kb.ticket_admin_kb(ticket_id, "new"),
            disable_web_page_preview=True,
        )

    try:
        try:
            card = await send_card(chat_id)
        except TelegramMigrateToChat as e:
            log.error("Guruh supergroup'ga aylangan! .env da GROUP_CHAT_ID=%s qilib qo‘ying", e.migrate_to_chat_id)
            chat_id = e.migrate_to_chat_id
            card = await send_card(chat_id)
    except Exception:
        log.exception("Kartochkani guruhga yuborib bo‘lmadi (ticket %s)", ticket_id)
        await db.delete_ticket(ticket_id)
        return None

    await db.set_card(ticket_id, chat_id, card.message_id)
    await db.link(chat_id, card.message_id, ticket_id)

    # Matn kartochkaga sig‘masa — matnli xabarlar ham, fayllar esa har doim reply sifatida
    to_copy = media_parts if body_fits(body) else parts
    reply_to = ReplyParameters(message_id=card.message_id, allow_sending_without_reply=True)
    for part in to_copy:
        try:
            try:
                copied = await bot.copy_message(chat_id, user.id, part["id"], reply_parameters=reply_to)
            except TelegramRetryAfter as e:  # Telegram "sekinroq" desa — kutib, qayta urinamiz
                await asyncio.sleep(min(e.retry_after, 15))
                copied = await bot.copy_message(chat_id, user.id, part["id"], reply_parameters=reply_to)
            await db.link(chat_id, copied.message_id, ticket_id)
        except Exception:
            log.exception("Ilovani nusxalab bo‘lmadi (ticket %s, msg %s)", ticket_id, part["id"])
        await asyncio.sleep(0.35)  # guruhga flood-limitdan saqlanish
    return ticket_id


# ---------------------------------------------------------------- idle messages

@router.callback_query(F.data.startswith("cat:"))
@router.callback_query(F.data.startswith("confirm:"))
async def cb_stale(call: CallbackQuery, db: DB) -> None:
    """Eski xabardagi tugma bosilganda (holat mos kelmasa)."""
    await call.answer(t(await get_lang(db, call.from_user.id), "session_expired"), show_alert=True)


@router.message(F.reply_to_message)
async def user_followup(message: Message, db: DB, bot: Bot) -> None:
    """Foydalanuvchi xodim javobiga Reply qilsa — xabar guruhdagi murojaatga qo‘shiladi."""
    lang = await get_lang(db, message.from_user.id)
    ticket_id = await db.ticket_by_message(message.chat.id, message.reply_to_message.message_id)
    ticket = await db.get_ticket(ticket_id) if ticket_id else None
    if not ticket or not ticket["card_message_id"]:
        await show_menu(message, lang, "use_menu")
        return

    chat_id, card_id = ticket["card_chat_id"], ticket["card_message_id"]
    no = ticket_no(ticket_id)
    header = f"📩 <b>Mijozdan qo‘shimcha xabar — #{no}</b>"
    reply_to = ReplyParameters(message_id=card_id, allow_sending_without_reply=True)
    try:
        if message.text:
            sent = await bot.send_message(
                chat_id, f"{header}\n\n<blockquote>{escape(message.text)}</blockquote>", reply_parameters=reply_to
            )
            await db.link(chat_id, sent.message_id, ticket_id)
        else:
            head = await bot.send_message(chat_id, header, reply_parameters=reply_to)
            await db.link(chat_id, head.message_id, ticket_id)
            copied = await bot.copy_message(
                chat_id, message.chat.id, message.message_id,
                reply_parameters=ReplyParameters(message_id=head.message_id, allow_sending_without_reply=True),
            )
            await db.link(chat_id, copied.message_id, ticket_id)
    except Exception:
        log.exception("Qo‘shimcha xabarni guruhga yuborib bo‘lmadi (ticket %s)", ticket_id)
        await message.answer(t(lang, "send_failed"))
        return
    await message.answer(t(lang, "followup_sent", ticket=no))

    # Hal qilingan murojaatga mijoz yana yozsa — murojaat qayta ochiladi
    if ticket["status"] == "done":
        from .group import refresh_card

        await db.set_status(ticket_id, "new", "mijoz qayta yozdi")
        await refresh_card(bot, await db.get_ticket(ticket_id))


@router.message()
async def fallback(message: Message, db: DB) -> None:
    user = message.from_user
    await db.upsert_user(user.id, user.username)
    lang = await db.get_lang(user.id)
    if not lang:
        await message.answer(t("uz", "choose_lang"), reply_markup=kb.lang_kb())
        return
    await show_menu(message, lang, "use_menu")
