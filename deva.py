import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters, CallbackQueryHandler
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "chanaly_boot"
OWNER_USERNAME = "Deva_harki"


# ---------- دوگمەکان ----------
def main_buttons():
    keyboard = [
        [InlineKeyboardButton("⬇️ داونلۆد ڤیدیۆ", callback_data="download")],
        [InlineKeyboardButton("👨‍💻 ئەدمین پانیل", callback_data="admin")],
        [InlineKeyboardButton("✉️ نامە بۆ خاوەن بوت", url=f"https://t.me/{OWNER_USERNAME}")]
    ]
    return InlineKeyboardMarkup(keyboard)


# ---------- فۆرسی چۆین ----------
async def force_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)

    if member.status in ["left", "kicked"]:
        keyboard = [
            [InlineKeyboardButton("📢 چوونە چەناڵ", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        await update.message.reply_text(
            "🚫 تکایە سەرەتا بچۆرە چەناڵ بۆ بەکارهێنانی بۆت 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return False
    return True


# ---------- داونلۆد ڤیدیۆ ----------
def download_video(url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'video.%(ext)s',
        'quiet': True,
        'merge_output_format': 'mp4'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    for f in os.listdir():
        if f.startswith("video."):
            return f


# ---------- /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 بەخێربێیت بۆ بۆتی داونلۆد\n\n"
        "🔗 لینکی هەر ڤیدیۆیەک بنێرە\n"
        "🎥 بۆت ڤیدیۆکە بە دەنگ دادەبەزێنێت",
        reply_markup=main_buttons()
    )


# ---------- وەرگرتنی لینک ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await force_join(update, context):
        return

    url = update.message.text
    msg = await update.message.reply_text("⏳ داونلۆد دەستی پێکرد... تکایە چاوەڕێ بکە")

    try:
        file_path = download_video(url)

        await update.message.reply_video(video=open(file_path, "rb"))
        os.remove(file_path)
        await msg.delete()

    except Exception as e:
        await msg.edit_text("❌ هەڵەیەک ڕوویدا، لینکەکە دروستە؟")


# ---------- ئەدمین پانیل ----------
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.username != OWNER_USERNAME:
        await query.edit_message_text("⛔ تۆ ئەدمین نیت")
        return

    await query.edit_message_text("👨‍💻 بەخێربێیت بۆ ئەدمین پانیل")


# ---------- Callback ----------
async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.data == "admin":
        await admin_panel(update, context)


# ---------- MAIN ----------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(callbacks))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()