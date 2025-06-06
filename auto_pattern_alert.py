import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from telegram import Bot
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, BINANCE_BASE_URL

bot = Bot(token=TELEGRAM_TOKEN)

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
    df["low"] = df["low"].astype(float)
    df["high"] = df["high"].astype(float)
    df["time"] = pd.to_datetime(df["time"], unit='ms')
    return df

def detect_tobo(df):
    last = df["close"].iloc[-5:]
    if last.iloc[0] > last.iloc[1] < last.iloc[2] > last.iloc[3] < last.iloc[4]:
        return True
    return False

def draw_chart(df, symbol, pattern_name="TOBO"):
    plt.figure(figsize=(10, 5))
    plt.plot(df["time"], df["close"], label="Close", color="blue")
    plt.title(f"{symbol} - {pattern_name} Formasyonu")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

def analyze_symbol(symbol):
    df = get_ohlcv(symbol)
    if detect_tobo(df):
        chart = draw_chart(df, symbol, "TOBO")
        bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=chart,
                       caption=f"📈 {symbol} için TOBO formasyonu tespit edildi!")
    else:
        print(f"{symbol} için formasyon yok.")

if __name__ == "__main__":
    coin_list = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    for coin in coin_list:
        analyze_symbol(coin)
