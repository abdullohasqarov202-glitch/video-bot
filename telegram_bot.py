import os
from flask import Flask, request
import telebot
import yt_dlp
import tempfile
import re

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN aniqlanmadi!")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

COOKIE_FILE = "cookies.txt"
CHANNEL_USERNAME = "@Asqarov_2007"

user_balances = {}

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

def sanitize_filename(filename):
    """Fayl nomidagi taqiqlangan belgilarni tozalash"""
    return re.sub(r'[\\/*?:"<>|⧸]', "_", filename)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.chat.id
    if not is_subscribed(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("📢 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"),
            telebot.types.InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")
        )
        bot.send_message(user_id, f"👋 Botdan foydalanish uchun kanalga obuna bo‘ling: {CHANNEL_USERNAME}", reply_markup=markup)
        return

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎥 Video yuklash", "🎧 Qo‘shiq topish", "📩 Admin bilan aloqa")
    bot.send_message(user_id, "✅ Xush kelibsiz!", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("http"))
def download_video(message):
    url = message.text.strip()
    bot.reply_to(message, "⏳ Yuklab olinmoqda...")

    if not os.path.exists(COOKIE_FILE):
        bot.reply_to(message, "⚠️ Cookie fayli topilmadi.")
        return

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'outtmpl': f'{tmpdir}/%(title)s.%(ext)s',
                'cookiefile': COOKIE_FILE,
                'format': 'mp4/bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'merge_output_format': 'mp4',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                safe_title = sanitize_filename(info.get('title', 'video'))
                video_path = os.path.join(tmpdir, f"{safe_title}.mp4")
                if not os.path.exists(video_path):
                    # Ba'zi hollarda yt-dlp nomni boshqacha beradi
                    for f in os.listdir(tmpdir):
                        if f.endswith(".mp4"):
                            video_path = os.path.join(tmpdir, f)
                            break

            title = info.get('title', 'Noma’lum video 🎬')
            artist = info.get('uploader', 'Noma’lum ijrochi')
            BOT_LINK = "https://t.me/Asqarov_2007_bot"
            caption = f"🎶 <b>{title}</b>\n👤 {artist}\n📲 <a href='{BOT_LINK}'>@Asqarov_2007_bot</a>"

            with open(video_path, 'rb') as video:
                bot.send_video(message.chat.id, video, caption=caption, parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik: {e}")

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "<h2>✅ Bot ishlayapti!</h2>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
