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

# 4️⃣ Referal tizimi va foydalanuvchilar xotirasi
user_referrals = {}
user_balances = {}
all_users = {}  # ✅ user_id: username shaklida saqlanadi

# 5️⃣ Admin username
ADMIN_USERNAME = "@Asqarov_0207"

# ✅ Obuna tekshirish
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False


# 6️⃣ Start / help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.chat.id
    username = message.from_user.username or f"id:{user_id}"
    args = message.text.split()

    # ✅ Foydalanuvchini ro‘yxatga qo‘shish
    all_users[user_id] = username

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

    # ✅ Tugmalar tartibi o‘zgartirildi
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎥 Video yuklash", "🎬 Kinolar")
    markup.add("🔗 Referal havola", "💎 Mening olmoslarim")
    markup.add("📩 Admin bilan aloqa", "💎 Premium olish")

    # 👑 Agar admin bo‘lsa, qo‘shimcha tugma
    if message.from_user.username == ADMIN_USERNAME[1:]:
        markup.add("👤 Foydalanuvchilar ro‘yxati")

    bot.send_message(user_id, "✅ Siz kanalga obuna bo‘lgansiz. Quyidagi menyudan tanlang:", reply_markup=markup)


# 7️⃣ Obuna qayta tekshirish
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    user_id = call.message.chat.id
    if is_subscribed(user_id):
        bot.edit_message_text("✅ Obuna tasdiqlandi!", chat_id=user_id, message_id=call.message.message_id)
        send_welcome(call.message)
    else:
        bot.answer_callback_query(call.id, "🚫 Hali obuna bo‘lmagansiz!")


# 8️⃣ Admin menyusi — foydalanuvchilar ro‘yxati (faqat ADMIN uchun)
@bot.message_handler(func=lambda message: message.text == "👤 Foydalanuvchilar ro‘yxati")
def show_users(message):
    if message.from_user.username != ADMIN_USERNAME[1:]:
        bot.reply_to(message, "🚫 Siz bu bo‘limga kira olmaysiz.")
        return

    if not all_users:
        bot.reply_to(message, "👤 Hozircha hech kim /start bosmagan.")
        return

    users_text = "\n".join([
        f"• @{uname}" if uname != f"id:{uid}" else f"• id:{uid}"
        for uid, uname in all_users.items()
    ])

    bot.reply_to(message, f"👥 <b>Start bosgan foydalanuvchilar:</b>\n\n{users_text}", parse_mode="HTML")


# 9️⃣ Admin va referal
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


# 💎 PREMIUM OLIB BO‘LIMI
@bot.message_handler(func=lambda message: message.text == "💎 Premium olish")
def buy_premium(message):
    user_id = message.chat.id
    balance = user_balances.get(user_id, 0)

    if balance >= 200:
        user_balances[user_id] -= 200
        bot.reply_to(message, "🌟 Tabriklaymiz! Siz Premium foydalanuvchi bo‘ldingiz! ✅")
    else:
        bot.reply_to(message, f"❌ Yetarli olmos yo‘q.\nSizda: {balance} 💎 bor.\nPremium olish uchun 200 💎 kerak.")


# 🎬 KINOLAR TUGMASI
@bot.message_handler(func=lambda message: message.text == "🎬 Kinolar")
def open_movies_channel(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🎬 Kinolar kanaliga o‘tish", url="https://t.me/KINOLAR_UZB12"))
    bot.send_message(message.chat.id, "🍿 Quyidagi tugma orqali kinolar kanaliga o‘ting:", reply_markup=markup)


# 🔟 Video yuklash (TikTok, Instagram, Facebook, Twitter)
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

            music = info.get("music") or info.get("track") or info.get("artist") or info.get("alt_title")
            music_text = f"\n🎵 Qo‘shiq: {music}" if music else ""

            caption = (
                f"✨ <b>Yuklab beruvchi:</b> <a href='https://t.me/asqarov_uzbot'>@asqarov_uzbot</a> 💫"
            )

            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(
                telebot.types.InlineKeyboardButton("➕ Guruh yoki kanalga qo‘shilish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"),
            )

            with open(video_path, 'rb') as v:
                bot.send_video(
                    message.chat.id,
                    v,
                    caption=caption,
                    parse_mode='HTML',
                    reply_markup=markup
                )

    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik: {e}")


# 🧩 Flask webhook
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
