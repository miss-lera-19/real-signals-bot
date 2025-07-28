import os
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Telegram токен і chat_id (встав свої значення)
BOT_TOKEN = "8441710554:AAGFDgaFwQpcx3bFQ-2FgjjlkK7CEKxmz34"
CHAT_ID = 681357425

# Вебсервер для Render
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running!'

# Обробник /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привіт! Я готовий до роботи.")

# Обробник повідомлення "Привіт"
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() == "привіт":
        await update.message.reply_text("Вітаю! Як можу допомогти?")

if __name__ == '__main__':
    import threading

    def run_flask():
        app.run(host='0.0.0.0', port=8080)

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Telegram бот
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
    app_bot.run_polling()
