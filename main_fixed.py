
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

# Монети і плечі
COINS = {
    "SOL": {"leverage": 300},
    "PEPE": {"leverage": 300},
    "BTC": {"leverage": 500},
    "ETH": {"leverage": 500},
}

# Початкова маржа
margin = 100

# Отримання ціни
def get_price(symbol):
    try:
        url = f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}USDT"
        response = requests.get(url, timeout=5)
        return float(response.json()["price"])
    except Exception as e:
        logging.warning(f"Помилка отримання ціни для {symbol}: {e}")
        return None

# Визначення напрямку
def get_direction(symbol):
    prices = []
    for _ in range(3):
        price = get_price(symbol)
        if price:
            prices.append(price)
        time.sleep(1)
    if len(prices) < 2:
        return None
    return "LONG" if prices[-1] > prices[0] else "SHORT"

# Генерація сигналу
def generate_signal(symbol, price, leverage, direction, margin):
    tp_value = margin + 500
    sl_value = margin - 100
    tp = round(price * (tp_value / margin), 6)
    sl = round(price * (sl_value / margin), 6)

    msg = (
        f"🚨 Сигнал на {direction}
"
        f"Монета: {symbol}/USDT
"
        f"Ціна входу: {price}
"
        f"Stop Loss: {sl}
"
        f"Take Profit: {tp}
"
        f"Плече: {leverage}×
"
        f"Маржа: ${margin}
"
        f"🎯 Стратегія: $500–1000 з 1 угоди"
    )
    return msg

# Основна функція
def run_bot():
    global margin
    while True:
        for coin, data in COINS.items():
            price = get_price(coin)
            direction = get_direction(coin)
            if price and direction:
                signal = generate_signal(coin, price, data["leverage"], direction, margin)
                bot.send_message(chat_id=CHAT_ID, text=signal)
            time.sleep(2)
        time.sleep(60)

if __name__ == "__main__":
    keep_alive()
    bot.send_message(chat_id=CHAT_ID, text="🤖 Бот запущено. Пошук реальних сигналів...")
    run_bot()
