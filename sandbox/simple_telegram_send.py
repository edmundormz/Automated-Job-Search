import requests
TELEGRAM_TOKEN = ""
TELEGRAM_CHAT_ID = ""
message = "Are you ready to integrate telegram in the main code?"
url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}"
print(requests.get(url).json()) # this sends the message