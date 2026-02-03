import os
import logging
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")  # لە Railway دابنێ
CHANNEL_USERNAME = "chanaly_boot"   # بەبێ @
OWNER_USERNAME = "Deva_harki"
COOKIES_FILE = "cookies.txt"        # ئەگەر هەیە

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)

# ================= FORCE JOIN =================
async def is_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(
            f"@{CHANNEL_USERNAME}",
            update.effective_user.id
        )
        return member.status in ("member", "administrator", "creator")
    except:
        return False

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_joined(update, context):
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 چۆین بکە", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ])
        await update.message.reply_text(
            "🔒 تکایە سەرەتا چۆینی چانەل بکە 👇",
            reply_markup=kb
        )
        return

    await update.message.reply_text(
        "👋 بەخێربێیت!\n\n"
        "🔗 لینک ڤیدیۆ بنێرە\n"
        "🎥 TikTok / Instagram / YouTube / Facebook\n\n"
        "ℹ️ ئەگەر ڤیدیۆ age‑restricted بێت → cookies پێویستە",
    )

# ================= DOWNLOAD =================
def download_video(url: str):
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title).80s.%(ext)s",
        "merge_output_format": "mp4",
        "quiet": True,
        "noplaylist": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "user_agent": "Mozilla/5.0",
    }

    if os.path.exists(COOKIES_FILE):
        ydl_opts["cookiefile"] = COOKIES_FILE

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# ================= HANDLE LINK =================
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    msg = await update.message.reply_text("⏳ تکایە چاوەڕوان بە...")

    try:
        file_path = download_video(url)

        await update.message.reply_video(
            video=open(file_path, "rb"),
            caption="✅ داونلۆد سەرکەوتوو بوو"
        )

        os.remove(file_path)
        await msg.delete()

    except yt_dlp.utils.DownloadError as e:
        error_text = str(e)

        if "comfortable for some audiences" in error_text:
            await msg.edit_text(
                "🔞 ئەم ڤیدیۆیە سنووردارە (Age‑Restricted)\n\n"
                "❗ TikTok پێویستی بە cookies هەیە\n"
                "📌 بێ cookies ناتوانرێت داونلۆد بکرێت"
            )
        else:
            await msg.edit_text(
                "❌ داونلۆد سەرکەوتوو نەبوو\n"
                "🔁 تکایە لینکێکی تر تاقی بکەوە"
            )

    except Exception as e:
        await msg.edit_text("❌ هەڵەیەک ڕوویدا، دواتر تاقی بکەوە")
        logging.error(e)

# ================= MAIN =================
def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN set نەکراوە")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()