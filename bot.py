import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    is_tiktok = "tiktok.com" in text
    is_douyin = "douyin.com/video" in text

    if not is_tiktok and not is_douyin:
        await update.message.reply_text(
            "❌ Send TikTok or Douyin VIDEO link."
        )
        return

    await update.message.reply_text("⏳ Downloading...")

    try:
        ydl_opts = {
            "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
            "format": "mp4",
            "merge_output_format": "mp4",
            "quiet": True,
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
        }

        if is_douyin:
            ydl_opts["cookiefile"] = "cookies.txt"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(text, download=True)
            filename = ydl.prepare_filename(info)
            caption = info.get("description", "")[:1000]

        await update.message.reply_video(
            video=open(filename, "rb"),
            caption=caption
        )

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"❌ Error:\n{e}")

def main():
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    app.run_polling()

if __name__ == "__main__":
    main()
