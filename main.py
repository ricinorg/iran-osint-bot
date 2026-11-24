from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, HTTPException, Request
from sqlalchemy import func, select
from config import settings
from database import engine, SessionLocal
from models import Base, User, Activity
from bot import send_message, set_webhook
from phone_service import inspect_phone

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await set_webhook()
    yield
    await engine.dispose()

app = FastAPI(title="IranOSINT Bot API", lifespan=lifespan)

@app.get("/")
async def health():
    return {"status": "ok", "service": "iran-osint-bot"}

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request, x_telegram_bot_api_secret_token: str | None = Header(default=None)):
    if x_telegram_bot_api_secret_token != settings.webhook_secret:
        raise HTTPException(status_code=403, detail="Invalid webhook secret")
    update = await request.json()
    message = update.get("message") or update.get("edited_message")
    if not message or not message.get("text"):
        return {"ok": True}
    chat_id = message["chat"]["id"]
    user = message.get("from", {})
    user_id = user.get("id")
    text = message["text"].strip()
    if not user_id:
        return {"ok": True}
    async with SessionLocal() as session:
        existing = await session.scalar(select(User).where(User.telegram_id == user_id))
        if existing is None:
            session.add(User(telegram_id=user_id, username=user.get("username")))
        session.add(Activity(telegram_id=user_id, action="message"))
        await session.commit()
    if text.startswith("/start"):
        await send_message(chat_id, "سلام! به IranOSINT خوش آمدید. 👋\n\nبرای بررسی قالب شماره موبایل ایران، شماره را ارسال کنید.\n/help راهنما")
    elif text.startswith("/help"):
        await send_message(chat_id, "راهنما:\n/start شروع\n/help راهنما\n/admin آمار مدیر\n\nیک شماره موبایل ایران ارسال کنید.")
    elif text.startswith("/admin"):
        if user_id not in settings.admins:
            await send_message(chat_id, "⛔ دسترسی ندارید.")
        else:
            async with SessionLocal() as session:
                count = await session.scalar(select(func.count()).select_from(User))
            await send_message(chat_id, f"📊 تعداد کاربران: {count or 0}")
    else:
        result = inspect_phone(text)
        if not result["valid"]:
            await send_message(chat_id, "❌ شماره معتبر نیست. نمونه: 09123456789")
        else:
            await send_message(chat_id, f"✅ قالب شماره معتبر است\nشماره: {result['number']}\nپیش‌شماره: {result['prefix']}\nاپراتور تخصیص اولیه: {result['carrier']}\n\nاین بررسی هویت صاحب شماره را مشخص نمی‌کند و اپراتور فعلی ممکن است به‌دلیل ترابرد متفاوت باشد.")
    return {"ok": True}
