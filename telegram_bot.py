import os
from flask import Flask, request
import telebot
import yt_dlp
import tempfile

# 1️⃣ Telegram token
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN aniqlanmadi! Render environment variable orqali qo‘shing.")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# 2️⃣ Cookie fayl (shu fayl papkada bo‘lishi shart!)
COOKIE_FILE = "cookies.txt"

# 3️⃣ Kanal username (shu joyni o‘zingiznikiga o‘zgartiring)
CHANNEL_USERNAME = "@Asqarov_2007"

# Referal tizimi uchun oddiy xotira
user_referrals = {}
user_balances = {}

# ✅ Obuna tekshirish funksiyasi
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

# 4️⃣ Start / help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.chat.id
    args = message.text.split()

    # 🔍 Avval kanal obunasini tekshiramiz
    if not is_subscribed(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("📢 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"),
            telebot.types.InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")
        )
        bot.send_message(
            user_id,
            f"👋 Assalomu alaykum!\n\nBotdan foydalanish uchun iltimos quyidagi kanalga obuna bo‘ling:\n{CHANNEL_USERNAME}",
            reply_markup=markup
        )
        return  # Obuna bo‘lmaguncha pastdagi menyuni ko‘rsatmaydi

    # ✅ Agar obuna bo‘lgan bo‘lsa, menyu chiqadi:
    if len(args) > 1:
        referrer_id = args[1]
        if referrer_id != str(user_id):
            user_balances[referrer_id] = user_balances.get(referrer_id, 0) + 10
            bot.send_message(referrer_id, "🎉 Sizga +10 💎 olmos qo‘shildi! Do‘stingiz sizning havolangiz orqali kirdi!")

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        "🎥 Video yuklash",
        "📩 Admin bilan aloqa",
        "🎨 Rasm yasash",
        "💎 Mening olmoslarim",
        "🔗 Referal havola"
    )

    bot.send_message(
        user_id,
        "✅ Tabriklaymiz! Siz kanalga obuna bo‘lgansiz.\nQuyidagi menyudan tanlang:",
        reply_markup=markup
    )

# 5️⃣ Obunani qayta tekshirish tugmasi
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    user_id = call.message.chat.id
    if is_subscribed(user_id):
        bot.edit_message_text("✅ Obuna muvaffaqiyatli tasdiqlandi!", chat_id=user_id, message_id=call.message.message_id)
        send_welcome(call.message)
    else:
        bot.answer_callback_query(call.id, "🚫 Hali obuna bo‘lmagansiz!")

# 6️⃣ Tugmalar
@bot.message_handler(func=lambda message: message.text == "📩 Admin bilan aloqa")
def contact_admin(message):
    bot.reply_to(message, "📞 Admin bilan aloqa: @Asqarov_0207")

@bot.message_handler(func=lambda message: message.text == "🎨 Rasm yasash")
def make_image(message):
    bot.reply_to(message, "🎨 Rasm yaratish xizmati hozircha sinovda — tez orada ishga tushadi!")

@bot.message_handler(func=lambda message: message.text == "🎥 Video yuklash")
def ask_video_link(message):
    bot.reply_to(message, "🎥 Yuklamoqchi bo‘lgan video havolasini yuboring (Instagram, YouTube va boshqalar).")

@bot.message_handler(func=lambda message: message.text == "💎 Mening olmoslarim")
def my_diamonds(message):
    balance = user_balances.get(message.chat.id, 0)
    bot.reply_to(message, f"💎 Sizda hozir: {balance} olmos mavjud.")

@bot.message_handler(func=lambda message: message.text == "🔗 Referal havola")
def referral_link(message):
    link = f"https://t.me/{bot.get_me().username}?start={message.chat.id}"
    bot.reply_to(message, f"🔗 Sizning taklif havolangiz:\n{link}\n\nHar bir do‘st uchun +10 💎 olmos!")

# 7️⃣ Video yuklab berish
@bot.message_handler(func=lambda message: message.text.startswith("http"))
def download_video(message):
    url = message.text.strip()
    bot.reply_to(message, "⏳ Yuklab olinmoqda, biroz kuting...")

    if not os.path.exists(COOKIE_FILE):
        bot.reply_to(message, "⚠️ Cookie fayli topilmadi. Iltimos, `cookies.txt` faylni serverga joylashtiring.")
        return

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # 🎥 Videoni yuklab olish
            ydl_opts = {
                'outtmpl': f'{tmpdir}/%(title)s.%(ext)s',
                'cookiefile': COOKIE_FILE,
                'format': 'mp4/bestaudio/best',
                'quiet': True,
                'merge_output_format': 'mp4',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)

            # 🎶 Qo‘shiq nomi, ijrochi va bot havolasi
            title = info.get('title', 'Noma’lum qo‘shiq 🎵')
            artist = info.get('uploader', 'Noma’lum ijrochi')
            BOT_LINK = "https://t.me/Asqarov_2007_bot"

            caption = f"🎶 <b>{title}</b>\n👤 {artist}\n\n📲 Yuklab beruvchi bot: <a href='{BOT_LINK}'>@asqarov_uzbot</a>"

            # 🎥 Videoni yuboramiz
            with open(video_path, 'rb') as video:
                bot.send_video(message.chat.id, video, caption=caption, parse_mode="HTML")

            # 🎧 Musiqani ham yuklab yuboramiz
            audio_opts = {
                'outtmpl': f'{tmpdir}/%(title)s.%(ext)s',
                'cookiefile': COOKIE_FILE,
                'format': 'bestaudio/best',
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with yt_dlp.YoutubeDL(audio_opts) as ydl_audio:
                audio_info = ydl_audio.extract_info(url, download=True)
                audio_path = ydl_audio.prepare_filename(audio_info)
                audio_path = audio_path.replace('.webm', '.mp3').replace('.m4a', '.mp3')

            with open(audio_path, 'rb') as audio:
                bot.send_audio(message.chat.id, audio, title=title, performer=artist)

    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik: {e}")

# 8️⃣ Flask webhook
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# 9️⃣ Asosiy sahifa
@app.route("/", methods=["GET"])
def home():
    return "<h2>✅ Bot server ishlayapti!</h2><p>Render orqali ishga tushgan video va musiqa yuklab beruvchi bot.</p>"

# 🔟 Flaskni ishga tushirish
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
