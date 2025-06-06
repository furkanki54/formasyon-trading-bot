import requests
import pandas as pd
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, BINANCE_API_BASE
from telebot import TeleBot
from pattern_utils import detect_tobo, detect_obo, detect_w, detect_cup_handle
from chart_drawer import draw_chart

bot = TeleBot(TELEGRAM_TOKEN)

def get_klines(symbol="BTCUSDT", interval="1h", limit=100):
    url = f"{BINANCE_API_BASE}/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    r = requests.get(url)
    data = r.json()
    df = pd.DataFrame(data, columns=[
        "time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ])
    df["time"] = pd.to_datetime(df["time"], unit='ms')
    df["close"] = pd.to_numeric(df["close"])
    return df[["time", "close"]]

def detect_patterns(df):
    patterns = []
    if detect_tobo(df):
        patterns.append("TOBO")
    if detect_obo(df):
        patterns.append("OBO")
    if detect_w(df):
        patterns.append("W")
    if detect_cup_handle(df):
        patterns.append("Fincan-Kulp")
    return patterns

def main():
    symbol = "BTCUSDT"
    df = get_klines(symbol, interval="1h", limit=100)
    patterns = detect_patterns(df)
    if patterns:
        image_path = draw_chart(df, symbol, patterns)
        message = f"📊 {symbol} grafik sinyali tespit edildi: {', '.join(patterns)}"
        with open(image_path, "rb") as photo:
            bot.send_photo(TELEGRAM_CHAT_ID, photo, caption=message)
    else:
        bot.send_message(TELEGRAM_CHAT_ID, f"{symbol} için formasyon bulunamadı.")

if __name__ == "__main__":
    main()
