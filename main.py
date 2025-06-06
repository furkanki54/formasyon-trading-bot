import requests
import pandas as pd
import ta
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, BINANCE_BASE_URL

URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def get_ohlcv(symbol, interval="1h", limit=100):
    url = f"{BINANCE_BASE_URL}/api/v3/klines"
    params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
    res = requests.get(url, params=params)
    data = res.json()
    df = pd.DataFrame(data, columns=[
        "time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["close"] = df["close"].astype(float)
    return df

def analyze(symbol, interval):
    try:
        df = get_ohlcv(symbol, interval)
        df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()
        df["ema50"] = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator()
        df["ema200"] = ta.trend.EMAIndicator(df["close"], window=200).ema_indicator()
        macd = ta.trend.MACD(df["close"])
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()

        rsi = df["rsi"].iloc[-1]
        ema50 = df["ema50"].iloc[-1]
        ema200 = df["ema200"].iloc[-1]
        macd_val = df["macd"].iloc[-1]
        macd_sig = df["macd_signal"].iloc[-1]
        price = df["close"].iloc[-1]

        # RSI puanı
        rsi_score = 9 if rsi < 30 else 2 if rsi > 70 else 6

        # EMA puanı
        if price > ema50 > ema200:
            ema_score = 9
        elif price < ema50 < ema200:
            ema_score = 2
        else:
            ema_score = 5

        # MACD puanı
        if macd_val > macd_sig:
            macd_score = 8
        elif macd_val < macd_sig:
            macd_score = 3
        else:
            macd_score = 5

        total = round((rsi_score + ema_score + macd_score) / 3, 2)
        return total

    except Exception as e:
        return f"Hata: {e}"

def genel_yorum(ortalama):
    if isinstance(ortalama, str):
        return "Analiz başarısız."
    if ortalama >= 8:
        return "🚀 Güçlü boğa trendi"
    elif ortalama >= 6.5:
        return "🟢 Piyasa boğa başlangıcında"
    elif ortalama >= 4:
        return "⚖️ Piyasa nötr"
    else:
        return "📉 Piyasa ayı bölgesinde"

def send_message(text):
    url = f"{URL}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    requests.post(url, data=payload)

def main():
    symbol = "BTCUSDT"  # Değiştirilebilir
    intervals = [("15dk", "15m"), ("1saat", "1h"), ("4saat", "4h"), ("1gün", "1d")]
    results = []

    for name, interval in intervals:
        score = analyze(symbol, interval)
        if isinstance(score, str):
            results.append(f"🕒 {name}: analiz hatalı")
        else:
            results.append(f"🕒 {name} → {score}/10")

    puanlar = [analyze(symbol, i[1]) for i in intervals]
    sayisal = [p for p in puanlar if not isinstance(p, str)]
    ortalama = round(sum(sayisal) / len(sayisal), 2) if sayisal else "N/A"
    yorum = genel_yorum(ortalama)

    mesaj = f"""📊 Gelişmiş Teknik Analiz: {symbol}

{chr(10).join(results)}

🎯 Genel Puan: {ortalama}/10
💬 Yorum: {yorum}
"""
    send_message(mesaj)

if __name__ == "__main__":
    main()
