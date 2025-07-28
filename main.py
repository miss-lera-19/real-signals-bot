import logging
import os
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from keep_alive import keep_alive

# === Константи ===
BOT_TOKEN = "8441710554:AAGFDgaFwQpcx3bFQ-2FgjjlkK7CEKxmz34"
CHAT_ID = 681357425

# === Логування ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# === Кнопки ===
keyboard = [
    [InlineKeyboardButton("Ціни зараз", callback_data="prices")],
    [InlineKeyboardButton("Змінити маржу", callback_data="change_margin")],
    [InlineKeyboardButton("Змінити плече", callback_data="change_leverage")],
    [InlineKeyboardButton("Додати монету", callback_data="add_coin")],
]
reply_markup = InlineKeyboardMarkup(keyboard)

# === /start команда ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привіт! Я бот для реальних сигналів.", reply_markup=reply_markup)

# === Обробка кнопок ===
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data

    if action == "prices":
        await query.edit_message_text(text="🔄 Отримую ціни... (реалізація пізніше)")
    elif action == "change_margin":
        await query.edit_message_text(text="Введіть нову маржу:")
    elif action == "change_leverage":
        await query.edit_message_text(text="Введіть нове плече:")
    elif action == "add_coin":
        await query.edit_message_text(text="Введіть монету, яку хочете додати:")
    else:
        await query.edit_message_text(text="Невідома дія.")

# === Головна функція ===
async def main():
    keep_alive()
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
