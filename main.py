import requests
import numpy as np
import telebot
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from coin_list import coin_list

bot = telebot.TeleBot(TELEGRAM_TOKEN)

intervals = {
    "15m": "15 dakika",
    "1h": "1 saat",
    "4h": "4 saat",
    "1d": "1 gün"
}

def get_klines(symbol, interval, limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    return response.json()

def calculate_rsi(close_prices, period=14):
    deltas = np.diff(close_prices)
    seed = deltas[:period]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(close_prices, fast=12, slow=26, signal=9):
    exp1 = np.mean(close_prices[-fast:])
    exp2 = np.mean(close_prices[-slow:])
    macd_line = exp1 - exp2
    signal_line = np.mean(close_prices[-signal:])
    return macd_line, signal_line

def calculate_ema(close_prices, period):
    return np.mean(close_prices[-period:])

def score_rsi(rsi):
    if rsi > 70:
        return 3
    elif rsi > 60:
        return 2
    elif rsi > 50:
        return 1
    else:
        return 0

def score_macd(macd, signal):
    return 3 if macd > signal else 0

def score_ema(last_price, ema50, ema200):
    if last_price > ema50 and last_price > ema200:
        return 3
    elif last_price > ema50 or last_price > ema200:
        return 2
    else:
        return 0

def yorumla(puan):
    if puan >= 8:
        return "🚀 Boğa piyasası"
    elif puan >= 5:
        return "⚖️ Nötr"
    else:
        return "🐻 Ayı piyasası"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    coin = message.text.upper()

    if coin not in coin_list:
        bot.send_message(message.chat.id, f"❌ '{coin}' desteklenen coin listesinde yok.")
        return

    rsi_scores, macd_scores, ema_scores = [], [], []
    for interval in intervals:
        klines = get_klines(coin, interval)
        close_prices = [float(k[4]) for k in klines]
        last_price = close_prices[-1]
        rsi = calculate_rsi(close_prices)
        macd, signal = calculate_macd(close_prices)
        ema50 = calculate_ema(close_prices, 50)
        ema200 = calculate_ema(close_prices, 100)

        rsi_scores.append(score_rsi(rsi))
        macd_scores.append(score_macd(macd, signal))
        ema_scores.append(score_ema(last_price, ema50, ema200))

    all_scores = rsi_scores + macd_scores + ema_scores
    avg_score = round(sum(all_scores) / len(all_scores), 2)
    yorum = yorumla(avg_score)

    msg = f"""📊 Teknik Analiz: {coin}
Fiyat: {round(last_price, 4)} USDT
———————————————
🔹 RSI Puanları: {rsi_scores}
🔹 MACD Puanları: {macd_scores}
🔹 EMA Puanları: {ema_scores}
———————————————
🎯 Ortalama Puan: {avg_score}/10
💬 Yorum: {yorum}
"""
    bot.send_message(message.chat.id, msg)

bot.polling()
