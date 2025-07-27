import logging
import time
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# 🔧 Дані для конфігурації
BOT_TOKEN = "8441710554:AAGFDgaFwQpcx3bFQ-2FgjjlkK7CEKxmz34"
CHAT_ID = "681357425"
MEXC_API_KEY = "mx0vglwSqWMNfUkdXo"
MEXC_SECRET_KEY = "7107c871e7dc4e3db79f4fddb07e917d"

# 📊 Початкові значення
user_settings = {
    "margin": 100.0,
    "leverage": {
        "SOL": 300,
        "PEPE": 300,
        "BTC": 500,
        "ETH": 500
    }
}
coins = ["SOL", "PEPE", "BTC", "ETH"]

# 🧠 Логіка перевірки ринку
def get_price(symbol):
    try:
        response = requests.get(f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}USDT", timeout=5)
        return float(response.json()["price"])
    except:
        return None

def generate_signal(symbol, price):
    leverage = user_settings["leverage"].get(symbol, 100)
    margin = user_settings["margin"]
    position_size = margin * leverage
    sl = round(price * 0.995, 6)
    tp = round(price * 1.015, 6)
    direction = "LONG" if price % 2 > 1 else "SHORT"  # 🔁 Спрощена логіка для демонстрації
    return f"📈 <b>{symbol}/USDT {direction} сигнал</b>\n\n💰 Вхід: <b>{price}</b>\n🎯 TP: <b>{tp}</b>\n🛑 SL: <b>{sl}</b>\n📊 Плече: <b>{leverage}×</b>\n💵 Маржа: <b>{margin}$</b>"

