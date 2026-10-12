import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# گرفتن کلیدها از تنظیمات رندر
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# اتصال به هوش مصنوعی Groq
groq_client = Groq(api_key=GROQ_API_KEY)

# پاسخ به دستور start/
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("سلام! من آماده‌ام. هر سوالی داری بپرس.")

# پردازش و پاسخ به پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    try:
        # ارسال پیام به مدل رایگان
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": user_text}],
            model="llama3-8b-8192", 
        )
        ai_response = chat_completion.choices.message.content
        await update.message.reply_text(ai_response)
    except Exception as e:
        await update.message.reply_text("خطایی رخ داد. لطفاً دوباره تلاش کنید.")
        print(f"Error: {e}")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("بات در حال اجرا است...")
    application.run_polling()

if __name__ == "__main__":
    main()
