import requests
import pandas as pd
import numpy as np

# Telegram bilgileri
TELEGRAM_TOKEN = "7759276451:AAF0Xphio-TjtYyFIzahQrG3fU-qdNQuBEw"
CHAT_ID = "-1002549376225"

# Binance'ten kapanış fiyatı çekme
def get_klines(symbol, interval, limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    closes = [float(i[4]) for i in data]
    return closes

# EMA puanlama
def get_ema_score(closes):
    prices = pd.Series(closes)
    ema_20 = prices.ewm(span=20).mean().iloc[-1]
    ema_50 = prices.ewm(span=50).mean().iloc[-1]
    ema_200 = prices.ewm(span=200).mean().iloc[-1]
    current = prices.iloc[-1]
    score = 0
    if current > ema_200:
        score += 1
    if current > ema_50:
        score += 1
    if current > ema_20:
        score += 1
    return score

# RSI puanlama
def get_rsi_score(closes):
    prices = pd.Series(closes)
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    latest_rsi = rsi.iloc[-1]

    if latest_rsi > 70:
        return 0  # Aşırı alım
    elif latest_rsi > 60:
        return 1
    elif latest_rsi > 50:
        return 2
    else:
        return 3  # Aşırı satım

# MACD hesaplama
def calculate_macd(close_prices, fast=12, slow=26, signal=9):
    exp1 = close_prices.ewm(span=fast, adjust=False).mean()
    exp2 = close_prices.ewm(span=slow, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return float(macd_line.iloc[-1]), float(signal_line.iloc[-1]), float(histogram.iloc[-1])

# MACD puanlama
def score_macd(macd_line, signal_line, histogram):
    if macd_line > signal_line and histogram > 0:
        if histogram > 50:
            return 3
        elif histogram > 20:
            return 2
        else:
            return 1
    elif macd_line < signal_line and histogram < 0:
        if histogram < -50:
            return 0
        elif histogram < -20:
            return 1
        else:
            return 2
    else:
        return 1  # Nötr/yatay

# Ortalama puanı hesapla
def analyze_symbol(symbol):
    intervals = ["15m", "1h", "4h", "1d"]
    rsi_scores, macd_scores, ema_scores = [], [], []

    for interval in intervals:
        try:
            closes = get_klines(symbol, interval, limit=100)
            closes_series = pd.Series(closes)

            rsi = get_rsi_score(closes)
            ema = get_ema_score(closes)
            macd_line, signal_line, hist = calculate_macd(closes_series)
            macd = score_macd(macd_line, signal_line, hist)

            rsi_scores.append(rsi)
            ema_scores.append(ema)
            macd_scores.append(macd)
        except Exception as e:
            print(f"{symbol} {interval} analiz hatası: {e}")
            rsi_scores.append(0)
            ema_scores.append(0)
            macd_scores.append(0)

    avg_score = round((sum(rsi_scores) + sum(macd_scores) + sum(ema_scores)) / 12, 2)

    # Yorumu belirle
    if avg_score >= 7:
        yorum = "🐂 Boğa piyasası"
    elif avg_score <= 3:
        yorum = "🐻 Ayı piyasası"
    else:
        yorum = "⚖️ Kararsız bölge"

    # Anlık fiyat
    try:
        ticker = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}").json()
        price = float(ticker['price'])
    except:
        price = 0

    # Mesajı oluştur
    message = f"""
📊 Teknik Analiz: {symbol}
Fiyat: {price} USDT
———————————————
🔹 RSI Puanları: {rsi_scores}
🔹 MACD Puanları: {macd_scores}
🔹 EMA Puanları: {ema_scores}
———————————————
🎯 Ortalama Puan: {avg_score}/10
💬 Yorum: {yorum}
"""
    return message

# Telegram'a mesaj gönder
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)

# Komutla analiz başlat
if __name__ == "__main__":
    symbol = "BTCUSDT"
    msg = analyze_symbol(symbol)
    send_telegram_message(msg)
