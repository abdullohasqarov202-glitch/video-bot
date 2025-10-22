import os
import telebot
import yt_dlp

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Salom! Menga Instagram, TikTok yoki YouTube link yubor — men video yuklab beraman 🎥")

@bot.message_handler(func=lambda msg: True)
def download(message):
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
