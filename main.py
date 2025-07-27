import os
import time
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from keep_alive import keep_alive

# ==== Константи ====
BOT_TOKEN = "8441710554:AAGFDgaFwQpcx3bFQ-2FgjjlkK7CEKxmz34"
CHAT_ID = "681357425"
MEXC_API_KEY = "mx0vglwSqWMNfUkdXo"
MEXC_SECRET_KEY = "7107c871e7dc4e3db79f4fddb07e917d"

coins = {
    "SOL": {"leverage": 300},
    "PEPE": {"leverage": 300},
    "BTC": {"leverage": 500},
    "ETH": {"leverage": 500},
}

current_margin = 100

# ==== Отримання ціни з MEXC ====
def get_price(symbol):
    try:
        url = f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}USDT"
        response = requests.get(url, timeout=10)
        data = response.json()
        return float(data["price"])
    except Exception as e:
        print(f"❌ Помилка отримання ціни для {symbol}: {e}")
        return None

# ==== Генерація сигналу ====
def generate_signal(symbol, price):
    direction = "LONG" if price % 2 > 1 else "SHORT"
    entry_price = price
    sl = round(entry_price * (0.98 if direction == "LONG" else 1.02), 5)
    tp = round(entry_price * (1.05 if direction == "LONG" else 0.95), 5)
    leverage = coins[symbol]["leverage"]
    signal = (
        f"📊 Реальний сигнал на {direction}\n"
        f"Монета: {symbol}/USDT\n"
        f"Ціна входу: {entry_price}\n"
        f"Stop Loss: {sl}\n"
        f"Take Profit: {tp}\n"
        f"Кредитне плече: {leverage}×\n"
        f"Маржа: ${current_margin}"
    )
    return signal

# ==== Команди ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Змінити маржу", "Змінити плече"], ["Додати монету", "Ціни зараз"]]
    await update.message.reply_text(
        "✅ Бот активовано. Виберіть дію:", 
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def change_margin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введіть нову маржу у форматі: 150")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_margin
    text = update.message.text
    if text.isdigit():
        current_margin = int(text)
        await update.message.reply_text(f"✅ Нова маржа встановлена: ${current_margin}")
    elif text == "Ціни зараз":
        prices = []
        for coin in coins:
            price = get_price(coin)
            if price:
                prices.append(f"{coin}/USDT = {price}")
        await update.message.reply_text("\n".join(prices))
    else:
        await update.message.reply_text("⚠️ Невідома команда.")

# ==== Головна логіка ====
async def check_market(app):
    while True:
        try:
            for coin in coins:
                price = get_price(coin)
                if price:
                    signal = generate_signal(coin, price)
                    await app.bot.send_message(chat_id=CHAT_ID, text=signal)
            print("✅ Сигнали оновлено.")
        except Exception as e:
            print(f"❌ Помилка перевірки ринку: {e}")
        await asyncio.sleep(600)

# ==== Запуск бота ====
import asyncio
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    keep_alive()  # Вебсервер для Render

    asyncio.create_task(check_market(app))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
