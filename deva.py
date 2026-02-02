import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "chanaly_boot"
OWNER_USERNAME = "Deva_harki"


# ---------- Buttons ----------
def buttons():
    keyboard = [
        [InlineKeyboardButton("⬇️ داونلۆد ڤیدیۆ", callback_data="dl")],
        [InlineKeyboardButton("👨‍💻 ئەدمین پانیل", callback_data="admin")],
        [InlineKeyboardButton("✉️ نامە بۆ خاوەن بوت", url=f"https://t.me/{OWNER_USERNAME}")]
    ]
    return InlineKeyboardMarkup(keyboard)


# ---------- Force Join ----------
async def force_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)

    if member.status in ["left", "kicked"]:
        await update.message.reply_text(
            "🚫 بۆ بەکارهێنانی بۆت پێویستە ئەندام بیت لەم چەناڵە 👇\n"
            f"https://t.me/{CHANNEL_USERNAME}"
        )
        return False
    return True


# ---------- Smart Loading Messages ----------
loading_msgs = [
    "⏳ داونلۆد دەستی پێکرد... تکایە ئارام بگرە 😊",
    "📥 ڤیدیۆکە قەبارەی زۆر هەیە، تۆزێک چاوەڕێ بکە 🎥",
    "⚡ خەریکی ئامادەکردنی ڤیدیۆ + دەنگین...",
]


async def animate_loading(msg):
    for text in loading_msgs:
        await msg.edit_text(text)
        await asyncio.sleep(3)


# ---------- Download Video ----------
def download_video(url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'video.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
        'noplaylist': True,
        'socket_timeout': 15,
        'retries': 3
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    for f in os.listdir():
        if f.startswith("video."):
            return f


# ---------- Start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 بەخێربێیت بۆ بۆتی داونلۆدی زیرەک 🤖✨\n\n"
        "🔗 تەنها لینکی ڤیدیۆ بنێرە\n"
        "🎥 بۆت ڤیدیۆکە بە کوالیتی بەرز + دەنگ دادەبەزێنێت\n\n"
        "دوگمەکان بەکاربهێنە 👇",
        reply_markup=buttons()
    )


# ---------- Handle Link ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await force_join(update, context):
        return

    text = update.message.text

    if "http" not in text:
        return

    msg = await update.message.reply_text("⏳ داونلۆد دەستی پێکرد...")
    asyncio.create_task(animate_loading(msg))

    try:
        file_path = download_video(text)
        await update.message.reply_video(video=open(file_path, "rb"))
        os.remove(file_path)
        await msg.delete()
    except:
        await msg.edit_text("❌ هەڵەیەک ڕوویدا، لینکەکە دروستە؟")


# ---------- Admin Panel ----------
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.username != OWNER_USERNAME:
        await query.edit_message_text("⛔ تۆ ئەدمین نیت")
        return

    await query.edit_message_text("👨‍💻 بەخێربێیت بۆ ئەدمین پانیل")


# ---------- Callbacks ----------
async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "admin":
        await admin_panel(update, context)


# ---------- Main ----------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(callbacks))

    app.run_polling()


if __name__ == "__main__":
    main()