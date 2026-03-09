import os
from flask import Flask, request
import telebot
import yt_dlp
import tempfile
from datetime import datetime, timedelta
import threading
import time

# 1️⃣ Telegram token
ASQAROV = os.environ.get("C")
if not TELEGRAM_TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN aniqlanmadi! Render environment variable orqali qo‘shing.")

bot = telebot.TeleBot(ASQAROV)
app = Flask(__name__)

# 2️⃣ Cookie fayl
COOKIE_FILE = "cookies.txt"

# 3️⃣ Kanal username
CHANNEL_USERNAME = "@Asqarov_2007"

# 4️⃣ Referal tizimi va foydalanuvchilar
user_referrals = {}
user_balances = {}
all_users = {}
user_last_bonus = {}

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

    first_time = user_id not in all_users
    all_users[user_id] = username

    # Obuna tekshirish
    if not is_subscribed(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("📢 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"),
            telebot.types.InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")
        )
        bot.send_message(user_id,
            f"👋 Assalomu alaykum!\n\nBotdan foydalanish uchun kanalga obuna bo‘ling:\n{CHANNEL_USERNAME}",
            reply_markup=markup
        )
        return

    if first_time:
        intro_text = (
            "👋 <b>Salom!</b> Men sizga yordam beruvchi <b>video yuklab beruvchi botman</b>!\n\n"
            "📽 <b>Nimalar qila olaman:</b>\n"
            "• TikTok, Instagram, Facebook, Twitter videolarini yuklab beraman 🎥\n"
            "• Kinolar kanaliga yo‘naltiraman 🎬\n"
            "• Do‘stlaringizni taklif qilib olmos yig‘ish 💎\n"
            "• Premium olish 🌟 va reklama joylash 📢\n"
            "• Admin bilan bog‘lanish 📩\n\n"
            "👇 Quyidagi menyudan tanlang!"
        )
        bot.send_message(user_id, intro_text, parse_mode="HTML")

    # Referal tizimi
    if len(args) > 1:
        referrer_id = args[1]
        if referrer_id != str(user_id):
            user_balances[referrer_id] = user_balances.get(referrer_id, 0) + 10
            bot.send_message(referrer_id, "🎉 Do‘stingiz sizning havolangiz orqali kirdi! +10 💎 olmos!")

    show_menu(message)


# 🔄 Menyu qayta ko‘rsatish
def show_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎥 Video yuklash", "🎬 Kinolar")
    markup.add("💰 Pul ishlash", "🎁 Bonus olish")
    markup.add("🔗 Referal havola", "💎 Mening olmoslarim")
    markup.add("📊 Statistika", "📢 Reklama berish")
    markup.add("📩 Admin bilan aloqa", "💎 Premium olish")

    if message.from_user.username == ADMIN_USERNAME[1:]:
        markup.add("👤 Foydalanuvchilar ro‘yxati")

    bot.send_message(message.chat.id, "📍 Quyidagi menyudan tanlang:", reply_markup=markup)


# 7️⃣ Obuna qayta tekshirish
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    user_id = call.message.chat.id
    if is_subscribed(user_id):
        bot.edit_message_text("✅ Obuna tasdiqlandi!", chat_id=user_id, message_id=call.message.message_id)
        send_welcome(call.message)
    else:
        bot.answer_callback_query(call.id, "🚫 Hali obuna bo‘lmagansiz!")


# 8️⃣ Admin menyusi
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
    total_users = len(all_users)
    bot.reply_to(message, f"👥 <b>Start bosgan foydalanuvchilar:</b>\n\n{users_text}\n\n📊 <b>Jami:</b> {total_users} ta",
                 parse_mode="HTML")


# 9️⃣ Foydali bo‘limlar
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


