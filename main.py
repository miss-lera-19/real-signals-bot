
import time
import requests
from telegram import Bot
from keep_alive import keep_alive

BOT_TOKEN = "8441710554:AAGFDgaFwQpcx3bFQ-2FgjjlkK7CEKxmz34"
CHAT_ID = "681357425"

bot = Bot(token=BOT_TOKEN)

symbols = {
    "SOL": {"leverage": 300},
    "PEPE": {"leverage": 300},
    "BTC": {"leverage": 500},
    "ETH": {"leverage": 500}
}

def get_price(symbol):
    try:
        url = f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}USDT"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data["price"])
    except Exception:
        return None

def send_signal(symbol, price, direction):
    leverage = symbols[symbol]["leverage"]
    margin = 100
    sl = price * 0.99 if direction == "LONG" else price * 1.01
    tp = price * 1.05 if direction == "LONG" else price * 0.95

    message = (
        f"{symbol}/USDT {direction} сигнал\n"
        f"Вхід: {price:.4f}\n"
        f"SL: {sl:.4f}\n"
        f"TP: {tp:.4f}\n"
        f"Маржа: ${margin}\n"
        f"Плече: {leverage}x\n\n"
        f"Ринок перевірено: {time.strftime('%H:%M:%S')}"
    )
    bot.send_message(chat_id=CHAT_ID, text=message)

def analyze_market():
    for symbol in symbols:
        price = get_price(symbol)
        if price:
            direction = "LONG" if int(time.time()) % 2 == 0 else "SHORT"
            send_signal(symbol, price, direction)
        else:
            bot.send_message(chat_id=CHAT_ID, text=f"Не вдалося отримати ціну для {symbol}/USDT.")

if __name__ == "__main__":
    keep_alive()
    while True:
        try:
            analyze_market()
            time.sleep(60)
        except Exception as e:
            bot.send_message(chat_id=CHAT_ID, text=f"Помилка: {e}")
            time.sleep(60)
