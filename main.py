import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from keep_alive import keep_alive

# Токен і Chat ID
BOT_TOKEN = "8441710554:AAGFDgaFwQpcx3bFQ-2FgjjlkK7CEKxmz34"
CHAT_ID = 681357425

# Логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Ціни зараз"], ["Змінити маржу", "Змінити плече"], ["Додати монету"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привіт! Бот запущено успішно ✅", reply_markup=reply_markup)

# Відповідь на "Привіт"
async def reply_hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! 👋 Я вже активний і готовий до роботи!")

# Обробка будь-яких повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    if msg.lower() == "ціни зараз":
        await update.message.reply_text("🔄 Отримую актуальні ціни...")
        # Тут буде додано перевірку цін по API MEXC
    else:
        await update.message.reply_text("Я отримав твоє повідомлення!")

# Запуск бота
def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("(?i)привіт"), reply_hello))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()

keep_alive()
run_bot()
