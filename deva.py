import os
import requests
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_USERNAME = "@chanaly_boot"
ADMIN_ID = 8186735286


# ---------------- Force Join ----------------
async def is_joined(user_id, bot):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


def join_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
        [InlineKeyboardButton("✅ Joined", callback_data="check_join")]
    ])


# ---------------- Keyboards ----------------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬇️ Download Video", callback_data="download")],
        [InlineKeyboardButton("📨 نامە بۆ خاوەن بوت", url="https://t.me/Deva_harki")],
        [InlineKeyboardButton("🛠 Admin Panel", callback_data="admin")]
    ])


def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 زانیاری بوت", callback_data="stats")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])


# ---------------- Start ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await is_joined(user_id, context.bot):
        await update.message.reply_text(
            "⚠️ بۆ بەکارهێنانی بوت پێویستە جوینی چانەل بکەیت",
            reply_markup=join_kb()
        )
        return

    await update.message.reply_text(
        "🤖 بەخێربێیت\n\nلینکی TikTok بنێرە بۆ داونلۆد ⬇️",
        reply_markup=main_menu()
    )


# ---------------- Buttons ----------------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    # Check Join
    if query.data == "check_join":
        if await is_joined(user_id, context.bot):
            await query.message.edit_text("✅ سوپاس بۆ جوین کردن", reply_markup=main_menu())
        else:
            await query.answer("❌ هێشتا جوین نەبوویت", show_alert=True)

    # Download
    elif query.data == "download":
        if not await is_joined(user_id, context.bot):
            await query.message.reply_text("سەرەتا جوین بکە", reply_markup=join_kb())
            return

        context.user_data["mode"] = "download"
        await query.message.reply_text("🔗 لینک بنێرە")

    # Admin
    elif query.data == "admin":
        if user_id != ADMIN_ID:
            await query.answer("تۆ ئەدمین نیت ❌", show_alert=True)
            return
        await query.message.edit_text("🛠 Admin Panel", reply_markup=admin_menu())

    # Stats
    elif query.data == "stats":
        await query.message.edit_text(
            "📊 بوت بە باشی کار دەکات\nForce Join: ON\nDownloader: ON",
            reply_markup=admin_menu()
        )

    # Back
    elif query.data == "back":
        await query.message.edit_text("🔙 گەڕانەوە", reply_markup=main_menu())


# ---------------- Downloader ----------------
def download_tiktok(url):
    api = f"https://tikwm.com/api/?url={url}"
    r = requests.get(api).json()

    if "data" in r and "play" in r["data"]:
        video_url = r["data"]["play"]
        title = r["data"].get("title", "TikTok Video")

        video = requests.get(video_url).content
        bio = BytesIO(video)
        bio.name = "video.mp4"
        return bio, title

    return None, None


# ---------------- Messages ----------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if not await is_joined(user_id, context.bot):
        await update.message.reply_text("⚠️ جوینی چانەل بکە", reply_markup=join_kb())
        return

    if context.user_data.get("mode") == "download":
        if "http" in text:
            msg = await update.message.reply_text("⬇️ داونلۆد دەستی پێکرد...")

            try:
                video, title = download_tiktok(text)
                if video:
                    await update.message.reply_video(video, caption=title)
                    await msg.delete()
                else:
                    await msg.edit_text("❌ نەتوانرا داونلۆد بکرێت")
            except:
                await msg.edit_text("❌ هەڵە ڕوویدا")


# ---------------- Main ----------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()