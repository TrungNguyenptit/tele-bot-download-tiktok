import os
import yt_dlp
from playwright.sync_api import sync_playwright
import random
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ===================== DOUYIN COOKIE =====================
def refresh_douyin_cookies():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="zh-CN"
        )

        page = context.new_page()
        page.goto("https://www.douyin.com", timeout=60000)

        # ⏳ ĐỢI LOAD
        page.wait_for_timeout(6000)

        # 🖱 GIẢ LẬP HÀNH VI NGƯỜI DÙNG
        for _ in range(3):
            page.mouse.wheel(0, random.randint(300, 800))
            page.wait_for_timeout(random.randint(1000, 2000))

        cookies = context.cookies()
        browser.close()

    # Save cookies.txt
    with open("cookies.txt", "w", encoding="utf-8") as f:
        for c in cookies:
            f.write(
                f"{c['domain']}\t"
                f"{'TRUE' if c['domain'].startswith('.') else 'FALSE'}\t"
                f"{c['path']}\t"
                f"{'TRUE' if c['secure'] else 'FALSE'}\t"
                f"{int(c['expires']) if c['expires'] else 0}\t"
                f"{c['name']}\t"
                f"{c['value']}\n"
            )

# ===================== HANDLER =====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    is_tiktok = "tiktok.com" in text
    is_douyin = "douyin.com/video" in text

    if not is_tiktok and not is_douyin:
        await update.message.reply_text("❌ Send TikTok or Douyin VIDEO link.")
        return

    await update.message.reply_text("⏳ Downloading video...")

    try:
        ydl_opts = {
            "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
            "format": "mp4",
            "merge_output_format": "mp4",
            "cookiefile": "cookies.txt",
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
            refresh_douyin_cookies()
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
    refresh_douyin_cookies()  # 👈 gọi 1 lần
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
