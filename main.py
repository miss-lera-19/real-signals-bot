import time
import requests
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ApplicationBuilder, ContextTypes
import asyncio

# --- Налаштування ---
BOT_TOKEN = "8441710554:AAGFDgaFwQpcx3bFQ-2FgjjlkK7CEKxmz34"
CHAT_ID = 681357425
MEXC_API_URL = "https://api.mexc.com"
symbols = {"SOLUSDT": 300, "PEPEUSDT": 300, "BTCUSDT": 500, "ETHUSDT": 500}

# --- Початкові значення ---
user_margin = 100
user_leverage = symbols.copy()

# --- Отримання ціни ---
def get_price(symbol):
    try:
        response = requests.get(f"{MEXC_API_URL}/api/v3/ticker/price", params={"symbol": symbol})
        return float(response.json()['price'])
    except Exception as e:
        return None

# --- Стратегія ---
def generate_signal(symbol, price):
    if symbol == "SOLUSDT":
        if price < 181:
            return "SHORT", price, price + 0.8, price - 1.6
        elif price > 182:
            return "LONG", price, price - 0.8, price + 1.6
    elif symbol == "PEPEUSDT":
        if price < 0.00001240:
            return "LONG", price, price - 0.00000020, price + 0.00000040
    elif symbol == "BTCUSDT":
        if price < 62000:
            return "LONG", price, price - 300, price + 600
        elif price > 64000:
            return "SHORT", price, price + 300, price - 600
    elif symbol == "ETHUSDT":
        if price < 3400:
            return "LONG", price, price - 20, price + 40
        elif price > 3500:
            return "SHORT", price, price + 20, price - 40
    return None, None, None, None

# --- Надсилання сигналу ---
async def send_signal(symbol, direction, entry, sl, tp, context: ContextTypes.DEFAULT_TYPE):
    margin = user_margin
    leverage = user_leverage[symbol]
    text = (
        f"📢 <b>{symbol} | {direction}</b>\n"
        f"💰 Вхід: <code>{entry:.6f}</code>\n"
        f"🛡️ SL: <code>{sl:.6f}</code>\n"
        f"🎯 TP: <code>{tp:.6f}</code>\n"
        f"💵 Маржа: ${margin}\n"
        f"📈 Плече: {leverage}×"
    )
    await context.bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="HTML")

# --- Ціни зараз ---
async def prices_now(update, context):
    msg = "📊 Поточні ціни:\n"
    for symbol in symbols:
        price = get_price(symbol)
        if price:
            msg += f"{symbol}: <code>{price}</code>\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="HTML")

# --- Кнопки ---
async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Ціни зараз", callback_data="prices")],
        [InlineKeyboardButton("Змінити маржу", callback_data="change_margin")],
        [InlineKeyboardButton("Змінити плече", callback_data="change_leverage")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привіт! Обери опцію:", reply_markup=reply_markup)

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "prices":
        await prices_now(update, context)

# --- Команди ---
async def set_margin(update, context):
    global user_margin
    try:
        user_margin = float(context.args[0])
        await update.message.reply_text(f"✅ Маржу змінено на ${user_margin}")
    except:
        await update.message.reply_text("❌ Введи число. Наприклад:\n/set_margin 120")

async def set_leverage(update, context):
    global user_leverage
    try:
        symbol = context.args[0].upper()
        leverage = int(context.args[1])
        if symbol in symbols:
            user_leverage[symbol] = leverage
            await update.message.reply_text(f"✅ Плече для {symbol} змінено на {leverage}×")
        else:
            await update.message.reply_text("❌ Монету не знайдено.")
    except:
        await update.message.reply_text("❌ Формат:\n/set_leverage SOLUSDT 200")

# --- Основний цикл ---
async def check_market(context: ContextTypes.DEFAULT_TYPE):
    for symbol in symbols:
        price = get_price(symbol)
        if price:
            direction, entry, sl, tp = generate_signal(symbol, price)
            if direction:
                await send_signal(symbol, direction, entry, sl, tp, context)

# --- Запуск бота ---
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("set_margin", set_margin))
    app.add_handler(CommandHandler("set_leverage", set_leverage))
    app.job_queue.run_repeating(check_market, interval=60, first=5)
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())з
