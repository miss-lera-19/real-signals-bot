import requests
import time
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from keep_alive import keep_alive

# 🔐 Токени та налаштування
BOT_TOKEN = '8441710554:AAGFDgaFwQpcx3bFQ-2FgjjlkK7CEKxmz34'
CHAT_ID = '681357425'
MEXC_API_KEY = 'mx0vglwSqWMNfUkdXo'
MEXC_SECRET_KEY = '7107c871e7dc4e3db79f4fddb07e917d'

# 📈 Монети та параметри
coins = {
    "SOL": {"leverage": 300},
    "PEPE": {"leverage": 300},
    "BTC": {"leverage": 500},
    "ETH": {"leverage": 500},
}

user_margin = 100  # стартова маржа

# 🔄 Отримати поточну ціну з MEXC
def get_price(symbol):
    try:
        url = f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}USDT"
        response = requests.get(url)
        data = response.json()
        return float(data['price'])
    except Exception as e:
        logging.error(f"Помилка отримання ціни для {symbol}: {e}")
        return None

# 📤 Надіслати сигнал у Telegram
async def send_signal(context: ContextTypes.DEFAULT_TYPE, symbol, direction, entry, sl, tp, leverage):
    text = (
        f"📉 Сигнал на {direction}\n"
        f"Монета: {symbol}/USDT\n"
        f"Вхід: {entry}\n"
        f"SL: {sl} | TP: {tp}\n"
        f"Плече: {leverage}×\n"
        f"Маржа: {user_margin}$\n"
        f"#REALSIGNAL"
    )
    await context.bot.send_message(chat_id=CHAT_ID, text=text)

# 📊 Логіка стратегії
async def check_market(context: ContextTypes.DEFAULT_TYPE):
    for coin, params in coins.items():
        price = get_price(coin)
        if price is None:
            continue

        impulse = price % 10  # умовний сигнал на імпульс

        if impulse > 5:
            direction = "LONG"
            entry = round(price * 1.001, 4)
            sl = round(price * 0.995, 4)
            tp = round(price * 1.01, 4)
        else:
            direction = "SHORT"
            entry = round(price * 0.999, 4)
            sl = round(price * 1.005, 4)
            tp = round(price * 0.99, 4)

        await send_signal(context, coin, direction, entry, sl, tp, params["leverage"])

# 🔘 Обробка кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_margin
    query = update.callback_query
    await query.answer()
    if query.data.startswith("margin_"):
        user_margin = int(query.data.split("_")[1])
        await query.edit_message_text(f"✅ Нова маржа: {user_margin}$")

# 🟢 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Маржа $100", callback_data='margin_100')],
        [InlineKeyboardButton("Маржа $200", callback_data='margin_200')],
        [InlineKeyboardButton("Маржа $500", callback_data='margin_500')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Привіт! Обери маржу:", reply_markup=reply_markup)

# 🟣 Ціни зараз
async def prices_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📊 Поточні ціни:\n"
    for coin in coins:
        price = get_price(coin)
        if price:
            text += f"{coin}/USDT: {price}\n"
    await update.message.reply_text(text)

# 🚀 Старт
if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("prices", prices_now))
    app.add_handler(CallbackQueryHandler(button))
    app.job_queue.run_repeating(check_market, interval=60, first=5)
    app.run_polling()
