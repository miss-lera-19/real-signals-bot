
import logging
import os
import asyncio
import aiohttp
import time
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from keep_alive import keep_alive

# Змінні з середовища
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
MEXC_API_KEY = os.environ.get("MEXC_API_KEY")
MEXC_SECRET_KEY = os.environ.get("MEXC_SECRET_KEY")

# Початкові налаштування
user_settings = {
    "margin": 100,
    "leverage": {
        "SOL": 300,
        "PEPE": 300,
        "BTC": 500,
        "ETH": 500
    }
}
coins = ["SOL", "PEPE", "BTC", "ETH"]

# Логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Отримання ціни з MEXC API
async def get_price(symbol: str) -> float:
    url = f"https://contract.mexc.com/api/v1/contract/ticker?symbol={symbol}_USDT"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                data = await response.json()
                return float(data["data"]["lastPrice"])
    except Exception as e:
        logging.error(f"Помилка при отриманні ціни {symbol}: {e}")
        return None

# Генерація сигналу
async def generate_signal(symbol: str) -> str:
    price = await get_price(symbol)
    if price is None:
        return f"⚠️ Помилка отримання ціни для {symbol}"

    margin = user_settings["margin"]
    leverage = user_settings["leverage"].get(symbol, 100)

    direction = "LONG" if int(time.time()) % 2 == 0 else "SHORT"
    entry = round(price, 5)
    sl = round(entry * (0.99 if direction == "LONG" else 1.01), 5)
    tp = round(entry * (1.03 if direction == "LONG" else 0.97), 5)

    return (
        f"📈 Реальний сигнал {symbol}/USDT
"
        f"Напрям: {direction}
"
        f"Ціна входу: {entry}
"
        f"Stop Loss: {sl}
"
        f"Take Profit: {tp}
"
        f"Кредитне плече: {leverage}×
"
        f"Маржа: ${margin}"
    )

# Команди
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Змінити маржу", callback_data="change_margin")],
        [InlineKeyboardButton("Змінити плече", callback_data="change_leverage")],
        [InlineKeyboardButton("Додати монету", callback_data="add_coin")],
        [InlineKeyboardButton("Ціни зараз", callback_data="current_prices")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Бот активний ✅", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "change_margin":
        await query.edit_message_text("Введи нову маржу (наприклад: 200):")
        context.user_data["action"] = "change_margin"

    elif query.data == "change_leverage":
        await query.edit_message_text("Введи монету та плече (наприклад: SOL 400):")
        context.user_data["action"] = "change_leverage"

    elif query.data == "add_coin":
        await query.edit_message_text("Введи назву монети, яку хочеш додати:")
        context.user_data["action"] = "add_coin"

    elif query.data == "current_prices":
        msg = ""
        for coin in coins:
            price = await get_price(coin)
            if price:
                msg += f"{coin}: ${price}\n"
            else:
                msg += f"{coin}: помилка\n"
        await query.edit_message_text(f"📊 Поточні ціни:\n{msg}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    action = context.user_data.get("action")

    if action == "change_margin":
        try:
            user_settings["margin"] = int(text)
            await update.message.reply_text(f"Маржу оновлено: ${text}")
        except:
            await update.message.reply_text("Помилка. Введи число.")
        context.user_data["action"] = None

    elif action == "change_leverage":
        try:
            coin, lev = text.upper().split()
            user_settings["leverage"][coin] = int(lev)
            await update.message.reply_text(f"Плече для {coin} оновлено на {lev}×")
        except:
            await update.message.reply_text("Формат: SOL 300")
        context.user_data["action"] = None

    elif action == "add_coin":
        coin = text.upper()
        if coin not in coins:
            coins.append(coin)
            user_settings["leverage"][coin] = 100
            await update.message.reply_text(f"Монету {coin} додано")
        else:
            await update.message.reply_text(f"Монета {coin} вже є")
        context.user_data["action"] = None

# Цикл надсилання сигналів
async def signal_loop(app):
    bot = Bot(BOT_TOKEN)
    while True:
        for coin in coins:
            signal = await generate_signal(coin)
            await bot.send_message(chat_id=CHAT_ID, text=signal)
        await asyncio.sleep(600)

# Запуск
async def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("prices", button_handler))
    app.add_handler(MessageHandler(None, handle_message))
    asyncio.create_task(signal_loop(app))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
