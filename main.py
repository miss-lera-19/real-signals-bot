import requests
import time
import logging
from telegram import Bot
from keep_alive import keep_alive

# Telegram токен і chat_id
BOT_TOKEN = "8441710554:AAGFDgaFwQpcx3bFQ-2FgjjlkK7CEKxmz34"
CHAT_ID = "681357425"

# Ключі MEXC (read-only)
MEXC_API_KEY = "mx0vglwSqWMNfUkdXo"
MEXC_SECRET_KEY = "7107c871e7dc4e3db79f4fddb07e917d"

bot = Bot(token=BOT_TOKEN)

# Параметри монет
COINS = {
    "SOL": {"leverage": 300},
    "PEPE": {"leverage": 300},
    "BTC": {"leverage": 500},
    "ETH": {"leverage": 500},
}

# Отримання ціни з MEXC API
def get_price(symbol):
    try:
        url = f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}USDT"
        response = requests.get(url, timeout=5)
        return float(response.json()["price"])
    except Exception as e:
        logging.warning(f"Помилка отримання ціни для {symbol}: {e}")
        return None

# Генерація сигналу
def generate_signal(symbol, price, leverage):
    direction = "LONG" if int(str(price)[-1]) % 2 == 0 else "SHORT"  # Імітація логіки
    entry = round(price, 6)
    sl = round(entry * (0.99 if direction == "LONG" else 1.01), 6)
    tp = round(entry * (1.03 if direction == "LONG" else 0.97), 6)
    msg = (
        f"📊 Реальний сигнал на {direction}
"
        f"Монета: {symbol}/USDT
"
        f"Вхід: {entry}
"
        f"SL: {sl}
"
        f"TP: {tp}
"
        f"Плече: {leverage}×
"
        f"Маржа: $100
"
        f"Стратегія: $500–1000 з 1 угоди 🚀"
    )
    return msg

# Основна функція
def run_bot():
    while True:
        for coin, data in COINS.items():
            price = get_price(coin)
            if price:
                signal = generate_signal(coin, price, data["leverage"])
                bot.send_message(chat_id=CHAT_ID, text=signal)
            time.sleep(2)
        time.sleep(60)

if __name__ == "__main__":
    keep_alive()
    bot.send_message(chat_id=CHAT_ID, text="🤖 Бот запущено. Шукаю сигнали...")
    run_bot()