from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from .texts import CATEGORIES, LANGS, t


def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=name, callback_data=f"lang:{code}") for code, name in LANGS.items()]]
    )


def main_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "btn_new"))],
            [KeyboardButton(text=t(lang, "btn_about")), KeyboardButton(text=t(lang, "btn_contacts"))],
            [KeyboardButton(text=t(lang, "btn_lang"))],
        ],
        resize_keyboard=True,
    )


def cancel_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t(lang, "btn_cancel"))]], resize_keyboard=True)


def category_kb(lang: str) -> InlineKeyboardMarkup:
    idx = 1 if lang == "ru" else 0
    keys = list(CATEGORIES)
    rows = [
        [InlineKeyboardButton(text=CATEGORIES[k][idx], callback_data=f"cat:{k}") for k in keys[i : i + 2]]
        for i in range(0, len(keys), 2)
    ]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="flow:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def saved_profile_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_use_saved"), callback_data="saved:yes")],
            [InlineKeyboardButton(text=t(lang, "btn_change_saved"), callback_data="saved:no")],
        ]
    )


def name_kb(lang: str, tg_name: str | None) -> ReplyKeyboardMarkup:
    rows = []
    if tg_name:
        rows.append([KeyboardButton(text=tg_name[:64])])
    rows.append([KeyboardButton(text=t(lang, "btn_cancel"))])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def phone_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "btn_share_phone"), request_contact=True)],
            [KeyboardButton(text=t(lang, "btn_cancel"))],
        ],
        resize_keyboard=True,
    )


def collect_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "btn_done"))], [KeyboardButton(text=t(lang, "btn_cancel"))]],
        resize_keyboard=True,
    )


def confirm_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_send"), callback_data="confirm:send")],
            [
                InlineKeyboardButton(text=t(lang, "btn_edit"), callback_data="confirm:edit"),
                InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="confirm:cancel"),
            ],
        ]
    )


def ticket_admin_kb(ticket_id: int, status: str) -> InlineKeyboardMarkup:
    buttons = []
    if status != "in_progress":
        buttons.append(InlineKeyboardButton(text="🟡 Jarayonda", callback_data=f"st:{ticket_id}:in_progress"))
    if status != "done":
        buttons.append(InlineKeyboardButton(text="✅ Hal qilindi", callback_data=f"st:{ticket_id}:done"))
    rows = [buttons] if buttons else []
    if status not in ("spam", "done"):
        rows.append([InlineKeyboardButton(text="🚫 Spam", callback_data=f"st:{ticket_id}:spam")])
    if status in ("done", "spam"):
        rows.append([InlineKeyboardButton(text="↩️ Qayta ochish", callback_data=f"st:{ticket_id}:new")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
