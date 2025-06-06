import requests
import pandas as pd
import ta
import time
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, BINANCE_BASE_URL

URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def get_updates(offset=None):
    url = f"{URL}/getUpdates"
    params = {"offset": offset, "timeout": 10}
    res = requests.get(url, params=params)
    return res.json()

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
    df["volume"] = df["volume"].astype(float)
    return df

def analyze(symbol):
    try:
        df = get_ohlcv(symbol)
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

        if rsi < 30:
            rsi_score = 9
            rsi_comment = "Aşırı satımda, toparlanabilir."
        elif rsi > 70:
            rsi_score = 2
            rsi_comment = "Aşırı alımda, düzeltme gelebilir."
        else:
            rsi_score = 6
            rsi_comment = "Nötr"

        if price > ema50 > ema200:
            ema_score = 9
            ema_comment = "Güçlü boğa trendi"
        elif price < ema50 < ema200:
            ema_score = 2
            ema_comment = "Ayı baskısı yüksek"
        else:
            ema_score = 5
            ema_comment = "Kararsız EMA"

        if macd_val > macd_sig:
            macd_score = 8
            macd_comment = "Pozitif MACD"
        elif macd_val < macd_sig:
            macd_score = 3
            macd_comment = "Negatif MACD"
        else:
            macd_score = 5
            macd_comment = "MACD zayıf"

        total_score = round((rsi_score + ema_score + macd_score) / 3, 2)
        sentiment = "📈 Boğa" if total_score >= 6.5 else "📉 Ayı" if total_score <= 4 else "⚖️ Kararsız"

        message = f"""
📊 Teknik Analiz: {symbol.upper()}
Fiyat: {round(price,2)} USDT
———————————————
📈 RSI: {round(rsi,2)} — {rsi_comment}
📉 EMA: 50={round(ema50,2)} | 200={round(ema200,2)} — {ema_comment}
📊 MACD: {round(macd_val,2)} / {round(macd_sig,2)} — {macd_comment}
———————————————
🎯 Puan: {total_score}/10
💬 Yorum: {sentiment}
"""
        return message
    except Exception as e:
        return f"{symbol.upper()} için analiz hatası: {e}"

def send_message(text):
    url = f"{URL}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    requests.post(url, data=payload)

def listen_for_commands():
    offset = None
    while True:
        updates = get_updates(offset)
        if "result" in updates:
            for update in updates["result"]:
                offset = update["update_id"] + 1
                message = update.get("message", {})
                text = message.get("text", "").strip().lower()
                if text.isalpha():
                    symbol = text.upper() + "USDT"
                    result = analyze(symbol)
                    send_message(result)
        time.sleep(5)

if __name__ == "__main__":
    listen_for_commands()
