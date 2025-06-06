import matplotlib.pyplot as plt
import pandas as pd

def draw_chart(df, symbol, detected_patterns):
    plt.figure(figsize=(10, 6))
    plt.plot(df['time'], df['close'], label="Fiyat", linewidth=2)

    title = f"{symbol.upper()} Teknik Grafik"
    if detected_patterns:
        title += f" ({', '.join(detected_patterns)})"

    plt.title(title)
    plt.xlabel("Zaman")
    plt.ylabel("Fiyat")
    plt.legend()
    plt.grid(True)

    image_path = f"{symbol}_chart.png"
    plt.savefig(image_path)
    plt.close()
    return image_path
