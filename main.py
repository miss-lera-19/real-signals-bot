import time
import requests
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from keep_alive import keep_alive

BOT_TOKEN = "ТУТ_ВСТАВ_СВІЙ_ТОКЕН"
CHAT_ID = 681357425

bot = Bot(token=BOT_TOKEN)

current_margin = 100
leverage = {"SOL": 300, "PEPE": 300, "BTC": 500, "ETH": 500}
coins = ["SOL", "PEPE", "BTC", "ETH"]

def get_prices():
    urls = {
        "SOL": "https://api.mexc.com/api/v3/ticker/price?symbol=SOLUSDT",
        "PEPE": "https://api.mexc.com/api/v3/ticker/price?symbol=PEPEUSDT",
        "BTC": "https://api.mexc.com/api/v3/ticker/price?symbol=BTCUSDT",
        "ETH": "https://api.mexc.com/api/v3/ticker/price?symbol=ETHUSDT",
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
    kb = [["📉 Змінити маржу", "📈 Змінити плече"], ["➕ Додати монету", "📊 Ціни зараз"]]
    reply_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)
    update.message.reply_text("✅ Бот активний. Обери дію:", reply_markup=reply_markup)

def handle_message(update: Update, context: CallbackContext):
    global current_margin
    text = update.message.text

    if text == "📉 Змінити маржу":
        update.message.reply_text("Введи нову маржу ($):")
        return

    if text.replace(".", "").isdigit():
        current_margin = float(text)
        update.message.reply_text(f"✅ Нова маржа встановлена: ${current_margin}")
        return

    if text == "📊 Ціни зараз":
        prices = get_prices()
    msg = "📊 Поточні ціни:\n"
" + "\n".join([f"{c}: ${prices[c]}" for c in prices])
        update.message.reply_text(msg)

def check_market():
    while True:
        bot.send_message(chat_id=CHAT_ID, text="⏳ Пошук можливостей на ринку...")
        time.sleep(600)

keep_alive()

updater = Updater(token=BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

updater.start_polling()
check_market()
