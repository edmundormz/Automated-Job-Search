import requests
TOKEN = "5918242394:AAGWuT6D4JKEnXKzej4eZWctAoiWlN4ygms"
chat_id = "949572254"
message = "hello from your telegram bot"
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
print(requests.get(url).json()) # this sends the message