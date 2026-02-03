import os
import logging
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "chanaly_boot"
OWNER_USERNAME = "Deva_harki"
COOKIES_PATH = "/app/cookies.txt"
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO)

# ================= FORCE JOIN =================
async def is_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", update.effective_user.id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False

# ================= BUTTONS =================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 داونلۆدی ڤیدیۆ", callback_data="download")],
        [InlineKeyboardButton("ℹ️ زانیاری بۆت", callback_data="about")],
        [InlineKeyboardButton("📨 پەیوەندی بە خاوەن بۆت", callback_data="owner")]
    ])

def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 گەڕانەوە", callback_data="home")]])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_joined(update, context):
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("📢 چۆین بکە", url=f"https://t.me/{CHANNEL_USERNAME}")]])
        await update.message.reply_text("🔒 تکایە سەرەتا چۆینی چانەل بکە👇", reply_markup=kb)
        return

    await update.message.reply_text(
        "👋 بەخێربێیت!\n\n"
        "🔗 لینک ڤیدیۆ بنێرە (TikTok / Instagram / YouTube / Facebook / X)\n"
        "ℹ️ Age-restricted → cookies.txt پێویستە",
        reply_markup=main_menu()
    )

# ================= BUTTON CALLBACK =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "home":
        await query.edit_message_text("🏠 سەرەتا", reply_markup=main_menu())
    elif query.data == "download":
        await query.edit_message_text("🔗 تکایە لینک ڤیدیۆ بنێرە", reply_markup=back_menu())
    elif query.data == "about":
        await query.edit_message_text(f"🤖 Video Downloader Bot\n⚡ خێرا • 🔐 پارێزراو • 🎥 کوالیتی بەرز\n👨‍💻 @{OWNER_USERNAME}", reply_markup=back_menu())
    elif query.data == "owner":
        await query.edit_message_text(f"📨 پەیوەندی 👇\nhttps://t.me/{OWNER_USERNAME}", reply_markup=back_menu())

# ================= DOWNLOAD FUNCTION =================
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

    if os.path.exists(COOKIES_PATH):
        ydl_opts["cookiefile"] = COOKIES_PATH

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)

        # Fallback audio بۆ >50MB
        if os.path.getsize(file_path) > 50*1024*1024:
            ydl_opts_audio = {
                "format": "bestaudio/best",
                "outtmpl": f"{DOWNLOAD_DIR}/%(title).80s.mp3",
                "quiet": True,
                "noplaylist": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl2:
                info2 = ydl2.extract_info(url, download=True)
                file_path = ydl2.prepare_filename(info2)

        return file_path

# ================= HANDLE LINK =================
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    msg = await update.message.reply_text("⏳ داونلۆد دەستی پێکرد...")

    try:
        file_path = download_video(url)
        await update.message.reply_video(video=open(file_path, "rb"), caption="✅ داونلۆد سەرکەوتوو بوو")
        os.remove(file_path)
        await msg.delete()

    except yt_dlp.utils.DownloadError as e:
        error_text = str(e)
        if "comfortable for some audiences" in error_text:
            await msg.edit_text("🔞 ڤیدیۆ سنووردارە (Age-restricted)\n❗ پێویستە cookies.txt هەبێت")
        else:
            await msg.edit_text("❌ داونلۆد سەرکەوتوو نەبوو\n🔁 تکایە لینکێکی تر تاقی بکەوە")
        logging.error(e)
    except Exception as e:
        await msg.edit_text("❌ هەڵەیەک ڕوویدا، دواتر تاقی بکەوە")
        logging.error(e)

# ================= MAIN =================
def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN set نەکراوە")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()