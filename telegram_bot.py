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

# 2️⃣ Cookie fayl (agar kerak bo‘lsa)
COOKIE_FILE = "cookies.txt"

# 3️⃣ Kanal username
CHANNEL_USERNAME = "@Asqarov_2007"

# 4️⃣ Referal tizimi uchun xotira
user_referrals = {}
user_balances = {}

# ✅ Obuna tekshirish
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False


# 5️⃣ Start / help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.chat.id
    args = message.text.split()

    # Obuna tekshirish
    if not is_subscribed(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("📢 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"),
            telebot.types.InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")
        )
        bot.send_message(
            user_id,
            f"👋 Assalomu alaykum!\n\nBotdan foydalanish uchun kanalga obuna bo‘ling:\n{CHANNEL_USERNAME}",
            reply_markup=markup
        )
        return

    # Referal tizimi
    if len(args) > 1:
        referrer_id = args[1]
        if referrer_id != str(user_id):
            user_balances[referrer_id] = user_balances.get(referrer_id, 0) + 10
            bot.send_message(referrer_id, "🎉 Do‘stingiz sizning havolangiz orqali kirdi! Sizga +10 💎 olmos!")

    # Menyu
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎥 Video yuklash", "📩 Admin bilan aloqa", "💎 Mening olmoslarim", "🔗 Referal havola")
    bot.send_message(user_id, "✅ Siz kanalga obuna bo‘lgansiz. Quyidagi menyudan tanlang:", reply_markup=markup)


# 6️⃣ Obuna qayta tekshirish
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    user_id = call.message.chat.id
    if is_subscribed(user_id):
        bot.edit_message_text("✅ Obuna tasdiqlandi!", chat_id=user_id, message_id=call.message.message_id)
        send_welcome(call.message)
    else:
        bot.answer_callback_query(call.id, "🚫 Hali obuna bo‘lmagansiz!")


# 7️⃣ Admin va referal
@bot.message_handler(func=lambda message: message.text == "📩 Admin bilan aloqa")
def contact_admin(message):
    bot.reply_to(message, "📞 Admin: @Asqarov_0207")

@bot.message_handler(func=lambda message: message.text == "💎 Mening olmoslarim")
def my_diamonds(message):
    balance = user_balances.get(message.chat.id, 0)
    bot.reply_to(message, f"💎 Sizda hozir: {balance} olmos mavjud.")

@bot.message_handler(func=lambda message: message.text == "🔗 Referal havola")
def referral_link(message):
    link = f"https://t.me/{bot.get_me().username}?start={message.chat.id}"
    bot.reply_to(message, f"🔗 Sizning taklif havolangiz:\n{link}\n\nHar bir do‘st uchun +10 💎 olmos!")


# 8️⃣ Video yuklash (faqat TikTok, Instagram, Facebook, Twitter)
@bot.message_handler(func=lambda message: message.text == "🎥 Video yuklash")
def ask_video_link(message):
    bot.reply_to(message, "🎥 Yuklamoqchi bo‘lgan video havolasini yuboring (TikTok, Instagram, Facebook yoki Twitter).")

@bot.message_handler(func=lambda message: message.text.startswith("http"))
def download_video(message):
    url = message.text.strip()
    bot.reply_to(message, "⏳ Yuklab olinmoqda, biroz kuting...")

    try:
        if not any(domain in url for domain in ["tiktok.com", "instagram.com", "fb.watch", "facebook.com", "x.com", "twitter.com"]):
            bot.reply_to(message, "⚠️ Faqat TikTok, Instagram, Facebook yoki Twitter havolalarini yuboring.")
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            video_opts = {
                'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                'cookiefile': COOKIE_FILE if os.path.exists(COOKIE_FILE) else None,
                'format': 'mp4',
                'quiet': True
            }

            with yt_dlp.YoutubeDL(video_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)

            # 🎵 Musiqa nomini olish (agar bo‘lsa)
            music = info.get("music", None) or info.get("track", None)
            music_text = f"\n🎵 Musiqa: {music}" if music else ""

            caption = f"🎬 <b>{info.get('title', 'Video')}</b>{music_text}\n\n📲 Yuklab beruvchi: <a href='https://t.me/asqarov_uzbot'>@asqarov_uzbot</a>"

            # 🔘 Tugma qo‘shish
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("➕ Guruh yoki kanalga qo‘shilish", url="https://t.me/Asqarov_2007"))

            with open(video_path, 'rb') as v:
                bot.send_video(message.chat.id, v, caption=caption, parse_mode='HTML', reply_markup=markup)

    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik: {e}")


# 🔟 Flask webhook
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200


@app.route("/")
def home():
    return "<h2>✅ Bot ishlayapti!</h2><p>TikTok, Instagram, Facebook, Twitter videolarini yuklab beruvchi bot.</p>"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

