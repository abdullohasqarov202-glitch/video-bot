# web.py
import os
from flask import Flask, request
import telebot

TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Render dashboard -> Environment -> add TELEGRAM_TOKEN
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN muhit o'zgaruvchisi aniqlanmadi")

bot = telebot.TeleBot(TOKEN, threaded=False)  # threaded=False muhim (gunicorn bilan yaxshi ishlaydi)
app = Flask(__name__)

# --- Bu yerga bot handlerlarini qo'shing (xuddi telegram_bot.py ichidagi handlerlar) ---
@bot.message_handler(commands=["start"])
def start_msg(message):
    bot.reply_to(message, "Salom! Bot ishga tushdi.")

# boshqa handlerlar...
# -------------------------------------------------------------------------------

@app.route("/"+TOKEN, methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "", 200

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)
