import os
from flask import Flask, request
import telebot
import yt_dlp
from telebot import types

# 🔹 Muhit o'zgaruvchilari (TOKEN va ADMIN_ID)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")  # Telegram ID (raqam)
if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN aniqlanmadi!")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# 🔹 Asosiy menyu tugmalari
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📥 Video yuklab ber", "🎨 Rasm yasab ber")
    markup.row("💬 Adminga murojaat")
    return markup

# 🟢 /start komandasi
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "👋 Assalomu alaykum!\n\nMen yordam bera olaman:\n"
        "📥 Video yuklab berish\n🎨 Rasm yasash\n💬 Adminga murojaat\n\nTanlang 👇",
        reply_markup=main_menu()
    )

# 🟢 1. Adminga murojaat
@bot.message_handler(func=lambda m: m.text == "💬 Adminga murojaat")
def contact_admin(message):
    bot.reply_to(message, "✍️ Adminga yuboriladigan xabarni yozing:")
    bot.register_next_step_handler(message, send_to_admin)

def send_to_admin(message):
    if ADMIN_ID:
        bot.send_message(
            ADMIN_ID,
            f"📩 <b>Yangi murojaat!</b>\n\n👤 <b>Foydalanuvchi:</b> {message.from_user.first_name}\n"
            f"🆔 <b>ID:</b> {message.from_user.id}\n💬 <b>Xabar:</b> {message.text}",
            parse_mode="HTML"
        )
        bot.reply_to(message, "✅ Xabaringiz adminga yuborildi!")
    else:
        bot.reply_to(message, "❌ Admin ID o‘rnatilmagan (ADMIN_ID yo‘q).")

# 🟢 2. Rasm yasash
@bot.message_handler(func=lambda m: m.text == "🎨 Rasm yasab ber")
def ask_prompt(message):
    bot.reply_to(message, "🖌 Qanday rasm yasab beray? Tavsif yozing:")
    bot.register_next_step_handler(message, generate_image)

def generate_image(message):
    prompt = message.text
    bot.reply_to(message, f"⏳ '{prompt}' mavzusida rasm yaratilmoqda...")
    
    # ⚠️ Bu joyga siz haqiqiy AI rasm API qo‘shishingiz mumkin.
    # Test uchun tayyor fayl yuboramiz:
    test_image_path = "sample.jpg"
    if os.path.exists(test_image_path):
        with open(test_image_path, 'rb') as img:
            bot.send_photo(message.chat.id, img, caption=f"🎨 Tayyor rasm: {prompt}")
    else:
        bot.reply_to(message, "⚠️ Hozircha test holatida. sample.jpg topilmadi.")

# 🟢 3. Video yuklab berish
@bot.message_handler(func=lambda m: m.text == "📥 Video yuklab ber")
def ask_video(message):
    bot.reply_to(message, "📎 Menga video havolasini yuboring:")
    bot.register_next_step_handler(message, download_video)

def download_video(message):
    url = message.text.strip()
    bot.reply_to(message, "📥 Yuklanmoqda, kuting...")

    try:
        ydl_opts = {'format': 'best', 'outtmpl': '/tmp/%(title)s.%(ext)s'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video)
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik: {e}")

# 🟢 Webhook endpoint
@app.route(f"/{TELEGRAM_TOKEN}", methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode('utf-8'))
    bot.process_new_updates([update])
    return "OK", 200

# 🟢 Flask serverni ishga tushirish
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)
