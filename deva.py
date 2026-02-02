import os
import yt_dlp
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_USERNAME = "chanaly_boot"
OWNER_USERNAME = "Deva_harki"
USERS_FILE = "users.txt"


# ---------------- Save Users ----------------
def save_user(user_id):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w").close()

    with open(USERS_FILE, "r+") as f:
        users = f.read().splitlines()
        if str(user_id) not in users:
            f.write(f"{user_id}\n")


# ---------------- Force Join ----------------
async def force_join_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return True


# ---------------- Menus ----------------
def main_menu():
    keyboard = [
        [InlineKeyboardButton("📥 داونلۆدی ڤیدیۆ", callback_data="download")],
        [InlineKeyboardButton("ℹ️ زانیاری بۆت", callback_data="about")],
        [InlineKeyboardButton("📨 نامە بۆ خاوەن بۆت", callback_data="owner")],
        [InlineKeyboardButton("🛠 Admin Panel", callback_data="admin")]
    ]
    return InlineKeyboardMarkup(keyboard)


def back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 چانەل", url=f"https://t.me/{CHANNEL_USERNAME}")],
        [InlineKeyboardButton("🔙 گەڕانەوە بۆ سەرەتا", callback_data="home")]
    ])


# ---------------- Start ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)

    joined = await force_join_check(update, context)
    if not joined:
        keyboard = [
            [InlineKeyboardButton("📢 چۆین بکە", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("✅ پشکنینەوە", callback_data="check_join")]
        ]
        await update.message.reply_text(
            "🔒 پێویستە سەرەتا چۆینی چانەلەکە بکەیت 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await update.message.reply_text(
        "👋 بەخێربێیت بۆ بۆتی داونلۆدی ڤیدیۆ 🎥\n\nلینک بنێرە 👇",
        reply_markup=main_menu()
    )


# ---------------- Buttons ----------------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "home":
        await query.edit_message_text("🏠 سەرەتا", reply_markup=main_menu())

    elif query.data == "about":
        await query.edit_message_text(
            "🤖 زانیاری بۆت\n\n"
            "ئەم بۆتە ڤیدیۆ دابەزێنێت لە:\n"
            "TikTok • Instagram • Facebook • YouTube\n\n"
            "👨‍💻 لەلاین @Deva_harki دروستکراوە",
            reply_markup=back_button()
        )

    elif query.data == "owner":
        await query.edit_message_text(
            f"📨 پەیوەندی بکە 👇\nhttps://t.me/{OWNER_USERNAME}",
            reply_markup=back_button()
        )

    elif query.data == "admin":
        if query.from_user.username != OWNER_USERNAME:
            await query.edit_message_text("❌ تەنها ئەدمین", reply_markup=back_button())
            return

        users_count = len(open(USERS_FILE).read().splitlines())
        await query.edit_message_text(
            f"🛠 Admin Panel 👑\n\n👥 ژمارەی بەکارهێنەران: {users_count}",
            reply_markup=back_button()
        )

    elif query.data == "download":
        await query.edit_message_text(
            "🔗 تکایە لینک ڤیدیۆ بنێرە 🎥",
            reply_markup=back_button()
        )

    elif query.data == "check_join":
        joined = await force_join_check(update, context)
        if joined:
            await query.edit_message_text("✅ سوپاس بۆ چۆین", reply_markup=main_menu())
        else:
            await query.answer("❌ هێشتا چۆینت نەکردووە", show_alert=True)


# ---------------- Loading Animation ----------------
async def loading_animation(msg):
    steps = [
        "⏳ داونلۆد دەستی پێکرد...",
        "📥 ڤیدیۆ دادەبەزێنرێت...",
        "⚙️ ڤیدیۆ + دەنگ تێکەڵ دەکرێت...",
        "🚀 نزیکەی تەواوبوون..."
    ]
    for s in steps:
        await msg.edit_text(s)
        await asyncio.sleep(2)


# ---------------- Downloader ----------------
def download_video(url, filename="video.mp4"):
    ydl_opts = {
        'format': 'best',
        'outtmpl': filename,
        'quiet': True,
        'noplaylist': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "http" not in text:
        await update.message.reply_text("⚠️ تکایە تەنها لینک بنێرە 🎥")
        return

    msg = await update.message.reply_text("⏳ داونلۆد دەستی پێکرد...")
    asyncio.create_task(loading_animation(msg))

    try:
        file_name = "video.mp4"
        download_video(text, file_name)

        await update.message.reply_video(video=open(file_name, "rb"))
        os.remove(file_name)
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ هەڵەیەک ڕوویدا\n{e}")


# ---------------- Main ----------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()