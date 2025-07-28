import os
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio

BOT_TOKEN = "8441710554:AAGFDgaFwQpcx3bFQ-2FgjjlkK7CEKxmz34"
CHAT_ID = 681357425

# Flask сервер для Render
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return '✅ Bot is running!'

# Обробники команд Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привіт! Я готовий до роботи.")

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() == "привіт":
        await update.message.reply_text("Вітаю! Як можу допомогти?")

# Запуск Telegram бота
async def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
    await app.run_polling()

# Запуск Flask і Telegram одночасно
if __name__ == '__main__':
    import threading

    threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=8080)).start()

    asyncio.run(run_bot())