# 💰 Pul ishlash
@bot.message_handler(func=lambda message: message.text == "💰 Pul ishlash")
def earn_money(message):
    text = (
        "💰 <b>Botdan pul ishlash yo‘llari:</b>\n\n"
        "1️⃣ Do‘stingiz /start bossa — sizga +10 💎 beriladi.\n"
        "2️⃣ Har kuni bonus oling 🎁\n"
        "3️⃣ 200 💎 to‘plang — Premium oling 🌟\n"
        "4️⃣ 100 💎 to‘plang — Reklama joylang 📢"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")


# 🎁 Bonus olish
@bot.message_handler(func=lambda message: message.text == "🎁 Bonus olish")
def daily_bonus(message):
    user_id = message.chat.id
    now = datetime.now()
    last_time = user_last_bonus.get(user_id)
    if last_time and now - last_time < timedelta(hours=24):
        time_left = timedelta(hours=24) - (now - last_time)
        hours_left = int(time_left.total_seconds() // 3600)
        bot.send_message(message.chat.id, f"⏳ Bonusni {hours_left} soatdan keyin olasiz.")
        return

    user_last_bonus[user_id] = now
    user_balances[user_id] = user_balances.get(user_id, 0) + 5
    bot.send_message(message.chat.id, "🎁 Tabriklaymiz! Sizga 5 💎 bonus qo‘shildi!")


# 📊 Statistika
@bot.message_handler(func=lambda message: message.text == "📊 Statistika")
def show_stats(message):
    user_id = message.chat.id
    balance = user_balances.get(user_id, 0)
    referrals = sum(1 for refs in user_referrals.values() if refs == user_id)
    bot.send_message(message.chat.id,
        f"📊 <b>Statistika:</b>\n👥 Takliflar: {referrals}\n💎 Olmos: {balance}\n🎯 Do‘st uchun: +10 💎",
        parse_mode="HTML"
    )


# 📢 Reklama berish
@bot.message_handler(func=lambda message: message.text == "📢 Reklama berish")
def reklama_berish(message):
    user_id = message.chat.id
    balance = user_balances.get(user_id, 0)

    if balance < 100:
        bot.send_message(user_id, f"❌ Reklama joylash uchun kamida 100 💎 kerak.\nSizda: {balance} 💎 bor.")
        return

    bot.send_message(user_id, "📢 Reklamangizni yuboring (matn, rasm yoki video bo‘lishi mumkin):")
    bot.register_next_step_handler(message, reklama_qabul)


def reklama_qabul(message):
    user_id = message.chat.id
    user_balances[user_id] -= 100
    bot.send_message(user_id, "✅ Reklama qabul qilindi va tez orada joylanadi. -100 💎 hisobingizdan olindi.")
    bot.send_message(ADMIN_USERNAME, f"📢 Yangi reklama:\n\n{message.text}")


# 🎬 Kinolar tugmasi
@bot.message_handler(func=lambda message: message.text == "🎬 Kinolar")
def open_movies_channel(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🎬 Kinolar kanaliga o‘tish", url="https://t.me/KINOLAR_UZB12"))
    bot.send_message(message.chat.id, "🍿 Quyidagi tugma orqali kinolar kanaliga o‘ting:", reply_markup=markup)


# 🎥 Video yuklash
@bot.message_handler(func=lambda message: message.text == "🎥 Video yuklash")
def ask_video_link(message):
    bot.reply_to(message, "🎥 Video havolasini yuboring (TikTok, Instagram, Facebook yoki Twitter).")

@bot.message_handler(func=lambda message: message.text.startswith("http"))
def download_video(message):
    url = message.text.strip()
    bot.reply_to(message, "⏳ Yuklab olinmoqda...")

    try:
        if not any(d in url for d in ["tiktok.com", "instagram.com", "facebook.com", "x.com", "twitter.com", "fb.watch"]):
            bot.reply_to(message, "⚠️ Faqat TikTok, Instagram, Facebook yoki Twitter havolasi yuboring.")
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                'cookiefile': COOKIE_FILE if os.path.exists(COOKIE_FILE) else None,
                'format': 'mp4',
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)

            caption = "✨ <b>Yuklab beruvchi:</b> <a href='https://t.me/asqarov_uzbot'>@asqarov_uzbot</a> 💫"
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("➕ Kanalga qo‘shilish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))

            with open(video_path, 'rb') as v:
                bot.send_video(message.chat.id, v, caption=caption, parse_mode='HTML', reply_markup=markup)

    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik: {e}")

# 🌟 Haftalik Premium tizimi
premium_users = set()
last_week_winner = None

@bot.message_handler(func=lambda message: message.text == "💎 Premium olish")
def premium_info(message):
    user_id = message.chat.id
    is_premium = user_id in premium_users
    winner_text = (
        f"🏆 <b>Oxirgi Premium g‘olib:</b> {all_users.get(last_week_winner, 'hali yo‘q')}"
        if last_week_winner else "🏆 Hali Premium g‘olib aniqlanmagan."
    )
    if is_premium:
        bot.send_message(
            user_id,
            f"🌟 Siz hozir Premium foydalanuvchisiz!\n\n{winner_text}",
            parse_mode="HTML"
        )
    else:
        bot.send_message(
            user_id,
            f"💎 Haftada eng ko‘p olmos to‘plagan foydalanuvchi Premium oladi!\n\n{winner_text}",
            parse_mode="HTML"
        )

def check_weekly_winner():
    global last_week_winner
    while True:
        now = datetime.now()
        if now.weekday() == 6 and now.hour == 20:  # Yakshanba 20:00
            if not user_balances:
                time.sleep(3600)
                continue

            winner_id = max(user_balances, key=user_balances.get)
            winner_balance = user_balances[winner_id]

            if winner_id != last_week_winner:
                last_week_winner = winner_id
                premium_users.add(winner_id)

                bot.send_message(
                    ADMIN_USERNAME,
                    f"🏆 <b>Yangi haftalik g‘olib:</b> {all_users.get(winner_id, winner_id)}\n"
                    f"💎 {winner_balance} olmos bilan Premium oldi!",
                    parse_mode="HTML"
                )

                bot.send_message(
                    winner_id,
                    "🎉 Tabriklaymiz!\n"
                    "Siz haftaning eng faol foydalanuvchisisiz!\n"
                    "Sizga <b>Premium</b> berildi 💎🌟",
                    parse_mode="HTML"
                )

                for uid in all_users:
                    if uid != winner_id:
                        bot.send_message(
                            uid,
                            f"🏆 Bu haftada eng faol foydalanuvchi: "
                            f"{all_users.get(winner_id, 'bir foydalanuvchi')} — {winner_balance} 💎 bilan Premium oldi! 🌟"
                        )
            time.sleep(86400)
        else:
            time.sleep(3600)

threading.Thread(target=check_weekly_winner, daemon=True).start()


# 🧩 Flask webhook
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
    bot.process_new_updates([update])
    return "OK", 200


@app.route("/")
def home():
    return "<h2>✅ Bot ishlayapti!</h2><p>TikTok, Instagram, Facebook, Twitter videolarini yuklab beruvchi bot.</p>"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
