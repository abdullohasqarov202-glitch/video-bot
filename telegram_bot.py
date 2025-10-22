import os
from flask import Flask, request
import telebot
import yt_dlp

# Telegram tokenni o‘rnatish
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN aniqlanmadi!")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# Start / help buyrug‘i
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Assalomu alaykum! Video yuboring, men uni yuklab beraman.")

# Video URL qabul qilish
@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text.strip()
    bot.reply_to(message, "Video yuklanmoqda, biroz kuting...")

    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': '/tmp/%(title)s.%(ext)s',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video)
    except Exception as e:
        bot.reply_to(message, f"Xatolik yuz berdi: {e}")

# Webhook endpoint
@app.route(f"/{TELEGRAM_TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

# Flask serverini ishga tushirish
if __name__ == "__main__":
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT)
