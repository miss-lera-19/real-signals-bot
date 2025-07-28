import asyncio
import logging
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)
import aiohttp
from keep_alive import keep_alive

# Константи
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
MEXC_API_KEY = os.getenv("MEXC_API_KEY")
MEXC_SECRET_KEY = os.getenv("MEXC_SECRET_KEY")

user_margin = 100
user_leverage = {
    "SOL": 300,
    "PEPE": 300,
    "BTC": 500,
    "ETH": 500
}

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Кнопки
def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Змінити маржу", callback_data="change_margin")],
        [InlineKeyboardButton("Змінити плече", callback_data="change_leverage")],
        [InlineKeyboardButton("Ціни зараз", callback_data="show_prices")]
    ])

# Команди
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Я бот для реальних торгових сигналів 🔥", reply_markup=get_main_keyboard())

# Обробка кнопок
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "change_margin":
        await query.edit_message_text("Введи нову маржу ($):")
        context.user_data["awaiting_margin"] = True

    elif query.data == "change_leverage":
        await query.edit_message_text("Введи монету і плече (наприклад: SOL 250):")
        context.user_data["awaiting_leverage"] = True

    elif query.data == "show_prices":
        prices = await get_all_prices()
        await query.edit_message_text(prices, reply_markup=get_main_keyboard())

# Обробка повідомлень користувача
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_margin

    if context.user_data.get("awaiting_margin"):
        try:
            user_margin = float(update.message.text)
            await update.message.reply_text(f"✅ Нова маржа: ${user_margin}", reply_markup=get_main_keyboard())
        except ValueError:
            await update.message.reply_text("Помилка. Введи число.")
        context.user_data["awaiting_margin"] = False

    elif context.user_data.get("awaiting_leverage"):
        try:
            coin, lev = update.message.text.upper().split()
            if coin in user_leverage:
                user_leverage[coin] = int(lev)
                await update.message.reply_text(f"✅ Нова плече для {coin}: {lev}×", reply_markup=get_main_keyboard())
            else:
                await update.message.reply_text("Монету не знайдено.")
        except Exception:
            await update.message.reply_text("Формат: SOL 250")
        context.user_data["awaiting_leverage"] = False

# Отримання ціни з MEXC
async def get_price(symbol):
    url = f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                return float(data["price"])
    except Exception as e:
        logger.error(f"Помилка отримання ціни {symbol}: {e}")
        return None

async def get_all_prices():
    sol = await get_price("SOLUSDT")
    pepe = await get_price("PEPEUSDT")
    btc = await get_price("BTCUSDT")
    eth = await get_price("ETHUSDT")
    return (
        f"📊 Поточні ціни:
"
        f"SOL: ${sol}
"
        f"PEPE: ${pepe}
"
        f"BTC: ${btc}
"
        f"ETH: ${eth}"
    )

# Перевірка ринку щохвилини
async def check_market(context: CallbackContext):
    for symbol in ["SOL", "PEPE", "BTC", "ETH"]:
        price = await get_price(symbol + "USDT")
        if not price:
            continue

        direction = "LONG" if price % 2 < 1 else "SHORT"  # Простий приклад, заміни на реальну стратегію
        entry = round(price, 4)
        sl = round(entry * (0.99 if direction == "LONG" else 1.01), 4)
        tp = round(entry * (1.03 if direction == "LONG" else 0.97), 4)
        leverage = user_leverage[symbol]
        text = (
            f"📈 Сигнал ({symbol}/USDT)
"
            f"Напрям: {direction}
"
            f"Вхід: {entry}
"
            f"SL: {sl}
"
            f"TP: {tp}
"
            f"Плече: {leverage}×
"
            f"Маржа: ${user_margin}"
        )
        await context.bot.send_message(chat_id=CHAT_ID, text=text)

# Основна функція запуску
async def main():
    keep_alive()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_buttons))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CommandHandler("prices", show_prices))
    application.add_handler(CommandHandler("margin", handle_message))
    application.add_handler(CommandHandler("leverage", handle_message))
    application.add_handler(CallbackQueryHandler(handle_buttons))
    application.add_handler(MessageHandler(None, handle_message))
    job_queue = application.job_queue
    job_queue.run_repeating(check_market, interval=60, first=10)
    await application.run_polling()

async def show_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = await get_all_prices()
    await update.message.reply_text(text, reply_markup=get_main_keyboard())

if __name__ == "__main__":
    asyncio.run(main())