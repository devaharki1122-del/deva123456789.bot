import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ===== ENV =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
TIKTOK_COOKIES = os.getenv("TIKTOK_COOKIES")

CHANNEL_USERNAME = "chanaly_boot"   # بەبێ @
OWNER_USERNAME = "Deva_harki"
USERS_FILE = "users.txt"


# ===== Save Users =====
def save_user(user_id):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w").close()

    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()

    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")


# ===== Force Join =====
async def force_join_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(
            f"@{CHANNEL_USERNAME}",
            update.effective_user.id
        )
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# ===== Keyboards =====
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 داونلۆدی ڤیدیۆ", callback_data="download")],
        [InlineKeyboardButton("ℹ️ زانیاری بۆت", callback_data="about")],
        [InlineKeyboardButton("📨 پەیوەندی بە خاوەن بۆت", callback_data="owner")]
    ])


def back_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 گەڕانەوە", callback_data="home")]
    ])


# ===== Start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id)

    if not await force_join_check(update, context):
        keyboard = [
            [InlineKeyboardButton("📢 چۆین بکە", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("✅ پشکنینەوە", callback_data="check_join")]
        ]
        await update.message.reply_text(
            "🔒 پێویستە سەرەتا چۆینی چانەل بکەیت 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await update.message.reply_text(
        "👋 بەخێربێیت\n\n🔗 لینک ڤیدیۆی TikTok بنێرە 👇",
        reply_markup=main_menu()
    )


# ===== Buttons =====
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "home":
        await query.edit_message_text("🏠 سەرەتا", reply_markup=main_menu())

    elif query.data == "download":
        await query.edit_message_text(
            "🔗 تکایە لینک ڤیدیۆ بنێرە",
            reply_markup=back_menu()
        )

    elif query.data == "about":
        await query.edit_message_text(
            "🤖 TikTok Downloader Bot\n\n"
            "⚡ خێرا • 🔐 پارێزراو • 🎥 کوالیتی بەرز\n\n"
            "👨‍💻 @Deva_harki",
            reply_markup=back_menu()
        )

    elif query.data == "owner":
        await query.edit_message_text(
            f"📨 پەیوەندی 👇\nhttps://t.me/{OWNER_USERNAME}",
            reply_markup=back_menu()
        )

    elif query.data == "check_join":
        if await force_join_check(update, context):
            await query.edit_message_text("✅ بەسەرکەوتوویی", reply_markup=main_menu())
        else:
            await query.answer("❌ هێشتا چۆینت نەکردووە", show_alert=True)


# ===== Download Function =====
def download_video(url):
    if TIKTOK_COOKIES:
        with open("cookies.txt", "w") as f:
            f.write(TIKTOK_COOKIES)

    ydl_opts = {
        "format": "best",
        "outtmpl": "video.%(ext)s",
        "quiet": True,
        "noplaylist": True,

        # TikTok Fix
        "cookiefile": "cookies.txt",
        "user_agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120 Safari/537.36",

        "ignoreerrors": True,
        "nocheckcertificate": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


# ===== Handle Links =====
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "tiktok.com" not in text:
        return

    msg = await update.message.reply_text("⏳ داونلۆد دەستی پێکرد...")

    try:
        file_path = download_video(text)
        await update.message.reply_video(video=open(file_path, "rb"))
        os.remove(file_path)
        await msg.delete()

    except Exception:
        await msg.edit_text("❌ ناتوانرێت ئەم ڤیدیۆیە داونلۆد بکرێت")


# ===== Main =====
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()