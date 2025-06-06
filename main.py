import telebot
import requests
import statistics
from config import TELEGRAM_TOKEN, CHAT_ID
from coin_list import COIN_LIST

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_technical_data(symbol):
    # Örnek veri – senin gerçek analiz fonksiyonlarınla entegre edilecek
    data = {
        'price': 0.718,
        'rsi': [1, 1, 2, 1],
        'macd': [1, 1, 1, 1],
        'ema': [1, 1, 1, 1]
    }
    return data

def interpret_score(avg):
    if avg >= 7:
        return "🐂 Güçlü boğa piyasası"
    elif avg >= 5:
        return "📈 Boğa başlangıcı"
    elif avg >= 3:
        return "⚖️ Nötr"
    else:
        return "🐻 Güçlü ayı piyasası"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    symbol = message.text.upper()
    if symbol not in COIN_LIST:
        bot.send_message(message.chat.id, f"❌ '{symbol}' desteklenmiyor.")
        return

    try:
        data = get_technical_data(symbol)
        avg_score = round(statistics.mean(data['rsi'] + data['macd'] + data['ema']), 2)
        yorum = interpret_score(avg_score)

        text = (
            f"📊 Teknik Analiz: {symbol}\n"
            f"Fiyat: {data['price']} USDT\n"
            f"———————————————\n"
            f"🔹 RSI Puanları: {data['rsi']}\n"
            f"🔹 MACD Puanları: {data['macd']}\n"
            f"🔹 EMA Puanları: {data['ema']}\n"
            f"———————————————\n"
            f"🎯 Ortalama Puan: {avg_score}/10\n"
            f"💬 Yorum: {yorum}"
        )
        bot.send_message(message.chat.id, text)

    except Exception as e:
        bot.send_message(message.chat.id, f"❗️Hata oluştu: {e}")

if __name__ == '__main__':
    bot.polling()
