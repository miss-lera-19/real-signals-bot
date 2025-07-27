import os
import time
import requests
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    ApplicationBuilder,
    ContextTypes,
)
from keep_alive import keep_alive

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
MEXC_API_KEY = os.getenv("MEXC_API_KEY")
MEXC_SECRET_KEY = os.getenv("MEXC_SECRET_KEY")

coins = {
    "SOL": {"leverage": 300},
    "PEPE": {"leverage": 300},
    "BTC": {"leverage": 500},
    "ETH": {"leverage": 500}
}
margin = 100

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Змінити маржу", "Змінити плече"], ["Додати монету", "Ціни зараз"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 Привіт! Бот активовано.", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global margin
    msg = update.message.text
    if msg == "Ціни зараз":
        prices = get_prices()
        if prices:
            msg = "📊 Поточні ціни:\n" + "\n".join([f"{k}: ${v}" for k, v in prices.items()])
        else:
            msg = "⚠️ Помилка отримання цін."
        await update.message.reply_text(msg)

    elif msg == "Змінити маржу":
        await update.message.reply_text("Введи нову маржу в $ (наприклад 150):")
        context.user_data["awaiting_margin"] = True

    elif msg == "Змінити плече":
        await update.message.reply_text("Введи монету і плече (наприклад: SOL 250):")
        context.user_data["awaiting_leverage"] = True

    elif msg == "Додати монету":
        await update.message.reply_text("Введи монету (наприклад: DOGE 200):")
        context.user_data["awaiting_add_coin"] = True

    elif context.user_data.get("awaiting_margin"):
        try:
            margin = int(msg)
            await update.message.reply_text(f"✅ Маржу змінено на ${margin}")
        except:
            await update.message.reply_text("❌ Помилка. Введи число.")
        context.user_data["awaiting_margin"] = False

    elif context.user_data.get("awaiting_leverage"):
        try:
            coin, lev = msg.split()
            coin = coin.upper()
            lev = int(lev)
            if coin in coins:
                coins[coin]["leverage"] = lev
                await update.message.reply_text(f"✅ Плече для {coin} змінено на {lev}×")
            else:
                await update.message.reply_text("❌ Такої монети немає.")
        except:
            await update.message.reply_text("❌ Введи у форматі: MONETA 200")
        context.user_data["awaiting_leverage"] = False

    elif context.user_data.get("awaiting_add_coin"):
        try:
            coin, lev = msg.split()
            coin = coin.upper()
            lev = int(lev)
            coins[coin] = {"leverage": lev}
            await update.message.reply_text(f"✅ Монету {coin} додано з плечем {lev}×")
        except:
            await update.message.reply_text("❌ Введи у форматі: MONETA 200")
        context.user_data["awaiting_add_coin"] = False

def get_prices():
    try:
        prices = {}
        for symbol in coins:
            pair = f"{symbol}_USDT"
            url = f"https://api.mexc.com/api/v3/ticker/price?symbol={pair}"
            res = requests.get(url)
            data = res.json()
            price = float(data["price"])
            prices[symbol] = round(price, 6) if price < 1 else round(price, 2)
        return prices
    except:
        return None

def check_market():
    prices = get_prices()
    if not prices:
        return None

    signals = []
    for coin, info in coins.items():
        price = prices[coin]
        if coin == "SOL" and price < 182:
            signals.append(f"🔻 SHORT {coin} @ {price} | Leverage {info['leverage']}× | SL: {round(price + 1, 2)} | TP: {round(price - 2, 2)}")
        elif coin == "SOL" and price > 182:
            signals.append(f"🔼 LONG {coin} @ {price} | Leverage {info['leverage']}× | SL: {round(price - 1, 2)} | TP: {round(price + 2, 2)}")
        # можна додати додаткові умови по інших монетах

    return signals

async def auto_signal(app):
    bot = Bot(BOT_TOKEN)
    counter = 0
    while True:
        if counter % 10 == 0:
            await bot.send_message(chat_id=CHAT_ID, text="⏳ Пошук можливостей на ринку...")

        signals = check_market()
        if signals:
            for s in signals:
                await bot.send_message(chat_id=CHAT_ID, text=s)
        await asyncio.sleep(60)
        counter += 1

if __name__ == "__main__":
    import asyncio
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.job_queue.run_once(lambda _: asyncio.create_task(auto_signal(app)), 1)
    app.run_polling()
