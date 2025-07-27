
import requests
import time
from telegram import Bot
from keep_alive import keep_alive
from threading import Thread

BOT_TOKEN = "8441710554:AAGFDgaFwQpcx3bFQ-2FgjjlkK7CEKxmz34"
CHAT_ID = "681357425"
MEXC_API_URL = "https://api.mexc.com/api/v3/ticker/price"

COINS = {
    "SOL": {"symbol": "SOLUSDT", "leverage": 300},
    "PEPE": {"symbol": "PEPEUSDT", "leverage": 300},
    "BTC": {"symbol": "BTCUSDT", "leverage": 500},
    "ETH": {"symbol": "ETHUSDT", "leverage": 500}
}

MARGIN = 100
bot = Bot(token=BOT_TOKEN)

# Отримання ціни
def get_price(symbol):
    try:
        response = requests.get(MEXC_API_URL, params={"symbol": symbol}, timeout=5)
        return float(response.json()["price"])
    except:
        return None

# Аналіз ринку
def analyze_market(symbol):
    prices = []
    for _ in range(3):
        price = get_price(symbol)
        if price:
            prices.append(price)
        time.sleep(1)
    if len(prices) < 3:
        return None
    direction = "LONG" if prices[-1] > prices[0] and prices[-1] > prices[-2] else "SHORT"
    return prices[-1], direction

# Розрахунок TP і SL
def calculate_tp_sl(price, direction, margin, leverage):
    target_profit = 500  # $500 прибутку
    risk = 100  # $100 ризику
    tp = price * (1 + target_profit / (margin * leverage)) if direction == "LONG" else price * (1 - target_profit / (margin * leverage))
    sl = price * (1 - risk / (margin * leverage)) if direction == "LONG" else price * (1 + risk / (margin * leverage))
    return round(tp, 6), round(sl, 6)

# Надсилання сигналу
def send_signal(coin, price, direction, tp, sl, leverage):
    msg = (
        f"📈 Сигнал на {direction}
"
        f"Монета: {coin}/USDT
"
        f"Ціна входу: {price}
"
        f"TP: {tp}
"
        f"SL: {sl}
"
        f"Маржа: ${MARGIN}
"
        f"Плече: {leverage}×
"
        f"🎯 Стратегія: $500–1000 з угоди"
    )
    bot.send_message(chat_id=CHAT_ID, text=msg)

# Цикл перевірки
def run_signals():
    while True:
        for coin, data in COINS.items():
            result = analyze_market(data["symbol"])
            if result:
                price, direction = result
                tp, sl = calculate_tp_sl(price, direction, MARGIN, data["leverage"])
                send_signal(coin, price, direction, tp, sl, data["leverage"])
            time.sleep(2)
        time.sleep(60)

if __name__ == "__main__":
    keep_alive()
    Thread(target=run_signals).start()
