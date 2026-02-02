import os
import requests
from io import BytesIO
from PIL import Image
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@chanaly_boot"
ADMIN_ID = 8186735286


# ========== Force Join ==========
async def force_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# ========== Main Menu ==========
def main_menu():
    buttons = [
        [InlineKeyboardButton("🤖 AI", callback_data="ai")],
        [InlineKeyboardButton("🖼 وێنە جوانکرد", callback_data="photo")],
        [InlineKeyboardButton("⬇️ TikTok Download", callback_data="download")],
        [InlineKeyboardButton("ℹ️ زانیاری بۆت", callback_data="info")],
    ]
    return InlineKeyboardMarkup(buttons)


# ========== Start ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await force_join(update, context):
        join_btn = [[InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")]]
        await update.message.reply_text(
            "تکایە سەرەتا بچۆ ژوورەوە بۆ چەنەڵ:",
            reply_markup=InlineKeyboardMarkup(join_btn),
        )
        return

    await update.message.reply_text(
        "👋 بەخێربێیت بۆ بوتەکەمان",
        reply_markup=main_menu(),
    )


# ========== Buttons ==========
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "ai":
        await query.message.reply_text("✍️ نامەکەت بنێرە")

    elif query.data == "photo":
        await query.message.reply_text("🖼 وێنە بنێرە")

    elif query.data == "download":
        await query.message.reply_text("🔗 لینکی TikTok بنێرە")

    elif query.data == "info":
        await query.message.reply_text(
            "ℹ️ زانیاری بۆت\n\n"
            "🤖 AI چات\n"
            "🖼 وێنە جوانکردن\n"
            "⬇️ TikTok داونلۆد"
        )


# ========== AI Chat ==========
async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🤖 AI وەڵام:\n{update.message.text}")


# ========== Photo Enhance ==========
async def enhance_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    img_bytes = await file.download_as_bytearray()

    image = Image.open(BytesIO(img_bytes)).convert("RGB")

    bio = BytesIO()
    bio.name = "enhanced.jpg"
    image.save(bio, "JPEG", quality=95)
    bio.seek(0)

    await update.message.reply_photo(photo=bio, caption="✨ وێنەکەت جوان کرا")


# ========== TikTok Downloader ==========
async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "tiktok.com" in url:
        try:
            api = "https://tikwm.com/api/"
            res = requests.post(api, data={"url": url})
            data = res.json()

            video_url = data["data"]["play"]
            video = requests.get(video_url).content

            bio = BytesIO(video)
            bio.name = "tiktok.mp4"

            await update.message.reply_video(video=bio, caption="✅ TikTok داونلۆد کرا")
        except:
            await update.message.reply_text("❌ هەڵە لە داونلۆد")
    else:
        await update.message.reply_text("❌ تەنها لینکی TikTok")


# ========== Admin Panel ==========
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    buttons = [
        [InlineKeyboardButton("📊 ژمارەی بەکارهێنەر", callback_data="users")],
    ]

    await update.message.reply_text(
        "⚙️ Admin Panel",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ========== Handlers ==========
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(buttons))

    app.add_handler(MessageHandler(filters.PHOTO, enhance_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, downloader))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))

    app.run_polling()


if __name__ == "__main__":
    main()