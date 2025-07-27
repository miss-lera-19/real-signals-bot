import requests
import time
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder, ContextTypes
from keep_alive import keep_alive

# Константи
BOT_TOKEN = "8441710554:AAGFDgaFwQpcx3bFQ-2FgjjlkK7CEKxmz34"
CHAT_ID = 681357425
MEXC_API_KEY = "mx0vglwSqWMNfUkdXo"
MEXC_SECRET_KEY = "7107c871e7dc4e3db79f4fddb07e917d"

coins = {
    "SOL": {"leverage": 300},
    "PEPE": {"leverage": 300},
    "BTC": {"leverage": 500},
    "ETH": {"leverage": 500}
}
user_margin = 100

# Отримати ціну монети
def get_price(symbol):
    try:
        url = f"https://api.mexc.com/api/v1/contract/market/ticker?symbol={symbol}_USDT"
        response = requests.get(url)
        data = response.json()
        return float(data["data"][0]["lastPrice"])
    except Exception:
        return None

# Стратегія формування сигналу
def generate_signal(symbol):
    current_price = get_price(symbol)
    if not current_price:
        return None

    direction = "LONG" if int(time.time()) % 2 == 0 else "SHORT"
    entry = round(current_price, 6)
    sl = round(entry * (0.98 if direction == "LONG" else 1.02), 6)
    tp = round(entry * (1.05 if direction == "LONG" else 0.95), 6)

    leverage = coins[symbol]["leverage"]
    margin = user_margin
    position_size = round(margin * leverage / entry, 3)

    return (
        f"📊 Реальний сигнал на {direction}\n"
        f"Монета: {symbol}/USDT\n"
        f"Ціна входу: {entry}\n"
        f"Stop Loss: {sl}\n"
        f"Take Profit: {tp}\n"
        f"Маржа: ${margin}\n"
        f"Плече: {leverage}×\n"
        f"Обʼєм позиції: {position_size} {symbol}"
    )

# Команди Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Ціни зараз"], ["Змінити маржу", "Змінити плече"], ["Додати монету"]]
    await update.message.reply_text("Привіт! Це бот реальних сигналів.", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_margin

    text = update.message.text
    if text == "Ціни зараз":
        msg = ""
        for coin in coins:
            price = get_price(coin)
            msg += f"{coin}/USDT: {price if price else 'н/д'}\n"
        await update.message.reply_text(msg)
    elif text == "Змінити маржу":
        await update.message.reply_text("Введи нову маржу у $:")
    elif text.isdigit() and int(text) > 0:
        user_margin = int(text)
        await update.message.reply_text(f"Нова маржа встановлена: ${user_margin}")
    else:
        await update.message.reply_text("Невідома команда. Використовуй кнопки.")

# Запуск сигналів кожні 60 секунд
async def send_signals(app):
    while True:
        try:
            await app.bot.send_message(chat_id=CHAT_ID, text="⏳ Пошук можливостей на ринку...")
            for coin in coins:
                signal = generate_signal(coin)
                if signal:
                    await app.bot.send_message(chat_id=CHAT_ID, text=signal)
        except Exception as e:
            print("Помилка при надсиланні сигналу:", e)
        await asyncio.sleep(60)

# Запуск
if __name__ == "__main__":
    import asyncio
    keep_alive()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    loop = asyncio.get_event_loop()
    loop.create_task(send_signals(app))
    app.run_polling()
