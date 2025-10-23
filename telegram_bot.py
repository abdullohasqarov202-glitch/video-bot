# telegram_webhook_bot.py
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

# Referal tizimi uchun oddiy xotira (haqiqiy bazada saqlash uchun keyin fayl yoki DB qo‘shish mumkin)
user_referrals = {}
user_balances = {}

# 2️⃣ Cookie matni — ixtiyoriy
INSTAGRAM_COOKIE = """
# Netscape HTTP Cookie File

.youtube.com	TRUE	/	TRUE	1794584724	__Secure-3PSID	g.a0002Ag3MBXSNz4344JortVw1FRVWf7XgAg28Xat7PhHLwRfTI8EBi3AN7kpLmeRR-u8bBGqaAACgYKAWESARUSFQHGX2MiT6sRwx8gYe5MKsZjtU0huBoVAUF8yKqOYonvW49ryT7r28fW85Vt0076
.youtube.com	TRUE	/	TRUE	1791560722	__Secure-1PSIDTS	sidts-CjUBmkD5S7A3wHIGr4JetDHI0LycstqhVyry1eQveIoJ6f6QJ2503JAnLeGuu6Z5MdtMtFxf-BAA
.youtube.com	TRUE	/	TRUE	1794584724	SAPISID	EeFNaiw6v4rBfiMz/AJ_dw-IsQd8A9LlNq
.youtube.com	TRUE	/	TRUE	1792660165	__Secure-1PSIDCC	AKEyXzVeOpL7s5-HawhR58LBclgJ-2xQcNd4dYhI3hAj65ynLNg4UqKVPVjed0jcgLN7aTDJ8A
.youtube.com	TRUE	/	TRUE	1794584724	SSID	AHBPpTtwibp7lww9v
.youtube.com	TRUE	/	TRUE	1794584724	__Secure-1PAPISID	EeFNaiw6v4rBfiMz/AJ_dw-IsQd8A9LlNq
.youtube.com	TRUE	/	TRUE	1794584724	__Secure-1PSID	g.a0002Ag3MBXSNz4344JortVw1FRVWf7XgAg28Xat7PhHLwRfTI8Ez4vMo_2-Xs_iJWgHJF4G_wACgYKAe0SARUSFQHGX2MiA6Yc4gB6gfQd2P4x6G-FcxoVAUF8yKpL56BLWJjZMOTVsbRgePW60076
.youtube.com	TRUE	/	TRUE	1794584724	__Secure-3PAPISID	EeFNaiw6v4rBfiMz/AJ_dw-IsQd8A9LlNq
.youtube.com	TRUE	/	TRUE	1792660165	__Secure-3PSIDCC	AKEyXzXfICK8_SaicnQUVt1ByEdI2VQlWXxWMwkVC1yQrRZcc6xJhsEAqz_dA0GSxATs6LhiaI4
.youtube.com	TRUE	/	TRUE	1791560722	__Secure-3PSIDTS	sidts-CjUBmkD5S7A3wHIGr4JetDHI0LycstqhVyry1eQveIoJ6f6QJ2503JAnLeGuu6Z5MdtMtFxf-BAA
.youtube.com	TRUE	/	TRUE	1794584724	LOGIN_INFO	AFmmF2swRQIgc2AHYhNbUCOROjoNmDyqdmW-N9Eootdl09pDD9oeI5cCIQCBZXqRNv6_tbYo67UZu83fMsMw3IsuwWJdYafM2W4uEg:QUQ3MjNmeVoxQS1DN1hzam5QeXpoclNfTlNabmpjU3NCa0gxUjV5aHp5c01MQ0UwUTR3bTJkV0hzTVQyVEt3LS1VeWhTT1F5LThZQ3ZuVnVzUlJaVDgybzVBV2JzT09tSkNLWlczbkFFYVctSGhpQk1Gd3Z4VW9qNGZUN1doMHRKNy0weGhRanNVbDNxYjk5VmxyTVJSY3pMV2UwUUFsSDdn
.youtube.com	TRUE	/	FALSE	0	PREF	f4=4000000&f6=40000000&tz=UTC&f7=100&hl=en
.youtube.com	TRUE	/	TRUE	0	YSC	-ftbJlQZeIo
.youtube.com	TRUE	/	TRUE	1776675890	__Secure-ROLLOUT_TOKEN	CIaOhP2TkPiU_gEQsrPv3rm3kAMYx--s37m3kAM%3D
.youtube.com	TRUE	/	TRUE	1776676165	VISITOR_INFO1_LIVE	6DU_l1Kw67w
.youtube.com	TRUE	/	TRUE	1776676165	VISITOR_PRIVACY_METADATA	CgJVWhIEGgAgUw%3D%3D
.youtube.com	TRUE	/	TRUE	1824196165	__Secure-YT_TVFAS	t=489201&s=2
.youtube.com	TRUE	/	TRUE	1776676165	DEVICE_INFO	ChxOelUyTXprMk9UVXhNak14T0RVeU1UQXhOZz09EMW+4scGGLK84scG
.youtube.com	TRUE	/tv	TRUE	1793956165	__Secure-YT_DERP	CNGRsoedAQ%3D%3D
"""

# 3️⃣ Start / help buyrug‘i (referal tizimi bilan)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.chat.id
    args = message.text.split()

    # referal havoladan kirgan foydalanuvchi uchun
    if len(args) > 1:
        referrer_id = args[1]
        if referrer_id != str(user_id):  # o‘zini o‘zi taklif qilmasin
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
                'cookiefile': 'cookies.txt' if INSTAGRAM_COOKIE.strip() else None,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)

            with open(video_path, 'rb') as video:
                bot.send_video(message.chat.id, video)

    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik: {e}")

# 6️⃣ Flask webhook yo‘li — to‘g‘ri versiya!
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Asosiy sahifa (GET)
@app.route("/", methods=["GET"])
def home():
    return "<h2>✅ Bot server ishlayapti!</h2><p>Video bot Render serverda muvaffaqiyatli ishga tushdi.</p>"

# 7️⃣ Ishga tushirish
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
