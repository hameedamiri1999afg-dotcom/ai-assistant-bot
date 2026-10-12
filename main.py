import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from aiohttp import web

# تنظیمات کلیدهای امنیتی رندر
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
# رندر آدرس وب‌سایت شما را خودکار در این متغیر قرار می‌دهد
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

groq_client = Groq(api_key=GROQ_API_KEY)
application = Application.builder().token(TELEGRAM_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("سلام! من روی وب‌سرویس رندر بیدار و آماده‌ام. سوالت را بپرس!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": user_text}],
            model="llama3-8b-8192", 
        )
        ai_response = chat_completion.choices.message.content
        await update.message.reply_text(ai_response)
    except Exception as e:
        await update.message.reply_text("خطایی در پردازش رخ داد.")

# ثبت دستورات ربات
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- تنظیمات سرور وب برای پاسخ به رندر و تلگرام ---
async def telegram_webhook(request):
    """دریافت پیام‌ها از طرف تلگرام و تحویل به ربات"""
    json_string = await request.text()
    update = Update.de_json(data=json_string, bot=application.bot)
    await application.process_update(update)
    return web.Response(text="OK")

async def health_check(request):
    """برای اینکه رندر بفهمد سایت بالا است"""
    return web.Response(text="Bot is alive!")

def main():
    # ساخت سرور وب آیو‌اچ‌تی‌تی‌پی
    web_app = web.Application()
    web_app.router.add_post('/webhook', telegram_webhook)
    web_app.router.add_get('/', health_check)

    # تنظیم پورت رندر
    port = int(os.environ.get("PORT", 10000))
    
    # راه‌اندازی وب‌هوک تلگرام به سمت سرور رندر
    async def bootstrap():
        await application.initialize()
        await application.bot.set_webhook(url=f"{RENDER_EXTERNAL_URL}/webhook")
        await application.start()
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bootstrap())
    
    # اجرای سرور وب
    web.run_app(web_app, port=port)

if __name__ == "__main__":
    main()
