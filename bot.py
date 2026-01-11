import os
import yt_dlp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)


DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "tiktok.com" not in text:
        await update.message.reply_text("Send me a TikTok link.")
        return

    await update.message.reply_text("Downloading…")

    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
        "format": "mp4",
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(text, download=True)
            filename = ydl.prepare_filename(info)
            caption = info.get("description", "")

        # Giới hạn caption Telegram (1024 ký tự)
        if len(caption) > 1000:
            caption = caption[:1000] + "..."

        await update.message.reply_video(
            video=open(filename, "rb"),
            caption=caption,
        )

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    print("BOT_TOKEN =", repr(BOT_TOKEN))
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
