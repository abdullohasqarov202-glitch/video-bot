import os
from yt_dlp import YoutubeDL

def progress_hook(d):
    status = d.get("status")
    if status == "downloading":
        filename = d.get("filename", "")
        downloaded = d.get("downloaded_bytes")
        total = d.get("total_bytes") or d.get("total_bytes_estimate")
        if total and downloaded:
            perc = downloaded / total * 100
            print("Yuklanmoqda: {} ({:.1f}%)".format(filename, perc))
        else:
            print("Yuklanmoqda: {}".format(filename))
    elif status == "finished":
        print("Yuklash tugadi, birlashtirilmoqda...")

def main():
    print("Instagram / TikTok / YouTube yuklovchi dastur")
    url = input("➡️ Video havolasini kiriting: ").strip()
    if not url:
        print("Hech qanday havola kiritilmadi. Dastur tugadi.")
        return

    # Agar cookies.txt shu papkada bo'lsa, foydalanamiz
    cookies_file = "cookies.txt"
    if os.path.exists(cookies_file):
        print("cookies.txt topildi — login talab qilinadigan videolar uchun ishlatiladi.")
        cookiefile = cookies_file
    else:
        print("cookies.txt topilmadi — faqat ochiq (public) videolar yuklanadi.")
        cookiefile = None

    ydl_opts = {
        "outtmpl": "%(title)s.%(ext)s",
        "cookiefile": cookiefile,
        "format": "best",            # ffmpeg kerak bo'lmagan bitta fayl format
        "noplaylist": True,
        "progress_hooks": [progress_hook],
        "quiet": False,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("✅ Video muvaffaqiyatli yuklab olindi!")
    except Exception as e:
        print("❌ Xatolik yuz berdi:", e)

if __name__ == "__main__":
    main()
