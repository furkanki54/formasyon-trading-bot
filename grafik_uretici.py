import matplotlib.pyplot as plt
import pandas as pd

def ciz_trend_grafigi(df, path):
    plt.figure(figsize=(12, 6))
    plt.plot(df['close'], label='Fiyat', color='blue')
    plt.plot([0, len(df)-1], [df['close'].iloc[0], df['close'].iloc[-1]],
             linestyle="--", color="red", label='Trend Çizgisi')

    plt.title('Trend ve Fiyat Grafiği')
    plt.xlabel('Zaman')
    plt.ylabel('Fiyat (USDT)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
