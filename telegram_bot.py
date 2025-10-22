import os
import yt_dlp
# ... (boshqa kodlar) ...

def download_video_with_cookies(url, chat_id, bot):
    # cookies fayl manzili (repo rootda yoki /opt/render/project/src/)
    cookies_path = "cookies.txt"
    cookiefile = cookies_path if os.path.exists(cookies_path) else None

    ydl_opts = {
        "format": "best",
        "outtmpl": "/tmp/%(title)s.%(ext)s",
        "cookiefile": cookiefile,   # agar None bo'lsa yt-dlp cookie ishlatmaydi
        "noplaylist": True,
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        with open(filename, "rb") as f:
            bot.send_video(chat_id, f)
    except yt_dlp.utils.DownloadError as e:
        # aniqlik uchun xabar yubor
        bot.send_message(chat_id, f"Xatolik yuz berdi: {e}")
    except Exception as e:
        bot.send_message(chat_id, f"Umumiy xato: {e}")
