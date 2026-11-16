"""Barcha foydalanuvchi matnlari (o‘zbekcha / ruscha).

Matnlar HTML formatida (parse_mode=HTML). Tugma matnlarini o‘zgartirsangiz,
handlerlar avtomatik ravishda yangisini taniydi — ular shu fayldan olinadi.
"""

PHONE = "+998 55 515-44-44"
SITE = "goldenlake.uz"
EMAIL = "info@goldenlake.uz"
ADMIN = "@goldenlake_admin"

LANGS = {"uz": "🇺🇿 O‘zbekcha", "ru": "🇷🇺 Русский"}

# Murojaat turlari: kalit -> (uz, ru)
CATEGORIES: dict[str, tuple[str, str]] = {
    "payment": ("📄 Shartnoma va to‘lovlar", "📄 Договор и оплата"),
    "construction": ("🏗 Qurilish jarayoni", "🏗 Ход строительства"),
    "tech": ("🛠 Texnik masala", "🛠 Технический вопрос"),
    "suggestion": ("💡 Taklif", "💡 Предложение"),
    "other": ("❓ Boshqa savol", "❓ Другой вопрос"),
}


# Menyudan olib tashlangan mavzular — eski murojaatlar to‘g‘ri ko‘rinishi uchun
_OLD_CATEGORIES = {
    "buy": ("🏠 Xonadon xarid qilish", "🏠 Покупка квартиры"),
    "complaint": ("😔 Shikoyat", "😔 Жалоба"),
}


def category_name(key: str, lang: str = "uz") -> str:
    uz, ru = CATEGORIES.get(key) or _OLD_CATEGORIES.get(key) or CATEGORIES["other"]
    return ru if lang == "ru" else uz


