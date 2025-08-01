from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from chat_expense_tracker import handle_message, download_expense_excel, start
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def start_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("download", download_expense_excel))

    print("🚀 Bot is running...")
    app.run_polling()
    