import os
from flask import Flask, request
import telebot
import yt_dlp
import tempfile
import shutil

# 1️⃣ Telegram token
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN topilmadi! Renderda environment variable sifatida qo‘shing.")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# 2️⃣ Cookie fayl
COOKIE_FILE = "cookies.txt"

# 3️⃣ Kanal nomi
CHANNEL_USERNAME = "@Asqarov_2007"

# ✅ Obuna tekshirish
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

# 4️⃣ Start buyrug‘i
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id

    if not is_subscribed(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("📢 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"),
            telebot.types.InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")
        )
        bot.send_message(
            user_id,
            f"👋 Salom! Botdan foydalanish uchun {CHANNEL_USERNAME} kanaliga obuna bo‘ling!",
            reply_markup=markup
        )
        return

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎥 Video yuklash", "🎧 Qo‘shiq topish")
    bot.send_message(user_id, "✅ Menyudan tanlang:", reply_markup=markup)


# 5️⃣ Obuna tekshirish tugmasi
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    user_id = call.message.chat.id
    if is_subscribed(user_id):
        bot.edit_message_text("✅ Obuna tasdiqlandi!", chat_id=user_id, message_id=call.message.message_id)
        send_welcome(call.message)
    else:
        bot.answer_callback_query(call.id, "🚫 Hali obuna bo‘lmagansiz!")


# 6️⃣ Qo‘shiq topish
@bot.message_handler(func=lambda message: message.text == "🎧 Qo‘shiq topish")
def ask_song_name(message):
    bot.reply_to(message, "🎶 Qaysi qo‘shiqni topay? Masalan: Shahzoda - Hayot ayt")

@bot.message_handler(func=lambda message: not message.text.startswith("http") and not message.text.startswith("/"))
def search_and_download_song(message):
    query = message.text.strip()
    bot.reply_to(message, f"🔎 Qidirilmoqda: {query}...")

    try:
        tmpdir = tempfile.mkdtemp()
        opts = {
            'quiet': True,
            'noplaylist': True,
            'cookiefile': COOKIE_FILE,
            'default_search': 'ytsearch1',
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