T: dict[str, dict[str, str]] = {
    "uz": {
        # --- Tugmalar ---
        "btn_new": "✍️ Murojaat yuborish",
        "btn_contacts": "📞 Bog‘lanish",
        "btn_lang": "🌐 Tilni o‘zgartirish",
        "btn_cancel": "❌ Bekor qilish",
        "btn_done": "✅ Tayyor",
        "btn_send": "📨 Yuborish",
        "btn_edit": "✏️ Qaytadan yozish",

        # --- Asosiy ---
        "choose_lang": "Assalomu alaykum! Tilni tanlang 👇\n\nЗдравствуйте! Выберите язык 👇",
        "welcome": (
            "Assalomu alaykum, <b>{name}</b>! 👋\n\n"
            "Bu — <b>Golden Lake</b> murojaatlar boti. Savol, taklif yoki muammongizni yozing — "
            "javob shu yerga keladi.\n\n"
            "🔒 Murojaat <b>anonim</b>: ism va telefon so‘ralmaydi.\n\n"
            "Boshlash uchun <b>«✍️ Murojaat yuborish»</b> tugmasini bosing."
        ),
        "menu": "Asosiy menyu 👇",
        "use_menu": "Yangi murojaat uchun <b>«✍️ Murojaat yuborish»</b> tugmasini bosing 👇",
        "cancelled": "Murojaat bekor qilindi.",
        "contacts": (
            "📞 <b>Bog‘lanish</b>\n\n"
            "👤 Administrator: {admin}"
        ),

        # --- Murojaat oqimi ---
        "ask_category": "<b>1/2.</b> Murojaat mavzusini tanlang 👇",
        "ask_message": (
            "<b>2/2.</b> Murojaatingizni yozing ✍️\n\n"
            "Rasm, video, fayl yoki ovozli xabar ham yuborishingiz mumkin. "
            "Tugatgach, <b>«✅ Tayyor»</b> ni bosing."
        ),
        "msg_added": "✔️ Qo‘shildi ({count}/{max}). Yana yozing yoki <b>«✅ Tayyor»</b> ni bosing.",
        "msg_limit": "Ko‘pi bilan {max} ta xabar qo‘shish mumkin. <b>«✅ Tayyor»</b> ni bosing.",
        "msg_unsupported": "Bu turdagi xabar qabul qilinmaydi. Matn, rasm, video, fayl yoki ovozli xabar yuboring.",
        "files_count": "📎 Fayllar: {count} ta",
        "msg_empty": "Avval murojaatingizni yozing yoki fayl yuboring ✍️",
        "confirm": (
            "📋 <b>Murojaatingiz:</b>\n\n"
            "🏷 {category}\n"
            "{preview}\n"
            "Yuboramizmi?"
        ),
        "sent": (
            "✅ <b>Murojaatingiz yuborildi!</b> Raqami: <b>#{ticket}</b>\n\n"
            "Javob shu botga keladi."
        ),
        "send_failed": "😔 Texnik nosozlik tufayli yuborilmadi. Birozdan so‘ng qayta urinib ko‘ring.",
        "too_fast": "Yangi murojaat uchun {sec} soniya kuting, iltimos.",
        "session_expired": "Bu murojaat eskirgan. Iltimos, qaytadan boshlang.",

        # --- Javoblar ---
        "admin_reply_header": "💬 <b>Golden Lake</b> mas’ul xodimi javobi — murojaat <b>#{ticket}</b>:",
        "reply_hint": "<i>Javob yozish uchun ushbu xabarga «Reply» (Ответить) qiling.</i>",
        "followup_sent": "✔️ Xabaringiz <b>#{ticket}</b> murojaatga qo‘shildi va xodimga yuborildi.",
        "status_in_progress": "🟡 Murojaatingiz <b>#{ticket}</b> ko‘rib chiqilmoqda. Tez orada javob beramiz.",
        "status_done": "✅ Murojaatingiz <b>#{ticket}</b> hal qilindi.\n\nGolden Lake’ni tanlaganingiz uchun rahmat! Yana savol bo‘lsa — bemalol yozing.",
    },
    "ru": {
        "btn_new": "✍️ Оставить обращение",
        "btn_contacts": "📞 Контакты",
        "btn_lang": "🌐 Сменить язык",
        "btn_cancel": "❌ Отменить",
        "btn_done": "✅ Готово",
        "btn_send": "📨 Отправить",
        "btn_edit": "✏️ Написать заново",

        "choose_lang": "Assalomu alaykum! Tilni tanlang 👇\n\nЗдравствуйте! Выберите язык 👇",
        "welcome": (
            "Здравствуйте, <b>{name}</b>! 👋\n\n"
            "Это бот обращений <b>Golden Lake</b>. Напишите вопрос, предложение или проблему — "
            "ответ придёт сюда.\n\n"
            "🔒 Обращение <b>анонимное</b>: имя и телефон не нужны.\n\n"
            "Чтобы начать, нажмите <b>«✍️ Оставить обращение»</b>."
        ),
        "menu": "Главное меню 👇",
        "use_menu": "Для нового обращения нажмите <b>«✍️ Оставить обращение»</b> 👇",
        "cancelled": "Обращение отменено.",
        "contacts": (
            "📞 <b>Контакты</b>\n\n"
            "👤 Администратор: {admin}"
        ),

        "ask_category": "<b>1/2.</b> Выберите тему обращения 👇",
        "ask_message": (
            "<b>2/2.</b> Напишите ваше обращение ✍️\n\n"
            "Можно также отправить фото, видео, файл или голосовое. "
            "Когда закончите, нажмите <b>«✅ Готово»</b>."
        ),
        "msg_added": "✔️ Добавлено ({count}/{max}). Напишите ещё или нажмите <b>«✅ Готово»</b>.",
        "msg_limit": "Можно добавить не более {max} сообщений. Нажмите <b>«✅ Готово»</b>.",
        "msg_unsupported": "Этот тип сообщения не поддерживается. Отправьте текст, фото, видео, файл или голосовое.",
        "files_count": "📎 Файлов: {count}",
        "msg_empty": "Сначала напишите обращение или отправьте файл ✍️",
        "confirm": (
            "📋 <b>Ваше обращение:</b>\n\n"
            "🏷 {category}\n"
            "{preview}\n"
            "Отправляем?"
        ),
        "sent": (
            "✅ <b>Обращение отправлено!</b> Номер: <b>#{ticket}</b>\n\n"
            "Ответ придёт в этот бот."
        ),
        "send_failed": "😔 Из-за технической ошибки не отправлено. Попробуйте чуть позже.",
        "too_fast": "Подождите {sec} сек. перед новым обращением, пожалуйста.",
        "session_expired": "Это обращение устарело. Пожалуйста, начните заново.",

        "admin_reply_header": "💬 Ответ сотрудника <b>Golden Lake</b> — обращение <b>#{ticket}</b>:",
        "reply_hint": "<i>Чтобы ответить, нажмите «Ответить» (Reply) на это сообщение.</i>",
        "followup_sent": "✔️ Ваше сообщение добавлено к обращению <b>#{ticket}</b> и передано сотруднику.",
        "status_in_progress": "🟡 Ваше обращение <b>#{ticket}</b> на рассмотрении. Скоро ответим.",
        "status_done": "✅ Ваше обращение <b>#{ticket}</b> решено.\n\nСпасибо, что выбрали Golden Lake! Если появятся вопросы — пишите.",
    },
}


def t(lang: str | None, key: str, **kwargs) -> str:
    lang = lang if lang in T else "uz"
    text = T[lang].get(key) or T["uz"][key]
    kwargs.setdefault("phone", PHONE)
    kwargs.setdefault("site", SITE)
    kwargs.setdefault("email", EMAIL)
    kwargs.setdefault("admin", ADMIN)
    return text.format(**kwargs) if kwargs else text


def all_variants(key: str) -> set[str]:
    """Tugma matnining barcha tillardagi variantlari (handler filtrlari uchun)."""
    return {T[lang][key] for lang in T}
