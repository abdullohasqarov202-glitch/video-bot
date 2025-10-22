import os
import telebot
import yt_dlp

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@Asqarov_2007"  # 👈 bu yerga o'z kanal username’ni yoz ( @ bilan )

bot = telebot.TeleBot(BOT_TOKEN)

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    if is_subscribed(message.from_user.id):
        bot.reply_to(message, "👋 Salom! Menga Instagram, TikTok yoki YouTube link yubor — men video yuklab beraman 🎥")
    else:
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("✅ Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_ID[1:]}")
        markup.add(btn)
        bot.send_message(
            message.chat.id,
            "❌ Siz hali kanalga obuna bo‘lmagansiz!\n\nIltimos, avval kanalga obuna bo‘ling, so‘ngra /start bosing 🔄",
            reply_markup=markup
        )

@bot.message_handler(func=lambda msg: True)
def download(message):
    if not is_subscribed(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("✅ Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_ID[1:]}")
        markup.add(btn)
        bot.send_message(message.chat.id, "❌ Avval kanalga obuna bo‘ling!", reply_markup=markup)
        return

    url = message.text.strip()
    bot.reply_to(message, "⏳ Yuklanmoqda, kuting...")

    try:
        ydl_opts = {'outtmpl': 'video.mp4', 'format': 'mp4', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        with open("video.mp4", "rb") as video:
            bot.send_video(message.chat.id, video)
        os.remove("video.mp4")
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik: {e}")

print("✅ Bot ishga tushdi!")
bot.infinity_polling()
