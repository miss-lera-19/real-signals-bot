import logging
import asyncio
import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8441710554:AAGFDgaFwQpcx3bFQ-2FgjjlkK7CEKxmz34"
CHAT_ID = 681357425
MEXC_API_KEY = "mx0vglwSqWMNfUkdXo"
MEXC_SECRET_KEY = "7107c871e7dc4e3db79f4fddb07e917d"

# Стартові значення
user_state = {
    "margin": 100,
    "leverage": {"SOL": 300, "PEPE": 300, "BTC": 500, "ETH": 500}
}
available_coins = ["SOL", "PEPE", "BTC", "ETH"]

# Налаштування логування
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Команди
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Змінити маржу", "Змінити плече"], ["Додати монету", "Ціни зараз"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привіт! Я готовий надсилати торгові сигнали 📈", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Змінити маржу":
        await update.message.reply_text("Введи нову маржу в $ (наприклад: 120)")
        context.user_data["change_margin"] = True
    elif text == "Змінити плече":
        await update.message.reply_text("Введи монету і нове плече (наприклад: SOL 200)")
        context.user_data["change_leverage"] = True
    elif text == "Додати монету":
        await update.message.reply_text("Введи назву монети у форматі: NEWCOIN")
        context.user_data["add_coin"] = True
    elif text == "Ціни зараз":
        prices = get_all_prices()
        if prices:
            message = "
".join([f"{coin}: {price} USDT" for coin, price in prices.items()])
        else:
            message = "Не вдалося отримати ціни ❌"
        await update.message.reply_text(message)
    elif context.user_data.get("change_margin"):
        try:
            new_margin = float(text)
            user_state["margin"] = new_margin
            await update.message.reply_text(f"Маржа оновлена: ${new_margin}")
        except:
            await update.message.reply_text("Неправильний формат. Введи число.")
        context.user_data["change_margin"] = False
    elif context.user_data.get("change_leverage"):
        try:
            coin, lev = text.split()
            lev = int(lev)
            user_state["leverage"][coin.upper()] = lev
            await update.message.reply_text(f"Плече оновлено для {coin.upper()}: {lev}×")
        except:
            await update.message.reply_text("Невірний формат. Введи, наприклад: SOL 200")
        context.user_data["change_leverage"] = False
    elif context.user_data.get("add_coin"):
        coin = text.upper()
        if coin not in available_coins:
            available_coins.append(coin)
            await update.message.reply_text(f"Монету {coin} додано ✅")
        else:
            await update.message.reply_text(f"Монета {coin} вже є")
        context.user_data["add_coin"] = False
    else:
        await update.message.reply_text("Не впізнаю команду. Скористайся кнопками.")

# Отримати ціну монети з MEXC
def get_price(symbol):
    url = f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}USDT"
    try:
        response = requests.get(url, timeout=10)
        return float(response.json()["price"])
    except:
        return None

# Ціни на всі монети
def get_all_prices():
    prices = {}
    for coin in available_coins:
        price = get_price(coin)
        if price:
            prices[coin] = price
    return prices

# Генерація сигналу LONG/SHORT
async def check_signals(app):
    while True:
        try:
            for coin in available_coins:
                price = get_price(coin)
                if not price:
                    continue
                lev = user_state["leverage"].get(coin, 100)
                margin = user_state["margin"]
                position_size = round(margin * lev / price, 2)
                sl = round(price * 0.99, 4)
                tp = round(price * 1.02, 4)
                direction = "LONG" if int(price) % 2 == 0 else "SHORT"
                text = (
                    f"📢 Реальний сигнал ({direction}) по {coin}:
"
                    f"💰 Ціна входу: {price} USDT
"
                    f"🎯 Take Profit: {tp} USDT
"
                    f"🛡 Stop Loss: {sl} USDT
"
                    f"💵 Плече: {lev}×
"
                    f"📊 Маржа: ${margin}
"
                    f"📈 Обʼєм: {position_size} {coin}"
                )
                await app.bot.send_message(chat_id=CHAT_ID, text=text)
        except Exception as e:
            logging.error(f"Помилка перевірки сигналів: {e}")
        await asyncio.sleep(60)

# Запуск бота
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    asyncio.create_task(check_signals(app))
    await app.run_polling()

if __name__ == "__main__":
    import keep_alive
    keep_alive.keep_alive()
    asyncio.run(main())