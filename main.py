import requests
import time
import numpy as np
from datetime import datetime
from telebot import TeleBot

# Telegram ayarları
TOKEN = '7698484488:AAHZWee_A-25rXzWGGzWueS420UZOm88_Bs'
CHAT_ID = '-1002549376225'
bot = TeleBot(TOKEN)

# Binance API URL
BASE_URL = 'https://fapi.binance.com'

# Analiz yapılacak coin listesi (sadece Binance Futures’ta listeli coinler)
COIN_LIST = [
    'BTCUSDT', 'ETHUSDT', 'BCHUSDT', 'XRPUSDT', 'LTCUSDT', 'TRXUSDT', 'ETCUSDT', 'LINKUSDT',
    'XLMUSDT', 'ADAUSDT', 'XMRUSDT', 'DASHUSDT', 'ZECUSDT', 'XTZUSDT', 'BNBUSDT', 'ATOMUSDT',
    'ONTUSDT', 'IOTAUSDT', 'BATUSDT', 'VETUSDT', 'NEOUSDT', 'QTUMUSDT', 'IOSTUSDT', 'THETAUSDT',
    'ALGOUSDT', 'ZILUSDT', 'KNCUSDT', 'ZRXUSDT', 'COMPUSDT', 'DOGEUSDT', 'SXPUSDT', 'KAVAUSDT',
    'BANDUSDT', 'RLCUSDT', 'MKRUSDT', 'SNXUSDT', 'DOTUSDT', 'DEFIUSDT', 'YFIUSDT', 'CRVUSDT',
    'TRBUSDT', 'RUNEUSDT', 'SUSHIUSDT', 'EGLDUSDT', 'SOLUSDT', 'ICXUSDT', 'STORJUSDT', 'UNIUSDT',
    'AVAXUSDT', 'ENJUSDT', 'FLMUSDT', 'KSMUSDT', 'NEARUSDT', 'AAVEUSDT', 'FILUSDT', 'RSRUSDT',
    'LRCUSDT', 'BELUSDT', 'AXSUSDT', 'ALPHAUSDT', 'ZENUSDT', 'SKLUSDT', 'GRTUSDT', '1INCHUSDT',
    'CHZUSDT', 'SANDUSDT', 'ANKRUSDT', 'RVNUSDT', 'SFPUSDT', 'COTIUSDT', 'CHRUSDT', 'MANAUSDT',
    'ALICEUSDT', 'HBARUSDT', 'ONEUSDT', 'DENTUSDT', 'CELRUSDT', 'HOTUSDT', 'MTLUSDT', 'OGNUSDT',
    'NKNUSDT', '1000SHIBUSDT', 'BAKEUSDT', 'GTCUSDT', 'BTCDOMUSDT', 'IOTXUSDT', 'C98USDT',
    'MASKUSDT', 'ATAUSDT', 'DYDXUSDT', '1000XECUSDT', 'GALAUSDT', 'CELOUSDT', 'ARUSDT', 'ARPAUSDT',
    'CTSIUSDT', 'LPTUSDT', 'ENSUSDT', 'PEOPLEUSDT', 'ROSEUSDT', 'DUSKUSDT', 'FLOWUSDT', 'IMXUSDT',
    'API3USDT', 'GMTUSDT', 'APEUSDT', 'WOOUSDT', 'JASMYUSDT', 'OPUSDT', 'INJUSDT', 'STGUSDT',
    'SPELLUSDT', '1000LUNCUSDT', 'LUNA2USDT', 'LDOUSDT', 'ICPUSDT', 'APTUSDT', 'QNTUSDT', 'FETUSDT',
    'FXSUSDT', 'HOOKUSDT', 'MAGICUSDT', 'TUSDT', 'HIGHUSDT', 'MINAUSDT', 'ASTRUSDT', 'PHBUSDT',
    'GMXUSDT', 'CFXUSDT', 'STXUSDT', 'ACHUSDT', 'SSVUSDT', 'CKBUSDT', 'PERPUSDT', 'TRUUSDT',
    'LQTYUSDT', 'USDCUSDT', 'IDUSDT', 'ARBUSDT', 'JOEUSDT', 'TLMUSDT', 'LEVERUSDT', 'RDNTUSDT',
    'HFTUSDT', 'XVSUSDT', 'ETHBTC', 'BLURUSDT', 'EDUUSDT', 'SUIUSDT', '1000PEPEUSDT'
]

