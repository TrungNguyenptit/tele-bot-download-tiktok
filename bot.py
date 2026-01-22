import os
import csv
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def is_tiktok_profile(url: str):
    return "tiktok.com/@" in url and "/video/" not in url

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    is_tiktok = "tiktok.com" in text
    is_douyin = "douyin.com/video" in text
    is_profile = is_tiktok_profile(text)

    # ---------- PROFILE TIKTOK -> EXPORT CSV ----------
    if is_profile:
        await update.message.reply_text("📂 Crawling TikTok profile...")

        try:
            ydl_opts = {
                "quiet": True,
                "extract_flat": True,   # chỉ lấy metadata, không tải video
                "skip_download": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=False)

            username = info.get("uploader", "tiktok_profile")
            entries = info.get("entries", [])

            if not entries:
                await update.message.reply_text("❌ No videos found on this profile.")
                return

            csv_file = f"{DOWNLOAD_DIR}/{username}_videos.csv"

            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["video_url", "video_id", "description"])

                for e in entries:
                    video_url = e.get("url")
                    video_id = e.get("id")
                    desc = (e.get("title") or "").replace("\n", " ")

                    # Chuẩn hóa link TikTok
                    if video_url and not video_url.startswith("http"):
                        video_url = f"https://www.tiktok.com/@{username}/video/{video_id}"

                    writer.writerow([video_url, video_id, desc])

            await update.message.reply_document(
                document=open(csv_file, "rb"),
                filename=os.path.basename(csv_file),
                caption=f"✅ Exported {len(entries)} videos from @{username}"
            )

            os.remove(csv_file)

        except Exception as e:
            await update.message.reply_text(f"❌ Error:\n{e}")

        return

    # ---------- VIDEO DOWNLOAD (TIKTOK / DOUYIN) ----------
    if not is_tiktok and not is_douyin:
        await update.message.reply_text(
            "❌ Send TikTok / Douyin VIDEO link or TikTok PROFILE link."
        )
        return

    await update.message.reply_text("⏳ Downloading video...")

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
