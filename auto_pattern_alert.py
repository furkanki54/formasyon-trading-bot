import requests
import pandas as pd
from config import SYMBOL, BINANCE_BASE_URL, IMG_PATH
from grafik_uretici import ciz_trend_grafigi
from formasyon_algilayici import basit_formasyon_tespiti
from telegram_sender import telegrama_mesaj_gonder, telegrama_resim_gonder

def veri_cek(symbol):
    url = f"{BINANCE_BASE_URL}/api/v3/klines?symbol={symbol}&interval=1h&limit=50"
    resp = requests.get(url).json()
    df = pd.DataFrame(resp, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'qav', 'trades', 'tbbav', 'tbqav', 'ignore'
    ])
    df['close'] = df['close'].astype(float)
    return df

def analiz_et_ve_gonder():
    df = veri_cek(SYMBOL)
    ciz_trend_grafigi(df, IMG_PATH)
    yorum = basit_formasyon_tespiti(df)
    fiyat = df['close'].iloc[-1]
    mesaj = f"📊 {SYMBOL} Formasyon Analizi\nFiyat: {fiyat:.2f} USDT\nYorum: {yorum}"
    telegrama_resim_gonder(IMG_PATH, mesaj)

if __name__ == "__main__":
    analiz_et_ve_gonder()
