# Golden Lake — Murojaatlar boti

Telegram bot: [@goldenlake_murojaat_bot](https://t.me/goldenlake_murojaat_bot)

Mijozlar botga murojaat yozadi → bot uni tartibli kartochka ko‘rinishida xodimlar guruhiga yuboradi →
xodim kartochkaga **Reply** qilib javob yozadi → javob mijozga bot orqali boradi.

## Mijoz uchun oqim (userflow)

```
/start → tilni tanlash (🇺🇿 / 🇷🇺) → salomlashish + asosiy menyu
  ├─ ✍️ Murojaat yuborish
  │    1/4  Mavzu: Xonadon xarid qilish · Shartnoma va to‘lovlar · Qurilish jarayoni ·
  │         Texnik masala · Shikoyat · Taklif · Boshqa savol
  │    2/4  Ism-familiya   (Telegram'dagi ism tugma sifatida taklif qilinadi)
  │    3/4  Telefon        («📱 Raqamni yuborish» tugmasi yoki qo‘lda; +998 formatiga keltiriladi)
  │    4/4  Murojaat matni (matn, rasm, video, hujjat, ovozli xabar — 10 tagacha) → «✅ Tayyor»
  │    Tekshirish ekrani → «📨 Yuborish» / «✏️ Qaytadan to‘ldirish» / «❌ Bekor qilish»
  │    ✅ «Murojaatingiz qabul qilindi! Raqami: #0012»
  ├─ 📞 Bog‘lanish
  └─ 🌐 Tilni o‘zgartirish
```

- Ikkinchi murojaatda ism va telefon qayta so‘ralmaydi — «Shu ma’lumotlar bilan davom etamizmi?» deb so‘raladi.
- Xodim javobi mijozga «💬 Golden Lake mas’ul xodimi javobi — murojaat #0012» sarlavhasi bilan keladi.
  Mijoz shu xabarga Reply qilsa, uning xabari guruhdagi o‘sha murojaatga qo‘shiladi.
- Ketma-ket spam yuborilmasligi uchun murojaatlar orasida 30 soniya kutish bor.

## Xodimlar guruhida

Har bir murojaat shunday ko‘rinadi:

```
🆕 YANGI MUROJAAT #0012
━━━━━━━━━━━━━━━━
🏷 Mavzu: 🏠 Xonadon xarid qilish
👤 Ism: Aziz Karimov
📞 Telefon: +998 90 123 45 67
✈️ Telegram: @aziz · ID 123456789
🌐 Til: 🇺🇿 O‘zbekcha
🕒 Vaqt: 12.11.2026, 17:30
━━━━━━━━━━━━━━━━
💬 Murojaat matni:
│ 3 xonali xonadon narxi qancha? Muddatli to‘lov bormi?
📎 Ilovalar: 2 ta — quyida ⬇️
━━━━━━━━━━━━━━━━
📌 Holat: 🆕 Yangi
↩️ Mijozga javob berish uchun shu xabarga Reply qiling.

#murojaat_0012 #xarid
[🟡 Jarayonda] [✅ Hal qilindi]
[🚫 Spam]
```

- Rasm/video/fayllar kartochkaga **reply** sifatida, aynan shu murojaatga bog‘langan holda keladi.
- **Javob berish:** kartochkaga (yoki uning ostidagi istalgan xabarga) Reply qilib yozing — matn, rasm, fayl, ovozli xabar ham bo‘ladi. Yuborilgach, xabaringizga 👍 qo‘yiladi.
- Birinchi javobdan so‘ng murojaat avtomatik **🟡 Jarayonda** holatiga o‘tadi.
- Holat tugmalari kartochkani yangilaydi (kim va qachon o‘zgartirgani yoziladi) va mijozga xabar beradi.
- «Hal qilindi» murojaatga mijoz yana yozsa — murojaat avtomatik qayta ochiladi.
- Qidiruv: `#murojaat_0012`, `#shikoyat`, `#xarid` va h.k. hashtaglar.
- `/stats` — murojaatlar statistikasi. `/chatid` — guruh ID’sini ko‘rsatadi.

## O‘rnatish

1. `.env.example` dan `.env` nusxa oling va to‘ldiring:
   ```
   BOT_TOKEN=...            # @BotFather tokeni
   GROUP_CHAT_ID=-100...    # murojaatlar guruhining ID'si
   ```
   Guruh ID’sini bilmasangiz: botni guruhga qo‘shing — u ID’ni o‘zi yozib beradi (yoki guruhda `/chatid`).
2. Botni guruhga **admin** qilib qo‘ying (Reply’larni ko‘rishi va reaksiya qo‘yishi uchun).
3. Ishga tushiring — quyidagi variantlardan biri.

### Docker (tavsiya etiladi)
```bash
docker compose up -d --build
docker compose logs -f
```

### Oddiy server (systemd)
```bash
cd /opt && git clone <repo> Golden-Lake-Murojaat-bot && cd Golden-Lake-Murojaat-bot
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env && nano .env
sudo cp deploy/goldenlake-bot.service /etc/systemd/system/
sudo systemctl enable --now goldenlake-bot
```

### Lokal
```bash
pip install -r requirements.txt
python -m bot
```

Ma’lumotlar (murojaatlar, foydalanuvchilar) `data/bot.db` (SQLite) faylida saqlanadi — uni zaxiralab turing.

## Matnlarni o‘zgartirish

Barcha matnlar va tugmalar `bot/texts.py` faylida (o‘zbekcha va ruscha). Murojaat mavzulari — `CATEGORIES`,
kompaniya telefoni/sayti — fayl boshidagi `PHONE`, `SITE`, `EMAIL`.

## Tuzilma

```
bot/
  __main__.py      ishga tushirish
  config.py        .env sozlamalari
  texts.py         barcha matnlar (uz/ru)
  keyboards.py     tugmalar
  card.py          guruhdagi murojaat kartochkasi
  db.py            SQLite
  handlers/user.py   mijoz oqimi
  handlers/group.py  guruh: javob, holatlar, /stats
```
