"""Barcha foydalanuvchi matnlari (o‘zbekcha / ruscha).

Matnlar HTML formatida (parse_mode=HTML). Tugma matnlarini o‘zgartirsangiz,
handlerlar avtomatik ravishda yangisini taniydi — ular shu fayldan olinadi.
"""

PHONE = "+998 55 515-44-44"
SITE = "goldenlake.uz"
EMAIL = "info@goldenlake.uz"

LANGS = {"uz": "🇺🇿 O‘zbekcha", "ru": "🇷🇺 Русский"}

# Murojaat turlari: kalit -> (uz, ru)
CATEGORIES: dict[str, tuple[str, str]] = {
    "buy": ("🏠 Xonadon xarid qilish", "🏠 Покупка квартиры"),
    "payment": ("📄 Shartnoma va to‘lovlar", "📄 Договор и оплата"),
    "construction": ("🏗 Qurilish jarayoni", "🏗 Ход строительства"),
    "tech": ("🛠 Texnik masala", "🛠 Технический вопрос"),
    "complaint": ("😔 Shikoyat", "😔 Жалоба"),
    "suggestion": ("💡 Taklif", "💡 Предложение"),
    "other": ("❓ Boshqa savol", "❓ Другой вопрос"),
}


def category_name(key: str, lang: str = "uz") -> str:
    uz, ru = CATEGORIES.get(key, CATEGORIES["other"])
    return ru if lang == "ru" else uz


