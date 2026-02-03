import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ---------- Config ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")  #      : "12345:ABCDEF"
CHANNEL_USERNAME = "chanaly_boot"  #  @
OWNER_USERNAME = "Deva_harki"
USERS_FILE = "users.txt"

COOKIES_FILE = "cookies.txt"  #  cookies export   browser

# ---------- Users Save ----------
def save_user(user_id):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            f.write("")
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

# ---------- Force Join ----------
async def force_join_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ---------- Keyboards ----------
def main_menu():
    keyboard = [
        [InlineKeyboardButton("  ", callback_data="download")],
        [InlineKeyboardButton("  ", callback_data="about")],
        [InlineKeyboardButton("    ", callback_data="owner")],
        [InlineKeyboardButton(" Admin Panel", callback_data="admin")]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("   ", callback_data="home")]])

# ---------- Start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id)
    joined = await force_join_check(update, context)

    if not joined:
        keyboard = [
            [InlineKeyboardButton("  ", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton(" ", callback_data="check_join")]
        ]
        await update.message.reply_text(
            "        ",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await update.message.reply_text(
        "      \n\n     ",
        reply_markup=main_menu()
    )

# ---------- Buttons ----------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "home":
        await query.edit_message_text(" ", reply_markup=main_menu())

    elif query.data == "about":
        await query.edit_message_text(
            "  \n\n"
            "    :\n"
            "TikTok • Instagram • Facebook • YouTube\n\n"
            "     \n\n"
            f"   @{OWNER_USERNAME}",
            reply_markup=back_button()
        )

    elif query.data == "owner":
        await query.edit_message_text(
            f"     \n\nhttps://t.me/{OWNER_USERNAME}",
            reply_markup=back_button()
        )

    elif query.data == "admin":
        if query.from_user.username != OWNER_USERNAME:
            await query.edit_message_text("  ", reply_markup=back_button())
            return
        with open(USERS_FILE, "r") as f:
            count = len(f.readlines())
        await query.edit_message_text(f" Admin Panel\n\n  : {count}", reply_markup=back_button())

    elif query.data == "download":
        await query.edit_message_text("       ", reply_markup=back_button())

    elif query.data == "check_join":
        joined = await force_join_check(update, context)
        if joined:
            await query.edit_message_text("   ", reply_markup=main_menu())
        else:
            await query.answer("   ", show_alert=True)

# ---------- Download ----------
def download_video(url, filename="video.mp4"):
    ydl_opts = {
        "format": "bv*+ba/best",
        "outtmpl": filename,
        "noplaylist": True,
        "quiet": True,
        "cookiefile": COOKIES_FILE,
        "age_limit": 0,
        "geo_bypass": True,
        "geo_bypass_country": "US",
        "retries": 10,
        "fragment_retries": 10,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept-Language": "en-US,en;q=0.9",
        },
        "ignoreerrors": False,
        "nocheckcertificate": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "http" not in text:
        return
    await update.message.reply_text("   ...")

    try:
        file_name = "video.mp4"
        download_video(text, file_name)
        await update.message.reply_video(video=open(file_name, "rb"))
        os.remove(file_name)
    except Exception as e:
        await update.message.reply_text(f"  \n{e}")

# ---------- Main ----------
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()