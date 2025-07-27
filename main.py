import os
import requests
import time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

current_margin = 100
leverage = {
    "SOL": 300,
    "PEPE": 300,
    "BTC": 500,
    "ETH": 500
}

def get_prices():
    urls = {
        "SOL": "https://api.mexc.com/api/v3/ticker/price?symbol=SOLUSDT",
        "PEPE": "https://api.mexc.com/api/v3/ticker/price?symbol=PEPEUSDT",
        "BTC": "https://api.mexc.com/api/v3/ticker/price?symbol=BTCUSDT",
        "ETH": "https://api.mexc.com/api/v3/ticker/price?symbol=ETHUSDT"
    }
    prices = {}
    for coin, url in urls.items():
        try:
            r = requests.get(url, timeout=5)
            data = r.json()
            prices[coin] = float(data["price"])
        except Exception:
            prices[coin] = None
    return prices

def start(update: Update, context: CallbackContext):
    kb = [["✏️ Змінити маржу", "📉 Змінити плече"], ["📊 Ціни зараз"]]
    reply_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)
    update.message.reply_text("✅ Бот активний!", reply_markup=reply_markup)

def handle_message(update: Update, context: CallbackContext):
    global current_margin
    text = update.message.text

    if text == "✏️ Змінити маржу":
        update.message.reply_text("Введи нову маржу (наприклад, 150):")
        return

    if text.replace(".", "", 1).isdigit():
        current_margin = float(text)
        update.message.reply_text(f"✅ Нова маржа: {current_margin}")
        return

    if text == "📊 Ціни зараз":
        prices = get_prices()
        msg = "📊 Поточні ціни:\n"
        for coin, price in prices.items():
            if price is not None:
                msg += f"{coin}: ${price}\n"
            else:
                msg += f"{coin}: помилка отримання\n"
        update.message.reply_text(msg)

def check_market():
    while True:
        try:
            prices = get_prices()
            message = "⏳ Пошук можливостей на ринку...\n"
            for coin, price in prices.items():
                if price is not None:
                    message += f"{coin}: ${price}\n"
            context.bot.send_message(chat_id=CHAT_ID, text=message)
        except Exception:
            pass
        time.sleep(600)

if __name__ == '__main__':
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()
