"""Guruhga yuboriladigan murojaat kartochkasini shakllantirish."""

from datetime import datetime
from html import escape as _html_escape

from .config import config
from .texts import LANGS, category_name

CARD_TEXT_LIMIT = 2500  # kartochka ichiga sig‘adigan matn uzunligi (Telegram limiti 4096)

STATUS = {
    "new": ("🆕", "Yangi"),
    "in_progress": ("🟡", "Jarayonda"),
    "done": ("✅", "Hal qilindi"),
    "spam": ("🚫", "Spam"),
}

CATEGORY_TAGS = {
    "buy": "#xarid",
    "payment": "#tolov",
    "construction": "#qurilish",
    "tech": "#texnik",
    "complaint": "#shikoyat",
    "suggestion": "#taklif",
    "other": "#boshqa",
}

LINE = "━━━━━━━━━━━━━━━━"


def escape(value) -> str:
    return _html_escape(str(value), quote=False)


def ticket_no(ticket_id: int) -> str:
    return f"{ticket_id:04d}"


def fmt_time(ts: int) -> str:
    return datetime.fromtimestamp(ts, config.tz).strftime("%d.%m.%Y, %H:%M")


def user_link(user_id: int, username: str | None, full_name: str) -> str:
    label = f"@{escape(username)}" if username else escape(full_name)
    return f'<a href="tg://user?id={user_id}">{label}</a> · ID <code>{user_id}</code>'


def join_texts(texts: list[str]) -> str:
    return "\n\n".join(x.strip() for x in texts if x and x.strip())


def body_fits(body: str) -> bool:
    return len(body) <= CARD_TEXT_LIMIT and len(escape(body)) <= 3000


def render_card(ticket) -> str:
    emoji, status_name = STATUS.get(ticket["status"], STATUS["new"])
    no = ticket_no(ticket["id"])
    title = "YANGI MUROJAAT" if ticket["status"] == "new" else "MUROJAAT"

    lines = [
        f"{emoji} <b>{title} #{no}</b>",
        LINE,
        f"🏷 <b>Mavzu:</b> {escape(category_name(ticket['category'], 'uz'))}",
        f"👤 <b>Ism:</b> {escape(ticket['full_name'])}",
        f"📞 <b>Telefon:</b> {escape(ticket['phone'])}",
        f"✈️ <b>Telegram:</b> {user_link(ticket['user_id'], ticket['username'], ticket['full_name'])}",
        f"🌐 <b>Til:</b> {LANGS.get(ticket['lang'], ticket['lang'])}",
        f"🕒 <b>Vaqt:</b> {fmt_time(ticket['created_at'])}",
        LINE,
    ]

    body = ticket["body"]
    if body:
        fits = body_fits(body)
        shown = body if fits else body[:CARD_TEXT_LIMIT].rstrip()
        while len(escape(shown)) > 3000:  # HTML-escape matnni uzaytirib yuborishi mumkin
            shown = shown[: int(len(shown) * 0.9)].rstrip()
        if not fits:
            shown += "…"
        lines.append("💬 <b>Murojaat matni:</b>")
        lines.append(f"<blockquote expandable>{escape(shown)}</blockquote>")
        if not fits:
            lines.append("<i>Matn uzun — to‘liq varianti quyida ⬇️</i>")
    else:
        lines.append("💬 <b>Murojaat matni:</b> <i>(faqat fayl/ovozli xabar)</i>")

    if ticket["attachments"]:
        lines.append(f"📎 <b>Ilovalar:</b> {ticket['attachments']} ta — quyida ⬇️")

    status_line = f"📌 <b>Holat:</b> {emoji} {status_name}"
    if ticket["status_by"]:
        status_line += f" — {escape(ticket['status_by'])}, {fmt_time(ticket['updated_at'])}"
    lines += [LINE, status_line]

    if ticket["status"] in ("new", "in_progress"):
        lines.append("↩️ <i>Mijozga javob berish uchun shu xabarga Reply qiling.</i>")

    lines.append(f"\n#murojaat_{no} {CATEGORY_TAGS.get(ticket['category'], '#boshqa')}")
    return "\n".join(lines)