# RSI hesapla
def calculate_rsi(data, period=14):
    delta = np.diff(data)
    gain = np.maximum(delta, 0)
    loss = np.maximum(-delta, 0)
    avg_gain = np.convolve(gain, np.ones((period,))/period, mode='valid')
    avg_loss = np.convolve(loss, np.ones((period,))/period, mode='valid')
    rs = avg_gain / (avg_loss + 1e-6)
    rsi = 100 - (100 / (1 + rs))
    return rsi[-1]

# EMA hesapla
def calculate_ema(data, period):
    ema = []
    k = 2 / (period + 1)
    for i in range(len(data)):
        if i < period:
            ema.append(np.mean(data[:i+1]))
        else:
            ema.append(data[i] * k + ema[-1] * (1 - k))
    return ema[-1]

# MACD hesapla
def calculate_macd(data):
    ema12 = calculate_ema(data, 12)
    ema26 = calculate_ema(data, 26)
    macd = ema12 - ema26
    signal = calculate_ema([macd]*9, 9)
    return macd, signal

# Binance’tan veri al
def get_klines(symbol, interval='1h', limit=100):
    url = f"{BASE_URL}/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    return [float(candle[4]) for candle in data]

# Telegram’a gönder
def send_to_telegram(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

# Teknik analiz
def analyze(symbol):
    intervals = ['15m', '1h', '4h', '1d']
    rsi_scores = []
    macd_scores = []
    ema_scores = []

    for interval in intervals:
        try:
            closes = get_klines(symbol, interval)
            if len(closes) < 30:
                continue
            rsi = calculate_rsi(closes)
            ema50 = calculate_ema(closes, 50)
            ema200 = calculate_ema(closes, 200)
            macd, signal = calculate_macd(closes)

            # RSI puanı
            if rsi > 70:
                rsi_score = 2
            elif rsi < 30:
                rsi_score = 2
            else:
                rsi_score = 1

            # MACD puanı
            macd_score = 2 if macd > signal else 1

            # EMA puanı
            ema_score = 2 if closes[-1] > ema50 and closes[-1] > ema200 else 1

            rsi_scores.append(rsi_score)
            macd_scores.append(macd_score)
            ema_scores.append(ema_score)
        except:
            continue

    if not rsi_scores:
        return

    total_score = np.mean(rsi_scores + macd_scores + ema_scores) * 10 / 6
    total_score = round(total_score, 2)

    if total_score >= 8:
        yorum = "🚀 Piyasa güçlü boğa eğiliminde"
    elif total_score >= 6:
        yorum = "📈 Piyasa boğa başlangıcında"
    elif total_score >= 4:
        yorum = "⚖️ Piyasa nötr"
    elif total_score >= 2:
        yorum = "📉 Piyasa ayı başlangıcında"
    else:
        yorum = "🐻 Güçlü ayı piyasası"

    fiyat = get_klines(symbol)[-1]
    mesaj = f"""📊 Teknik Analiz: {symbol}
Fiyat: {fiyat} USDT
———————————————
🔹 RSI Puanları: {rsi_scores}
🔹 MACD Puanları: {macd_scores}
🔹 EMA Puanları: {ema_scores}
———————————————
🎯 Ortalama Puan: {total_score}/10
💬 Yorum: {yorum}
"""
    send_to_telegram(mesaj)

# Tüm coinleri sırayla analiz et
for coin in COIN_LIST:
    analyze(coin)
    time.sleep(2)
