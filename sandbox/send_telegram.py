import logging
from telegram import Bot

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram bot token
TOKEN = "5918242394:AAGWuT6D4JKEnXKzej4eZWctAoiWlN4ygms"

# User ID to send the message
USER_ID = "949572254"

def send_message_once(token, user_id, message):
    try:
        bot = Bot(token)
        bot.send_message(chat_id=user_id, text=message)
        logger.info("Message sent successfully!")
    except Exception as e:
        logger.error("Failed to send message: %s", str(e))

def main():
    message = "Hello! This is a one-time message."
    send_message_once(TOKEN, USER_ID, message)

if __name__ == "__main__":
    main()
