import requests
import numpy as np
from telebot import TeleBot

# Telegram ayarları
TOKEN = '7698484488:AAHZWee_A-25rXzWGGzWueS420UZOm88_Bs'
CHAT_ID = '-1002549376225'
bot = TeleBot(TOKEN)

# Binance API URL
BASE_URL = 'https://fapi.binance.com'

# Sadece bu coinlerde çalışacak
ALLOWED_COINS = [
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

def get_klines(symbol, interval='1h', limit=100):
    url = f"{BASE_URL}/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = requests.get(url).json()
    return [float(kline[4]) for kline in data]

def calculate_rsi(data, period=14):
    delta = np.diff(data)
    gain = np.maximum(delta, 0)
    loss = np.maximum(-delta, 0)
    avg_gain = np.convolve(gain, np.ones((period,))/period, mode='valid')
    avg_loss = np.convolve(loss, np.ones((period,))/period, mode='valid')
    rs = avg_gain / (avg_loss + 1e-6)
    rsi = 100 - (100 / (1 + rs))
    return rsi[-1]

def calculate_ema(data, period):
    ema = []
    k = 2 / (period + 1)
    for i in range(len(data)):
        if i < period:
            ema.append(np.mean(data[:i+1]))
        else:
            ema.append(data[i] * k + ema[-1] * (1 - k))
    return ema[-1]

def calculate_macd(data):
    ema12 = calculate_ema(data, 12)
    ema26 = calculate_ema(data, 26)
    macd = ema12 - ema26
    signal = calculate_ema([macd]*9, 9)
    return macd, signal

def analyze_coin(symbol):
    intervals = ['15m', '1h', '4h', '1d']
    scores = []
    fiyat = None

    for interval in intervals:
        try:
            closes = get_klines(symbol, interval)
            if not closes:
                continue
            rsi = calculate_rsi(closes)
            ema50 = calculate_ema(closes, 50)
            ema200 = calculate_ema(closes, 200)
            macd, signal = calculate_macd(closes)

            fiyat = closes[-1]

            rsi_score = 9 if rsi < 30 else 2 if rsi > 70 else 6
            ema_score = 9 if closes[-1] > ema50 > ema200 else 2 if closes[-1] < ema50 < ema200 else 5
            macd_score = 8 if macd > signal else 3

            scores.append((rsi_score + ema_score + macd_score)/3)
        except:
            continue

    if not scores:
        return "Yeterli veri yok veya analiz yapılamadı."

    avg_score = round(np.mean(scores), 2)

    if avg_score >= 8:
        yorum = "🚀 Güçlü boğa trendi"
    elif avg_score >= 6.5:
        yorum = "📈 Boğa başlangıcı"
    elif avg_score >= 4:
        yorum = "⚖️ Piyasa nötr"
    else:
        yorum = "📉 Ayı baskısı"

    return f"""📊 Teknik Analiz: {symbol}
Fiyat: {round(fiyat, 2)} USDT
———————————————
🎯 Ortalama Puan: {avg_score}/10
💬 Yorum: {yorum}
"""

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    coin = message.text.strip().upper()
    if not coin.endswith("USDT"):
        coin += "USDT"
    if coin not in ALLOWED_COINS:
        bot.send_message(message.chat.id, f"❌ {coin} desteklenen coin listesinde yok.")
        return
    sonuc = analyze_coin(coin)
    bot.send_message(message.chat.id, sonuc)

print("Bot çalışıyor...")
bot.polling()
