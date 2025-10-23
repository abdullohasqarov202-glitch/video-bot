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

# Referal tizimi uchun oddiy xotira
user_referrals = {}
user_balances = {}

# 2️⃣ Cookie faylni ko‘rsatish (shu fayl papkada bo‘lishi shart!)
COOKIE_FILE = "cookies.txt"

# 3️⃣ Start / help buyrug‘i
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.chat.id
    args = message.text.split()

    # referal tizimi
    if len(args) > 1:
        referrer_id = args[1]
        if referrer_id != str(user_id):
            user_balances[referrer_id] = user_balances.get(referrer_id, 0) + 10
            bot.send_message(referrer_id, "🎉 Sizga +10 💎 olmos qo‘shildi! Do‘stingiz sizning havolangiz orqali kirdi!")

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎥 Video yuklash", "📩 Admin bilan aloqa", "🎨 Rasm yasash", "💎 Mening olmoslarim", "🔗 Referal havola")

    bot.send_message(
        user_id,
        "Assalomu alaykum!\nPastdagi tugmalardan birini tanlang:",
        reply_markup=markup
    )

# 4️⃣ Tugmalar
@bot.message_handler(func=lambda message: message.text == "📩 Admin bilan aloqa")
def contact_admin(message):
    bot.reply_to(message, "Admin bilan aloqa uchun: @Asqarov_0207")

@bot.message_handler(func=lambda message: message.text == "🎨 Rasm yasash")
def make_image(message):
    bot.reply_to(message, "✍️ Rasm yaratish xizmati hozircha sinovda — tez orada qo‘shiladi!")

@bot.message_handler(func=lambda message: message.text == "🎥 Video yuklash")
def ask_video_link(message):
    bot.reply_to(message, "🎥 Video havolasini yuboring (Instagram, YouTube va boshqalar).")

@bot.message_handler(func=lambda message: message.text == "💎 Mening olmoslarim")
def my_diamonds(message):
    balance = user_balances.get(message.chat.id, 0)
    bot.reply_to(message, f"💎 Sizda hozir: {balance} olmos mavjud.")

@bot.message_handler(func=lambda message: message.text == "🔗 Referal havola")
def referral_link(message):
    link = f"https://t.me/{bot.get_me().username}?start={message.chat.id}"
    bot.reply_to(message, f"📢 Sizning taklif havolangiz:\n{link}\n\nHar bir do‘st uchun +10 💎 olmos!")

# 5️⃣ Video yuklab berish
@bot.message_handler(func=lambda message: message.text.startswith("http"))
def download_video(message):
    url = message.text.strip()
    bot.reply_to(message, "⏳ Yuklab olinmoqda...")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'outtmpl': f'{tmpdir}/%(title)s.%(ext)s',
                'cookiefile': COOKIE_FILE,  # cookie fayl ulanmoqda
                'format': 'mp4/bestaudio/best',
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)

            with open(video_path, 'rb') as video:
                bot.send_video(message.chat.id, video)

    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik: {e}")

# 6️⃣ Flask webhook yo‘li
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Asosiy sahifa
@app.route("/", methods=["GET"])
def home():
    return "<h2>✅ Bot server ishlayapti!</h2><p>Video bot Render serverda muvaffaqiyatli ishga tushdi.</p>"

# 7️⃣ Flask ishga tushirish
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
