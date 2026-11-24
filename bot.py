import httpx
from config import settings
API = f"https://api.telegram.org/bot{settings.bot_token}"
async def send_message(chat_id: int, text: str):
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text})
        r.raise_for_status()
        if not r.json().get("ok"): raise RuntimeError("Telegram sendMessage failed")
async def set_webhook():
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(f"{API}/setWebhook", json={"url": f"{settings.webhook_base_url.rstrip('/')}/telegram/webhook", "secret_token": settings.webhook_secret})
        r.raise_for_status()
        if not r.json().get("ok"): raise RuntimeError("Telegram setWebhook failed")
