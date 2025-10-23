# telegram_webhook_bot.py
import os
from flask import Flask, request
import telebot
import yt_dlp
import tempfile

# 1️⃣ Telegram token
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN aniqlanmadi!")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# 2️⃣ Cookie matni — shu yerga sizning cookies.txt ichidagi ma’lumotni joylang
INSTAGRAM_COOKIE = """
# Netscape HTTP Cookie File
.instagram.com   TRUE    /   FALSE   1739980000  sessionid   1234567890%3AabcdEfGhIjKlMnOpQrStUvWxYz
.instagram.com   TRUE    /   TRUE    1739980000  ds_user_id  987654321
.instagram.com   TRUE    /   TRUE    1739980000  csrftoken   ABCDEFGHIJKLMNOPQRSTUVWX
"""  # ⬆ bu joyga brauzerdan eksport qilingan cookie yoziladi

# 3️⃣ Start / help buyrug‘i
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎥 Video yuklash", "📩 Admin bilan aloqa", "🎨 Rasm yasash")
    bot.send_message(
        message.chat.id,
        "Assalomu alaykum!\nPastdagi tugmalardan birini tanlang:",
        reply_markup=markup
    )

# 4️⃣ Tugma tanlanganda
@bot.message_handler(func=lambda message: message.text == "📩 Admin bilan aloqa")
def contact_admin(message):
    bot.reply_to(message, "Admin bilan aloqa uchun: @SizningAdminNickingiz")

@bot.message_handler(func=lambda message: message.text == "🎨 Rasm yasash")
def make_image(message):
    bot.reply_to(message, "✍️ Rasm yaratish xizmati hozircha sinovda — tez orada qo‘shiladi!")

@bot.message_handler(func=lambda message: message.text == "🎥 Video yuklash")
def ask_video_link(message):
    bot.reply_to_
