import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def telegrama_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": mesaj}
    requests.post(url, data=data)

def telegrama_resim_gonder(dosya_path, mesaj=""):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    with open(dosya_path, 'rb') as f:
        files = {'photo': f}
        data = {"chat_id": TELEGRAM_CHAT_ID, "caption": mesaj}
        requests.post(url, files=files, data=data)