T: dict[str, dict[str, str]] = {
    "uz": {
        # --- Tugmalar ---
        "btn_new": "✍️ Murojaat yuborish",
        "btn_contacts": "📞 Bog‘lanish",
        "btn_lang": "🌐 Tilni o‘zgartirish",
        "btn_cancel": "❌ Bekor qilish",
        "btn_back": "⬅️ Orqaga",
        "btn_share_phone": "📱 Raqamni yuborish",
        "btn_done": "✅ Tayyor",
        "btn_send": "📨 Yuborish",
        "btn_edit": "✏️ Qaytadan to‘ldirish",
        "btn_use_saved": "✅ Ha, shu ma’lumotlar bilan",
        "btn_change_saved": "✏️ O‘zgartirish",

        # --- Asosiy ---
        "choose_lang": "Assalomu alaykum! Tilni tanlang 👇\n\nЗдравствуйте! Выберите язык 👇",
        "welcome": (
            "Assalomu alaykum, <b>{name}</b>! 👋\n\n"
            "Bu — <b>Golden Lake</b> turar-joy majmuasining rasmiy murojaatlar boti "
            "(quruvchi: Centris Development).\n\n"
            "Bu yerda siz:\n"
            "• xonadon xarid qilish bo‘yicha savol berishingiz,\n"
            "• shartnoma, to‘lov yoki qurilish jarayoni haqida so‘rashingiz,\n"
            "• shikoyat yoki taklif qoldirishingiz mumkin.\n\n"
            "Har bir murojaat mas’ul xodimlarimizga darhol yetkaziladi va "
            "javob shu bot orqali sizga keladi. 📩\n\n"
            "Boshlash uchun <b>«✍️ Murojaat yuborish»</b> tugmasini bosing."
        ),
        "menu": "Asosiy menyu. Kerakli bo‘limni tanlang 👇",
        "use_menu": "Iltimos, quyidagi menyudan foydalaning 👇\n\nYangi murojaat uchun <b>«✍️ Murojaat yuborish»</b> tugmasini bosing.",
        "cancelled": "Murojaat bekor qilindi. Istalgan vaqtda qaytadan yuborishingiz mumkin.",
        "contacts": (
            "📞 <b>Bog‘lanish</b>\n\n"
            "☎️ Telefon: <b>{phone}</b>\n"
            "🌐 Sayt: {site}\n"
            "✉️ Email: {email}\n"
            "📍 Sotuv ofisi: Toshkent sh., Oltinko‘l ko‘chasi, 109\n\n"
            "Yozma murojaat qoldirmoqchi bo‘lsangiz — <b>«✍️ Murojaat yuborish»</b> tugmasini bosing."
        ),

        # --- Murojaat oqimi ---
        "ask_category": "<b>1/4.</b> Murojaatingiz qaysi mavzuda? 👇",
        "use_saved": (
            "Oldingi murojaatingizdagi ma’lumotlar:\n\n"
            "👤 {name}\n📞 {phone}\n\n"
            "Shu ma’lumotlar bilan davom etamizmi?"
        ),
        "ask_name": (
            "<b>2/4.</b> Ismingiz va familiyangizni yozing.\n\n"
            "<i>Masalan: Aziz Karimov</i>"
        ),
        "bad_name": "Iltimos, ismingizni matn ko‘rinishida yozing (2–64 belgi).",
        "ask_phone": (
            "<b>3/4.</b> Siz bilan bog‘lanish uchun telefon raqamingiz.\n\n"
            "Pastdagi <b>«📱 Raqamni yuborish»</b> tugmasini bosing yoki raqamni yozing.\n"
            "<i>Masalan: +998 90 123 45 67</i>"
        ),
        "bad_phone": "Raqam noto‘g‘ri ko‘rinadi. Iltimos, <b>+998 90 123 45 67</b> ko‘rinishida yozing yoki tugma orqali yuboring.",
        "ask_message": (
            "<b>4/4.</b> Endi murojaatingizni batafsil yozing. ✍️\n\n"
            "Matn bilan birga <b>rasm, video, hujjat yoki ovozli xabar</b> ham yuborishingiz mumkin. "
            "Bir nechta xabar yuborsangiz — barchasi bitta murojaatga qo‘shiladi.\n\n"
            "Tugatgach, <b>«✅ Tayyor»</b> tugmasini bosing."
        ),
        "msg_added": "✔️ Qo‘shildi ({count}/{max}). Yana qo‘shishingiz yoki <b>«✅ Tayyor»</b> tugmasini bosishingiz mumkin.",
        "msg_limit": "Bitta murojaatga ko‘pi bilan {max} ta xabar qo‘shish mumkin. <b>«✅ Tayyor»</b> tugmasini bosing.",
        "msg_unsupported": "Bu turdagi xabarni qabul qila olmayman. Iltimos, matn, rasm, video, hujjat yoki ovozli xabar yuboring.",
        "files_count": "📎 Fayllar: {count} ta",
        "msg_empty": "Avval murojaatingiz matnini yozing yoki fayl yuboring. ✍️",
        "confirm": (
            "📋 <b>Murojaatingizni tekshiring:</b>\n\n"
            "🏷 <b>Mavzu:</b> {category}\n"
            "👤 <b>Ism:</b> {name}\n"
            "📞 <b>Telefon:</b> {phone}\n"
            "💬 <b>Xabarlar:</b> {count} ta\n"
            "{preview}\n"
            "Hammasi to‘g‘rimi? <b>«📨 Yuborish»</b> tugmasini bosing."
        ),
        "sent": (
            "✅ <b>Murojaatingiz qabul qilindi!</b>\n\n"
            "📌 Murojaat raqami: <b>#{ticket}</b>\n\n"
            "Mas’ul xodimimiz murojaatingizni ko‘rib chiqib, tez orada shu bot orqali "
            "yoki telefon orqali siz bilan bog‘lanadi.\n\n"
            "Shoshilinch holatda: <b>{phone}</b>"
        ),
        "send_failed": (
            "😔 Kechirasiz, texnik nosozlik tufayli murojaat yuborilmadi.\n\n"
            "Iltimos, birozdan so‘ng qayta urinib ko‘ring yoki <b>{phone}</b> raqamiga qo‘ng‘iroq qiling."
        ),
        "too_fast": "Siz hozirgina murojaat yubordingiz. Yangi murojaat uchun {sec} soniya kuting, iltimos.",
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
        "btn_back": "⬅️ Назад",
        "btn_share_phone": "📱 Отправить номер",
        "btn_done": "✅ Готово",
        "btn_send": "📨 Отправить",
        "btn_edit": "✏️ Заполнить заново",
        "btn_use_saved": "✅ Да, с этими данными",
        "btn_change_saved": "✏️ Изменить",

        "choose_lang": "Assalomu alaykum! Tilni tanlang 👇\n\nЗдравствуйте! Выберите язык 👇",
        "welcome": (
            "Здравствуйте, <b>{name}</b>! 👋\n\n"
            "Это официальный бот обращений жилого комплекса <b>Golden Lake</b> "
            "(застройщик — Centris Development).\n\n"
            "Здесь вы можете:\n"
            "• задать вопрос о покупке квартиры,\n"
            "• уточнить информацию по договору, оплате или ходу строительства,\n"
            "• оставить жалобу или предложение.\n\n"
            "Каждое обращение сразу передаётся ответственным сотрудникам, "
            "а ответ придёт вам прямо в этот бот. 📩\n\n"
            "Чтобы начать, нажмите <b>«✍️ Оставить обращение»</b>."
        ),
        "menu": "Главное меню. Выберите раздел 👇",
        "use_menu": "Пожалуйста, воспользуйтесь меню ниже 👇\n\nДля нового обращения нажмите <b>«✍️ Оставить обращение»</b>.",
        "cancelled": "Обращение отменено. Вы можете отправить его заново в любое время.",
        "contacts": (
            "📞 <b>Контакты</b>\n\n"
            "☎️ Телефон: <b>{phone}</b>\n"
            "🌐 Сайт: {site}\n"
            "✉️ Email: {email}\n"
            "📍 Офис продаж: г. Ташкент, ул. Алтынкуль, 109\n\n"
            "Чтобы оставить письменное обращение, нажмите <b>«✍️ Оставить обращение»</b>."
        ),

        "ask_category": "<b>1/4.</b> Какая тема вашего обращения? 👇",
        "use_saved": (
            "Данные из вашего прошлого обращения:\n\n"
            "👤 {name}\n📞 {phone}\n\n"
            "Продолжим с этими данными?"
        ),
        "ask_name": (
            "<b>2/4.</b> Напишите ваше имя и фамилию.\n\n"
            "<i>Например: Азиз Каримов</i>"
        ),
        "bad_name": "Пожалуйста, напишите имя текстом (2–64 символа).",
        "ask_phone": (
            "<b>3/4.</b> Номер телефона для связи с вами.\n\n"
            "Нажмите кнопку <b>«📱 Отправить номер»</b> ниже или напишите номер.\n"
            "<i>Например: +998 90 123 45 67</i>"
        ),
        "bad_phone": "Номер выглядит некорректно. Напишите его в формате <b>+998 90 123 45 67</b> или отправьте кнопкой.",
        "ask_message": (
            "<b>4/4.</b> Теперь подробно опишите ваше обращение. ✍️\n\n"
            "Вместе с текстом можно отправить <b>фото, видео, документ или голосовое сообщение</b>. "
            "Если отправите несколько сообщений — все они попадут в одно обращение.\n\n"
            "Когда закончите, нажмите <b>«✅ Готово»</b>."
        ),
        "msg_added": "✔️ Добавлено ({count}/{max}). Можете добавить ещё или нажать <b>«✅ Готово»</b>.",
        "msg_limit": "В одно обращение можно добавить не более {max} сообщений. Нажмите <b>«✅ Готово»</b>.",
        "msg_unsupported": "Этот тип сообщения не поддерживается. Отправьте текст, фото, видео, документ или голосовое.",
        "files_count": "📎 Файлов: {count}",
        "msg_empty": "Сначала напишите текст обращения или отправьте файл. ✍️",
        "confirm": (
            "📋 <b>Проверьте ваше обращение:</b>\n\n"
            "🏷 <b>Тема:</b> {category}\n"
            "👤 <b>Имя:</b> {name}\n"
            "📞 <b>Телефон:</b> {phone}\n"
            "💬 <b>Сообщений:</b> {count}\n"
            "{preview}\n"
            "Всё верно? Нажмите <b>«📨 Отправить»</b>."
        ),
        "sent": (
            "✅ <b>Ваше обращение принято!</b>\n\n"
            "📌 Номер обращения: <b>#{ticket}</b>\n\n"
            "Ответственный сотрудник рассмотрит его и в ближайшее время свяжется с вами "
            "через этот бот или по телефону.\n\n"
            "В срочных случаях: <b>{phone}</b>"
        ),
        "send_failed": (
            "😔 Извините, из-за технической ошибки обращение не отправлено.\n\n"
            "Пожалуйста, попробуйте чуть позже или позвоните по номеру <b>{phone}</b>."
        ),
        "too_fast": "Вы только что отправили обращение. Пожалуйста, подождите {sec} сек. перед новым.",
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
    return text.format(**kwargs) if kwargs else text


def all_variants(key: str) -> set[str]:
    """Tugma matnining barcha tillardagi variantlari (handler filtrlari uchun)."""
    return {T[lang][key] for lang in T}