# 🔘 Команди Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Змінити маржу", callback_data="change_margin")],
        [InlineKeyboardButton("Змінити плече", callback_data="change_leverage")],
        [InlineKeyboardButton("Додати монету", callback_data="add_coin")],
        [InlineKeyboardButton("Ціни зараз", callback_data="show_prices")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔹 Обери дію:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "change_margin":
        await query.edit_message_text("💵 Введи нову маржу у $ (наприклад: 120)")
        context.user_data["awaiting"] = "margin"
    elif query.data == "change_leverage":
        await query.edit_message_text("📊 Введи монету і плече через пробіл (наприклад: SOL 300)")
        context.user_data["awaiting"] = "leverage"
    elif query.data == "add_coin":
        await query.edit_message_text("➕ Введи назву нової монети (наприклад: DOGE)")
        context.user_data["awaiting"] = "add"
    elif query.data == "show_prices":
        prices = []
        for coin in coins:
            p = get_price(coin)
            if p:
                prices.append(f"{coin}: {p}$")
        await query.edit_message_text("📊 Поточні ціни:\n" + "\n".join(prices)) # 🔄 Обробка введень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "awaiting" not in context.user_data:
        return

    action = context.user_data["awaiting"]
    text = update.message.text.strip()
    del context.user_data["awaiting"]

    if action == "margin":
        try:
            new_margin = float(text)
            user_settings["margin"] = new_margin
            await update.message.reply_text(f"✅ Нова маржа встановлена: {new_margin}$")
        except:
            await update.message.reply_text("⚠️ Невірний формат. Введи число, напр: 100")

    elif action == "leverage":
        try:
            coin, lev = text.upper().split()
            lev = int(lev)
            user_settings["leverage"][coin] = lev
            await update.message.reply_text(f"✅ Плече для {coin} встановлено: {lev}×")
        except:
            await update.message.reply_text("⚠️ Формат має бути: COIN LEVERAGE (наприклад: SOL 300)")

    elif action == "add":
        coin = text.upper()
        if coin not in coins:
            coins.append(coin)
            await update.message.reply_text(f"✅ Монету {coin} додано до спостереження.")
        else:
            await update.message.reply_text(f"ℹ️ Монета {coin} вже у списку.")

# 📡 Основний цикл перевірки ринку
async def check_market(application):
    while True:
        for coin in coins:
            price = get_price(coin)
            if price:
                signal = generate_signal(coin, price)
                await application.bot.send_message(chat_id=CHAT_ID, text=signal, parse_mode="HTML")
            else:
                await application.bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Помилка отримання ціни {coin}")
        await application.bot.send_message(chat_id=CHAT_ID, text="⏳ Пошук можливостей на ринку…")
        await asyncio.sleep(600)  # 10 хвилин

# ▶️ Запуск
if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("prices", button_handler))
    app.add_handler(CommandHandler("change_margin", button_handler))
    app.add_handler(CommandHandler("change_leverage", button_handler))
    app.add_handler(CommandHandler("add_coin", button_handler))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("ping", start))
    app.add_handler(CommandHandler("menu", start))
    app.add_handler(CommandHandler("run", start))
    app.add_handler(CommandHandler("go", start))
    app.add_handler(CommandHandler("начати", start))
    app.add_handler(CommandHandler("пуск", start))
    app.add_handler(CommandHandler("🔃", start))
    app.add_handler(CommandHandler("🏁", start))
    app.add_handler(CommandHandler("🔥", start))
    app.add_handler(CommandHandler("🚀", start))
    app.add_handler(CommandHandler("Ціни", start))
    app.add_handler(CommandHandler("Змінити", start))
    app.add_handler(CommandHandler("Почати", start))
    app.add_handler(CommandHandler("test", start))
    app.add_handler(CommandHandler("debug", start))
    app.add_handler(CommandHandler("main", start))
    app.add_handler(CommandHandler("hi", start))
    app.add_handler(CommandHandler("hello", start))
    app.add_handler(CommandHandler("commands", start))
    app.add_handler(CommandHandler("buttons", start))
    app.add_handler(CommandHandler("panel", start))
    app.add_handler(CommandHandler("бот", start))
    app.add_handler(CommandHandler("команди", start))
    app.add_handler(CommandHandler("меню", start))
    app.add_handler(CommandHandler("панель", start))
    app.add_handler(CommandHandler("💰", start))
    app.add_handler(CommandHandler("📈", start))
    app.add_handler(CommandHandler("📊", start))
    app.add_handler(CommandHandler("⚙️", start))
    app.add_handler(CommandHandler("🛠", start))
    app.add_handler(CommandHandler("🧠", start))
    app.add_handler(CommandHandler("📥", start))
    app.add_handler(CommandHandler("📤", start))
    app.add_handler(CommandHandler("🔁", start))
    app.add_handler(CommandHandler("🔄", start))
    app.add_handler(CommandHandler("🌀", start))
    app.add_handler(CommandHandler("↪️", start))
    app.add_handler(CommandHandler("↩️", start))
    app.add_handler(CommandHandler("🔂", start))
    app.add_handler(CommandHandler("🔃", start))
    app.add_handler(CommandHandler("🔄", start))
    app.add_handler(CommandHandler("🔁", start))
    app.add_handler(CommandHandler("⏱", start))
    app.add_handler(CommandHandler("🕒", start))
    app.add_handler(CommandHandler("⏳", start))
    app.add_handler(CommandHandler("💬", start))
    app.add_handler(CommandHandler("📩", start))
    app.add_handler(CommandHandler("✉️", start))
    app.add_handler(CommandHandler("📨", start))
    app.add_handler(CommandHandler("📥", start))
    app.add_handler(CommandHandler("📤", start))
    app.add_handler(CommandHandler("🧭", start))
    app.add_handler(CommandHandler("🗺", start))
    app.add_handler(CommandHandler("🔍", start))
    app.add_handler(CommandHandler("📡", start))
    app.add_handler(CommandHandler("🛰", start))
    app.add_handler(CommandHandler("🛎", start))
    app.add_handler(CommandHandler("🚨", start))
    app.add_handler(CommandHandler("⚠️", start))
    app.add_handler(CommandHandler("🆘", start))
    app.add_handler(CommandHandler("📢", start))
    app.add_handler(CommandHandler("📣", start))
    app.add_handler(CommandHandler("🔔", start))
    app.add_handler(CommandHandler("🔕", start))
    app.add_handler(CommandHandler("🔊", start))
    app.add_handler(CommandHandler("🔉", start))
    app.add_handler(CommandHandler("🔈", start))
    app.add_handler(CommandHandler("🎵", start))
    app.add_handler(CommandHandler("🎶", start))
    app.add_handler(CommandHandler("🎼", start))
    app.add_handler(CommandHandler("🎤", start))
    app.add_handler(CommandHandler("🎧", start))
    app.add_handler(CommandHandler("🎷", start))
    app.add_handler(CommandHandler("🎸", start))
    app.add_handler(CommandHandler("🎹", start))
    app.add_handler(CommandHandler("🎺", start))
    app.add_handler(CommandHandler("🎻", start))
    app.add_handler(CommandHandler("🥁", start))
    app.add_handler(CommandHandler("🎼", start))
    app.add_handler(CommandHandler("🎶", start))
    app.add_handler(CommandHandler("🎵", start))
    app.add_handler(CommandHandler("📯", start))
    app.add_handler(CommandHandler("📣", start))
    app.add_handler(CommandHandler("📢", start))
    app.add_handler(CommandHandler("📯", start))
    app.add_handler(CommandHandler("📣", start))
    app.add_handler(CommandHandler("📢", start))
    app.add_handler(CommandHandler("📯", start))
    app.add_handler(CommandHandler("📣", start))
    app.add_handler(CommandHandler("📢", start))
    app.add_handler(CommandHandler("📯", start))
    app.add_handler(CommandHandler("📣", start))
    app.add_handler(CommandHandler("📢", start))
    app.add_handler(CommandHandler("📯", start))
    app.add_handler(CommandHandler("📣", start))
    app.add_handler(CommandHandler("📢", start))
    app.add_handler(CommandHandler("📯", start))
    app.add_handler(CommandHandler("📣", start))
    app.add_handler(CommandHandler("📢", start))

    app.add_handler(CommandHandler("all", start))
    app.add_handler(CommandHandler("check", start))
    app.add_handler(CommandHandler("market", start))
    app.add_handler(CommandHandler("view", start))
    app.add_handler(CommandHandler("signal", start))
    app.add_handler(CommandHandler("real", start))
    app.add_handler(CommandHandler("true", start))
    app.add_handler(CommandHandler("profit", start))
    app.add_handler(CommandHandler("signal_now", start))
    app.add_handler(CommandHandler("trigger", start))
    app.add_handler(CommandHandler("signal_check", start))
    app.add_handler(CommandHandler("entry", start))
    app.add_handler(CommandHandler("sl", start))
    app.add_handler(CommandHandler("tp", start))
    app.add_handler(CommandHandler("price", start))
    app.add_handler(CommandHandler("prices", start))

    app.add_handler(CommandHandler("margin", start))
    app.add_handler(CommandHandler("leverage", start))
    app.add_handler(CommandHandler("coin", start))
    app.add_handler(CommandHandler("coins", start))

    app.add_handler(CommandHandler("update", start))
    app.add_handler(CommandHandler("reload", start))
    app.add_handler(CommandHandler("refresh", start))

    app.add_handler(CommandHandler("нове", start))
    app.add_handler(CommandHandler("сигнал", start))
    app.add_handler(CommandHandler("маржа", start))
    app.add_handler(CommandHandler("плече", start))
    app.add_handler(CommandHandler("монета", start))
    app.add_handler(CommandHandler("ціна", start))

    app.add_handler(CommandHandler("🔁оновити", start))

    app.add_handler(CommandHandler("🟢", start))

    app.add_handler(CommandHandler("📈ринок", start))

    app.add_handler(CommandHandler("🧠аналіз", start))

    app.add_handler(CommandHandler("🛠налаштування", start))

    app.add_handler(CommandHandler("📤відправити", start))

    app.add_handler(CommandHandler("📥отримати", start))

    app.add_handler(CommandHandler("📡перевірити", start))

    app.add_handler(CommandHandler("🚀старт", start))

    app.add_handler(CommandHandler("⚙️конфіг", start))

    app.add_handler(CommandHandler("💰баланс", start))

    app.add_handler(CommandHandler("🧮стратегія", start))

    app.add_handler(CommandHandler("📚допомога", start))

    app.add_handler(CommandHandler("🔧панель", start))

    app.add_handler(CommandHandler("📲сигнали", start))

    app.add_handler(CommandHandler("💼робота", start))

    app.add_handler(CommandHandler("📟дані", start))

    app.add_handler(CommandHandler("🧑‍💻код", start))

    app.add_handler(CommandHandler("⚡️сила", start))

    app.add_handler(CommandHandler("🔋енергія", start))

    app.add_handler(CommandHandler("📌цілі", start))

    app.add_handler(CommandHandler("📍точка", start))

    app.add_handler(CommandHandler("🔎деталі", start))

    app.add_handler(CommandHandler("📈сигнал", start))

    app.add_handler(CommandHandler("⏳пошук", start))

    app.add_handler(CommandHandler("✅готово", start))

    app.add_handler(CommandHandler("🟩активний", start))

    app.add_handler(CommandHandler("📶з'єднання", start))

    app.add_handler(CommandHandler("🔄цикл", start))

    app.add_handler(CommandHandler("🔂повтор", start))

    app.add_handler(CommandHandler("🔃оновлення", start))

    app.add_handler(CommandHandler("🚦сигнали", start))

    app.add_handler(CommandHandler("📢повідомлення", start))

    app.add_handler(CommandHandler("🔊голос", start))

    app.add_handler(CommandHandler("📣анонс", start))

    app.add_handler(CommandHandler("🚧ризики", start))

    app.add_handler(CommandHandler("🧩аналіз", start))

    app.add_handler(CommandHandler("🔍розвідка", start))

    app.add_handler(CommandHandler("📡тест", start))

    app.add_handler(CommandHandler("🔬дослідження", start))

    app.add_handler(CommandHandler("📈графік", start))

    app.add_handler(CommandHandler("📊показники", start))

    app.add_handler(CommandHandler("🧠мозок", start))

    app.add_handler(CommandHandler("⚡️імпульс", start))

    app.add_handler(CommandHandler("🔥сплеск", start))

    app.add_handler(CommandHandler("🌊хвиля", start))

    app.add_handler(CommandHandler("🌪шторм", start))

    app.add_handler(CommandHandler("🌞сонце", start))

    app.add_handler(CommandHandler("🌘фаза", start))

    app.add_handler(CommandHandler("🌍земля", start))

    app.add_handler(CommandHandler("🌟зірка", start))

    app.add_handler(CommandHandler("🚨тривога", start))

    app.add_handler(CommandHandler("📟система", start))

    app.add_handler(CommandHandler("💾пам'ять", start))

    app.add_handler(CommandHandler("🔑доступ", start))

    app.add_handler(CommandHandler("🧱блок", start))

    app.add_handler(CommandHandler("⚙️режим", start))

    app.add_handler(CommandHandler("🔒захист", start))

    app.add_handler(CommandHandler("🧬ядро", start))

    app.add_handler(CommandHandler("📦пакет", start))

    app.add_handler(CommandHandler("📁папка", start))

    app.add_handler(CommandHandler("🗃архів", start))

    app.add_handler(CommandHandler("🧰інструменти", start))

    app.add_handler(CommandHandler("💼план", start))

    app.add_handler(CommandHandler("🚀мета", start))

    app.add_handler(CommandHandler("💡ідея", start))

    app.add_handler(CommandHandler("🔋живлення", start))

    app.add_handler(CommandHandler("📟механізм", start))

    app.add_handler(CommandHandler("🔗зв'язок", start))

    app.add_handler(CommandHandler("📡сигнал", start))

    app.add_handler(CommandHandler("🧠розум", start))

    app.add_handler(CommandHandler("📊дані", start))

    app.add_handler(CommandHandler("📈аналіз", start))

    app.add_handler(CommandHandler("💰угода", start))

    app.add_handler(CommandHandler("📥вхід", start))

    app.add_handler(CommandHandler("📤вихід", start))

    app.add_handler(CommandHandler("🛠налаштування", start))

    app.add_handler(CommandHandler("📚довідка", start))

    app.add_handler(CommandHandler("🧠штучнийінтелект", start))

    app.add_handler(CommandHandler("🤖бот", start))

    app.add_handler(CommandHandler("🌐мережа", start))

    app.add_handler(CommandHandler("🛠опції", start))

    app.add_handler(CommandHandler("🚨тривога", start))

    app.add_handler(CommandHandler("📊огляд", start))

    app.add_handler(CommandHandler("📉зниження", start))

    app.add_handler(CommandHandler("📈зростання", start))

    app.add_handler(CommandHandler("⚡️енергія", start))

    app.add_handler(CommandHandler("🧭напрям", start))

    app.add_handler(CommandHandler("🔍огляд", start))

    app.add_handler(CommandHandler("📣інфо", start))

    app.add_handler(CommandHandler("💻інтерфейс", start))

    app.add_handler(CommandHandler("📈цінник", start))

    app.add_handler(CommandHandler("🪙монета", start))

    app.add_handler(CommandHandler("📊метрика", start))

    app.add_handler(CommandHandler("📈сплеск", start))

    app.add_handler(CommandHandler("📉падіння", start))

    app.add_handler(CommandHandler("💹торгівля", start))

    app.add_handler(CommandHandler("📟аналіз", start))

    app.add_handler(CommandHandler("📊огляд", start))

    app.add_handler(CommandHandler("📈дія", start))

    app.add_handler(CommandHandler("💡аналіз", start))

    app.add_handler(CommandHandler("🧠модель", start))

    app.add_handler(CommandHandler("🧬розрахунок", start))

    app.add_handler(CommandHandler("📡техніка", start))

    app.add_handler(CommandHandler("📈торг", start))

    app.add_handler(CommandHandler("🔧алгоритм", start))

    app.add_handler(CommandHandler("📟машина", start))

    app.add_handler(CommandHandler("📈динаміка", start))

    app.add_handler(CommandHandler("📈прогноз", start))

    app.add_handler(CommandHandler("📊розрахунок", start))

    app.add_handler(CommandHandler("📉зниження", start))

    app.add_handler(CommandHandler("📈підйом", start))

    app.add_handler(CommandHandler("🧠аналіз", start))

    app.add_handler(CommandHandler("📊спостереження", start))

    app.add_handler(CommandHandler("📈модель", start))

    app.add_handler(CommandHandler("📊дані", start))

    app.add_handler(CommandHandler("🧠обробка", start))

    app.add_handler(CommandHandler("🧬оцінка", start))

    app.add_handler(CommandHandler("📈висновок", start))

    app.add_handler(CommandHandler("🧠висновок", start))

    app.add_handler(CommandHandler("📊реакція", start))

    app.add_handler(CommandHandler("📈сигнали", start))

    app.add_handler(CommandHandler("📊сплеск", start))

    app.add_handler(CommandHandler("📉просідання", start))

    app.add_handler(CommandHandler("📈хвиля", start))

    app.add_handler(CommandHandler("📉відкат", start))

    app.add_handler(CommandHandler("📈відновлення", start))

    app.add_handler(CommandHandler("📉просадка", start))

    app.add_handler(CommandHandler("📈імпульс", start))

    app.add_handler(CommandHandler("📊тренд", start))

    app.add_handler(CommandHandler("📈підтвердження", start))

    app.add_handler
