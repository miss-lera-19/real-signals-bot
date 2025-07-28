import time
import requests
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from keep_alive import keep_alive

BOT_TOKEN = '8441710554:AAGFDgaFwQpcx3bFQ-2FgjjlkK7CEKxmz34'
CHAT_ID = '681357425'
MEXC_API_KEY = 'mx0vglwSqWMNfUkdXo'
MEXC_SECRET_KEY = '7107c871e7dc4e3db79f4fddb07e917d'

user_margin = 100
leverage = {
    "SOL": 300,
    "PEPE": 300,
    "BTC": 500,
    "ETH": 500
}
tracked_coins = ["SOL", "PEPE", "BTC", "ETH"]

def get_price(symbol):
    try:
        url = f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}USDT"
        response = requests.get(url, timeout=5)
        return float(response.json()['price'])
    except:
        return None

def create_signal(symbol, price):
    lev = leverage.get(symbol, 300)
    entry = round(price, 5)
    direction = "LONG" if price % 2 > 1 else "SHORT"
    sl = round(entry * (0.995 if direction == "LONG" else 1.005), 5)
    tp = round(entry * (1.05 if direction == "LONG" else 0.95), 5)
    return f"""
📈 <b>{symbol}/USDT {direction} SIGNAL</b>
💰 Вхід: <b>{entry}</b>
🛡 Stop Loss: <b>{sl}</b>
🎯 Take Profit: <b>{tp}</b>
📊 Плече: <b>{lev}×</b>
💵 Маржа: <b>{user_margin}$</b>
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Змінити маржу", "Змінити плече"], ["Ціни зараз"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привіт! Я бот для сигналів", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_margin
    msg = update.message.text

    if msg == "Змінити маржу":
        await update.message.reply_text("Введи нову маржу у $:")
        context.user_data["changing_margin"] = True

    elif msg == "Змінити плече":
        await update.message.reply_text("Введи монету та нове плече (наприклад: SOL 200):")
        context.user_data["changing_leverage"] = True

    elif msg == "Ціни зараз":
        text = ""
        for coin in tracked_coins:
            p = get_price(coin)
            text += f"{coin}/USDT: {p}$\n" if p else f"{coin}: помилка\n"
        await update.message.reply_text(text)

    elif context.user_data.get("changing_margin"):
        try:
            user_margin = int(msg)
            await update.message.reply_text(f"Маржу оновлено: {user_margin}$")
        except:
            await update.message.reply_text("Помилка. Введи число.")
        context.user_data["changing_margin"] = False

    elif context.user_data.get("changing_leverage"):
        try:
            parts = msg.upper().split()
            if len(parts) == 2 and parts[0] in tracked_coins:
                leverage[parts[0]] = int(parts[1])
                await update.message.reply_text(f"Плече для {parts[0]} встановлено: {parts[1]}×")
            else:
                await update.message.reply_text("Формат: SOL 200")
        except:
            await update.message.reply_text("Помилка.")
        context.user_data["changing_leverage"] = False

async def market_loop(app: Application):
    while True:
        try:
            for coin in tracked_coins:
                price = get_price(coin)
                if price:
                    signal = create_signal(coin, price)
                    await app.bot.send_message(chat_id=CHAT_ID, text=signal, parse_mode="HTML")
            await app.bot.send_message(chat_id=CHAT_ID, text="⏳ Пошук можливостей на ринку...")
        except Exception as e:
            logging.error(f"Error in market loop: {e}")
        await asyncio.sleep(60)

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    keep_alive()
    app.create_task(market_loop(app))
    await app.run_polling()

import asyncio
if __name__ == '__main__':
    asyncio.run(main())