import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "chanaly_boot"   # without @
OWNER_USERNAME = "Deva_harki"       # without @
USERS_FILE = "users.txt"


def save_user(user_id):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w").close()
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")


async def force_join_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(
            f"@{CHANNEL_USERNAME}", update.effective_user.id
        )
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 داونلۆد", callback_data="download")],
        [InlineKeyboardButton("ℹ️ زانیاری", callback_data="about")],
        [InlineKeyboardButton("📨 خاوەن بۆت", callback_data="owner")],
    ])


def back_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 گەڕانەوە", callback_data="home")]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)

    if not await force_join_check(update, context):
        await update.message.reply_text(
            "🔒 تکایە چۆینی چانەل بکە",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join", url=f"https://t.me/{CHANNEL_USERNAME}")],
                [InlineKeyboardButton("✅ پشکنینەوە", callback_data="check_join")]
            ])
        )
        return

    await update.message.reply_text(
        "🔗 لینک بنێرە بۆ داونلۆد",
        reply_markup=main_menu()
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "home":
        await q.edit_message_text("🏠", reply_markup=main_menu())

    elif q.data == "about":
        await q.edit_message_text(
            "TikTok • Instagram • Facebook • YouTube • Twitter/X",
            reply_markup=back_btn()
        )

    elif q.data == "owner":
        await q.edit_message_text(
            f"https://t.me/{OWNER_USERNAME}",
            reply_markup=back_btn()
        )

    elif q.data == "download":
        await q.edit_message_text(
            "🔗 لینک ڤیدیۆ بنێرە",
            reply_markup=back_btn()
        )

    elif q.data == "check_join":
        if await force_join_check(update, context):
            await q.edit_message_text("✅", reply_markup=main_menu())
        else:
            await q.answer("❌", show_alert=True)


def download_video_api(url, filename="video.mp4"):
    api = "https://api.cobalt.tools/api/json"

    payload = {
        "url": url,
        "vQuality": "max",
        "vCodec": "h264",
        "isAudioOnly": False
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.post(api, json=payload, headers=headers, timeout=60)
    data = r.json()

    if "url" not in data:
        raise Exception("Download failed")

    video = requests.get(data["url"], stream=True)
    with open(filename, "wb") as f:
        for chunk in video.iter_content(1024):
            if chunk:
                f.write(chunk)


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "http" not in url:
        return

    await update.message.reply_text("⏳")

    try:
        file = "video.mp4"
        download_video_api(url, file)

        await update.message.reply_video(
            video=open(file, "rb"),
            caption="✅"
        )

        os.remove(file)
    except:
        await update.message.reply_text("❌")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    app.run_polling()


if __name__ == "__main__":
    main()