import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_USERNAME = "chanaly_boot"  # بەبێ @
OWNER_USERNAME = "Deva_harki"

USERS_FILE = "users.txt"


# -------- Users Save --------
def save_user(user_id):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            f.write("")

    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()

    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")


# -------- Force Join --------
async def force_join_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
    return member.status in ["member", "administrator", "creator"]


# -------- Keyboards --------
def main_menu():
    keyboard = [
        [InlineKeyboardButton("📥 داونلۆدی ڤیدیۆ", callback_data="download")],
        [InlineKeyboardButton("ℹ️ زانیاری بۆت", callback_data="about")],
        [InlineKeyboardButton("📨 نامە بۆ خاوەن بۆت", callback_data="owner")],
        [InlineKeyboardButton("🛠 Admin Panel", callback_data="admin")]
    ]
    return InlineKeyboardMarkup(keyboard)


def back_button():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 گەڕانەوە بۆ سەرەتا", callback_data="home")]]
    )


# -------- Start --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id)

    joined = await force_join_check(update, context)

    if not joined:
        keyboard = [
            [InlineKeyboardButton("📢 چۆین بکە", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("✅ پشکنینەوە", callback_data="check_join")]
        ]
        await update.message.reply_text(
            "🔒 بۆ بەکارهێنانی بۆت پێویستە چۆینی چانەلەکە بکەیت 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await update.message.reply_text(
        "👋 بەخێربێیت بۆ بۆتی داونلۆدی ڤیدیۆ 🎥\n\nلینک بنێرە یان دووگمەکان بەکاربهێنە 👇",
        reply_markup=main_menu()
    )


# -------- Buttons --------
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
            "⚡ خێرا و بە کوالیتی بەرز\n\n"
            "👨‍💻 لەلاین @Deva_harki دروستکراوە",
            reply_markup=back_button()
        )

    elif query.data == "owner":
        await query.edit_message_text(
            f"📨 پەیوەندی بە خاوەن بۆت 👇\n\nhttps://t.me/{OWNER_USERNAME}",
            reply_markup=back_button()
        )

    elif query.data == "admin":
        if query.from_user.username != OWNER_USERNAME:
            await query.edit_message_text("❌ تەنها ئەدمین", reply_markup=back_button())
            return

        with open(USERS_FILE, "r") as f:
            count = len(f.readlines())

        await query.edit_message_text(
            f"🛠 Admin Panel\n\n👥 ژمارەی بەکارهێنەران: {count}",
            reply_markup=back_button()
        )

    elif query.data == "download":
        await query.edit_message_text(
            "🔗 تکایە لینک ڤیدیۆ بنێرە بۆ داونلۆد 🎥",
            reply_markup=back_button()
        )

    elif query.data == "check_join":
        joined = await force_join_check(update, context)
        if joined:
            await query.edit_message_text("✅ سوپاس بۆ چۆین", reply_markup=main_menu())
        else:
            await query.answer("❌ هێشتا چۆینت نەکردووە", show_alert=True)


# -------- Download --------
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
        return

    await update.message.reply_text("⏳ داونلۆد دەستی پێکرد...")

    try:
        file_name = "video.mp4"
        download_video(text, file_name)

        await update.message.reply_video(video=open(file_name, "rb"))
        os.remove(file_name)

    except Exception as e:
        await update.message.reply_text(f"❌ هەڵەیەک ڕوویدا\n{e}")


# -------- Main --------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()