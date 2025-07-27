import time
import requests
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
from keep_alive import keep_alive

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
margin = 100

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Змінити маржу", "Змінити плече"], ["Додати монету", "Ціни зараз"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привіт! Бот працює ✅", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global margin
    text = update.message.text

    if text == "Ціни зараз":
        prices = get_prices()
        await update.message.reply_text(prices)
    elif text == "Змінити маржу":
        await update.message.reply_text("Введи нову маржу у $:")
        context.user_data["awaiting_margin"] = True
    elif text == "Змінити плече":
        await update.message.reply_text("Введи монету і нове плече (наприклад: SOL 400):")
        context.user_data["awaiting_leverage"] = True
    elif text == "Додати монету":
        await update.message.reply_text("Введи назву нової монети (наприклад: XRP):")
        context.user_data["awaiting_coin"] = True
    elif context.user_data.get("awaiting_margin"):
        try:
            margin = float(text)
            await update.message.reply_text(f"Маржу оновлено: ${margin}")
        except:
            await update.message.reply_text("Невірне значення")
        context.user_data["awaiting_margin"] = False
    elif context.user_data.get("awaiting_leverage"):
        parts = text.split()
        if len(parts) == 2 and parts[0].upper() in coins and parts[1].isdigit():
            coins[parts[0].upper()]["leverage"] = int(parts[1])
            await update.message.reply_text(f"Плече оновлено для {parts[0].upper()}: {parts[1]}×")
        else:
            await update.message.reply_text("Формат невірний")
        context.user_data["awaiting_leverage"] = False
    elif context.user_data.get("awaiting_coin"):
        coin = text.upper()
        if coin not in coins:
            coins[coin] = {"leverage": 100}
            await update.message.reply_text(f"Монету {coin} додано з плечем 100×")
        else:
            await update.message.reply_text("Монета вже існує")
        context.user_data["awaiting_coin"] = False

def get_prices():
    url = "https://api.mexc.com/api/v1/contract/ticker"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        results = []
        for coin in coins:
            symbol = f"{coin}_USDT"
            item = next((x for x in data if x["symbol"] == symbol), None)
            if item:
                price = float(item["lastPrice"])
                results.append(f"{coin}: ${price:.4f}")
        return "\n".join(results)
    except:
        return "Помилка отримання цін ❌"

async def run_signal_check(bot: Bot):
    while True:
        try:
            prices = get_prices()
            print("⏳ Пошук можливостей на ринку...")
            await bot.send_message(chat_id=CHAT_ID, text="⏳ Пошук можливостей на ринку...")
        except Exception as e:
            print("❌ Помилка:", e)
        await asyncio.sleep(600)

if __name__ == "__main__":
    import asyncio
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    loop = asyncio.get_event_loop()
    loop.create_task(run_signal_check(app.bot))
    app.run_polling()