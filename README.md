# Golden Lake — Murojaatlar boti

Telegram bot: [@goldenlake_murojaat_bot](https://t.me/goldenlake_murojaat_bot)

Mijozlar botga murojaat yozadi → bot uni tartibli kartochka ko‘rinishida xodimlar guruhiga yuboradi →
xodim kartochkaga **Reply** qilib javob yozadi → javob mijozga bot orqali boradi.

## Mijoz uchun oqim (userflow)

```
/start → tilni tanlash (🇺🇿 / 🇷🇺) → salomlashish + asosiy menyu
  ├─ ✍️ Murojaat yuborish
  │    1/2  Mavzu: Shartnoma va to‘lovlar · Qurilish jarayoni · Texnik masala · Taklif · Boshqa savol
  │    2/2  Murojaat matni (matn, rasm, video, hujjat, ovozli xabar — 10 tagacha) → «✅ Tayyor»
  │    Tekshirish ekrani → «📨 Yuborish» / «✏️ Qaytadan yozish» / «❌ Bekor qilish»
  │    ✅ «Murojaatingiz yuborildi! Raqami: #0012»
  ├─ 📞 Bog‘lanish (@goldenlake_admin)
  └─ 🌐 Tilni o‘zgartirish
```

- Murojaatlar **anonim**: ism, telefon so‘ralmaydi, guruhda mijozning Telegram profili ham ko‘rinmaydi.
- Xodim javobi mijozga «💬 Golden Lake mas’ul xodimi javobi — murojaat #0012» sarlavhasi bilan keladi.
  Mijoz shu xabarga Reply qilsa, uning xabari guruhdagi o‘sha murojaatga qo‘shiladi.
- Ketma-ket spam yuborilmasligi uchun murojaatlar orasida 30 soniya kutish bor.

## Xodimlar guruhida

Har bir murojaat shunday ko‘rinadi:

```
🆕 YANGI MUROJAAT #0012
━━━━━━━━━━━━━━━━
🏷 Mavzu: 📄 Shartnoma va to‘lovlar
🔒 Muallif: anonim
🌐 Til: 🇺🇿 O‘zbekcha
🕒 Vaqt: 12.11.2026, 17:30
━━━━━━━━━━━━━━━━
💬 Murojaat matni:
│ Muddatli to‘lov grafigini qayerdan ko‘rsam bo‘ladi?
📎 Ilovalar: 2 ta — quyida ⬇️
━━━━━━━━━━━━━━━━
📌 Holat: 🆕 Yangi
↩️ Mijozga javob berish uchun shu xabarga Reply qiling.

#murojaat_0012 #tolov
[🟡 Jarayonda] [✅ Hal qilindi]
[🚫 Spam]
```

- Rasm/video/fayllar kartochkaga **reply** sifatida, aynan shu murojaatga bog‘langan holda keladi.
- **Javob berish:** kartochkaga (yoki uning ostidagi istalgan xabarga) Reply qilib yozing — matn, rasm, fayl, ovozli xabar ham bo‘ladi. Yuborilgach, xabaringizga 👍 qo‘yiladi.
- Birinchi javobdan so‘ng murojaat avtomatik **🟡 Jarayonda** holatiga o‘tadi.
- Holat tugmalari kartochkani yangilaydi (kim va qachon o‘zgartirgani yoziladi) va mijozga xabar beradi.
- «Hal qilindi» murojaatga mijoz yana yozsa — murojaat avtomatik qayta ochiladi.
- Qidiruv: `#murojaat_0012`, `#tolov`, `#qurilish` va h.k. hashtaglar.
- `/stats` — murojaatlar statistikasi. `/chatid` — guruh ID’sini ko‘rsatadi.

## Vercel'ga o‘rnatish (bepul)

Bot Vercel’da (bepul) ishlaydi, ma’lumotlar Neon’da (bepul Postgres) saqlanadi.

1. **Vercel’da loyiha:** [vercel.com](https://vercel.com) → GitHub orqali kiring → **Add New → Project** →
   `Golden-Lake-Murojaat-bot` repo’sini **Import** qiling → Framework: **Other** →
   **Environment Variables** ga qo‘shing:

   | Nomi | Qiymati |
   |---|---|
   | `BOT_TOKEN` | @BotFather tokeni |
   | `GROUP_CHAT_ID` | `-1003561633389` |
   | `WEBHOOK_SECRET` | o‘zingiz o‘ylab topgan maxfiy so‘z (faqat lotin harf va raqam) |

   **Deploy** ni bosing.
2. **Baza (Neon):** loyiha ichida **Storage → Create Database → Neon (Serverless Postgres)** →
   region: **Frankfurt** → **Create** → loyihaga **Connect** qiling. `DATABASE_URL` avtomatik qo‘shiladi.
   (Yoki [neon.tech](https://neon.tech) da baza ochib, connection string’ni `DATABASE_URL` sifatida qo‘lda qo‘shing.)
3. **Qayta deploy:** **Deployments** → oxirgi deploy yonidagi **⋯ → Redeploy**
   (yangi o‘zgaruvchilar faqat shundan keyin ishlaydi).
4. **Botni ulash** — brauzerda bir marta oching:
   ```
   https://<loyiha-nomi>.vercel.app/api/setup?secret=<WEBHOOK_SECRET>
   ```
   `"✅ Tayyor! Bot ishlayapti"` chiqsa — hammasi joyida. Botga `/start` yozib tekshiring.

Bot guruhda **admin** bo‘lishi kerak. Guruh ID’sini bilmasangiz — botni guruhga qo‘shing, u ID’ni o‘zi yozib beradi
(yoki guruhda `/chatid`).

**Muammo bo‘lsa:** Vercel → loyiha → **Logs** bo‘limida xatolik ko‘rinadi.
`https://<loyiha>.vercel.app/` ochilsa `"Golden Lake murojaat boti ishlayapti"` chiqishi kerak.

### Lokal ishga tushirish (dasturchilar uchun)
```bash
pip install -r requirements.txt
cp .env.example .env   # to‘ldiring
python -m bot          # polling rejimi — Vercel webhook’ini o‘chiradi!
```
Lokal sinovdan so‘ng Vercel’dagi botni qayta ulash uchun `/api/setup?secret=...` ni yana oching.

## Matnlarni o‘zgartirish

Barcha matnlar va tugmalar `bot/texts.py` faylida (o‘zbekcha va ruscha). Murojaat mavzulari — `CATEGORIES`,
kompaniya telefoni/sayti va admin — fayl boshidagi `PHONE`, `SITE`, `ADMIN`.

## Tuzilma

```
api/index.py       Vercel kirish nuqtasi (webhook, /api/setup)
vercel.json        Vercel sozlamalari
bot/
  app.py           dispatcher, update’ni qayta ishlash, webhook o‘rnatish
  __main__.py      lokal ishga tushirish (polling)
  config.py        sozlamalar (environment variables)
  storage.py       mijoz qaysi bosqichdaligini Postgres’da saqlash
  texts.py         barcha matnlar (uz/ru)
  keyboards.py     tugmalar
  card.py          guruhdagi murojaat kartochkasi
  db.py            Postgres (Neon)
  handlers/user.py   mijoz oqimi
  handlers/group.py  guruh: javob, holatlar, /stats
```
