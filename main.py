import os
import time
import requests
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder, ContextTypes
from keep_alive import keep_alive

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
MEXC_API_KEY = os.environ.get("MEXC_API_KEY")
MEXC_SECRET_KEY = os.environ.get("MEXC_SECRET_KEY")

# Стартові параметри
margin = 100
leverage = {
    'SOL': 300,
    'PEPE': 300,
    'BTC': 500,
    'ETH': 500
}
coins = ['SOL', 'PEPE', 'BTC', 'ETH']

def get_price(symbol):
    try:
        url = f'https://api.mexc.com/api/v1/contract/market/ticker?symbol={symbol}_USDT'
        response = requests.get(url)
        data = response.json()
        return float(data['data'][0]['lastPrice'])
    except Exception as e:
        print(f"[ПОМИЛКА] Ціна {symbol}: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Змінити маржу'], ['Змінити плече'], ['Додати монету'], ['Ціни зараз']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("🤖 Бот активовано", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global margin
    text = update.message.text

    if text == 'Змінити маржу':
        await update.message.reply_text("Введи нову маржу ($):")
        return

    if text == 'Ціни зараз':
        msg = "📊 Поточні ціни:\n"
        for coin in coins:
            price = get_price(coin)
            if price:
                msg += f"{coin}: ${price:.4f}\n"
            else:
                msg += f"{coin}: помилка отримання\n"
        await update.message.reply_text(msg)
        return

    if text.isdigit():
        margin = int(text)
        await update.message.reply_text(f"✅ Нова маржа: ${margin}")
        return

    await update.message.reply_text("Невідома команда.")

async def send_signal(application):
    while True:
        try:
            for coin in coins:
                price = get_price(coin)
                if price:
                    direction = "LONG" if price % 2 < 1 else "SHORT"
                    sl = round(price * (0.99 if direction == "LONG" else 1.01), 4)
                    tp = round(price * (1.01 if direction == "LONG" else 0.99), 4)
                    lev = leverage.get(coin, 100)
                    msg = (
                        f"📈 Сигнал {direction} по {coin}/USDT\n"
                        f"🔹 Вхід: ${price}\n"
                        f"🎯 TP: {tp}\n"
                        f"🛡 SL: {sl}\n"
                        f"💰 Маржа: ${margin}\n"
                        f"🚀 Плече: {lev}×"
                    )
                    await application.bot.send_message(chat_id=CHAT_ID, text=msg)
            await application.bot.send_message(chat_id=CHAT_ID, text="⏳ Пошук можливостей на ринку...")
        except Exception as e:
            print(f"[ПОМИЛКА сигналу] {e}")
        await asyncio.sleep(600)

if __name__ == '__main__':
    import asyncio
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    asyncio.get_event_loop().create_task(send_signal(app))
    app.run_polling()
