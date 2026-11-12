"""Vercel kirish nuqtasi (ASGI).

  POST /api/webhook          — Telegram update'lari shu yerga keladi
  GET  /api/setup?secret=... — bir martalik sozlash: bazada jadvallar + webhook o'rnatish
  GET  /                     — holatni tekshirish
"""

import hmac
import json
import logging
import os
import sys
from urllib.parse import parse_qs

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("api")

from bot.app import handle_update, setup_webhook  # noqa: E402
from bot.config import config  # noqa: E402


async def _read_body(receive) -> bytes:
    body = b""
    while True:
        message = await receive()
        body += message.get("body", b"")
        if not message.get("more_body"):
            return body


async def _send(send, status: int, payload: dict) -> None:
    data = json.dumps(payload, ensure_ascii=False, indent=2).encode()
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [(b"content-type", b"application/json; charset=utf-8")],
    })
    await send({"type": "http.response.body", "body": data})


def _secret_ok(given: str) -> bool:
    return bool(config.webhook_secret) and hmac.compare_digest(given, config.webhook_secret)


async def app(scope, receive, send):
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return
    if scope["type"] != "http":
        return

    path = scope.get("path", "/").rstrip("/")
    method = scope.get("method", "GET")
    headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}

    if path.endswith("/webhook") and method == "POST":
        if config.webhook_secret and not _secret_ok(headers.get("x-telegram-bot-api-secret-token", "")):
            return await _send(send, 403, {"ok": False})
        try:
            await handle_update(json.loads(await _read_body(receive)))
        except Exception:
            # 200 qaytaramiz — aks holda Telegram shu update'ni qayta-qayta yuborib, navbatni to'sib qo'yadi
            log.exception("Update'ni qayta ishlashda xatolik")
        return await _send(send, 200, {"ok": True})

    if path.endswith("/setup"):
        query = parse_qs(scope.get("query_string", b"").decode())
        if not _secret_ok(query.get("secret", [""])[0]):
            return await _send(send, 403, {
                "ok": False,
                "error": "secret noto'g'ri. Manzil: /api/setup?secret=<WEBHOOK_SECRET qiymati>",
            })
        host = headers.get("x-forwarded-host") or headers.get("host")
        try:
            result = await setup_webhook(f"https://{host}/api/webhook")
        except Exception as e:
            log.exception("Setup xatoligi")
            return await _send(send, 500, {"ok": False, "error": f"{type(e).__name__}: {e}"})
        result["xabar"] = "✅ Tayyor! Bot ishlayapti. Telegram'da botga /start yozib tekshiring."
        return await _send(send, 200, result)

    return await _send(send, 200, {"ok": True, "status": "Golden Lake murojaat boti ishlayapti"})
