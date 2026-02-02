import os
import requests
from io import BytesIO
from PIL import Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("8251863494:AAGB7Wwt0j82hAyB-WRY7tnjefDD05_jQEM")
CHANNEL_USERNAME = "@chanaly_boot"  # گۆڕە بۆ چەنەڵەکەت
ADMIN_ID = 8186735286  # گۆڕە بۆ ئایدی خۆت


# ========== Force Join ==========
async def force_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
        else:
            return False
    except:
        return False


# ========== Start ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await force_join(update, context):
        join_btn = [[InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")]]
        await update.message.reply_text(
            "تکایە سەرەتا بچۆ ژوورەوە بۆ چەنەڵ:",
            reply_markup=InlineKeyboardMarkup(join_btn)
        )
        return

    buttons = [
        [InlineKeyboardButton("🤖 AI", callback_data="ai")],
        [InlineKeyboardButton("🖼 وێنە جوانکرد", callback_data="photo")],
        [InlineKeyboardButton("⬇️ Download", callback_data="download")]
    ]

    await update.message.reply_text(
        "بەخێربێیت بۆ بوتەکەمان 👋",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ========== Buttons ==========
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "ai":
        await query.message.reply_text("نامەکەت بنێرە بۆ AI 🤖")

    elif query.data == "photo":
        await query.message.reply_text("وێنە بنێرە بۆ جوانکردن 🖼")

    elif query.data == "download":
        await query.message.reply_text("لینکی فایلی داونلۆد بنێرە ⬇️")


# ========== AI Chat (Simple Echo) ==========
async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"AI وەڵام:\n{text}")


# ========== Photo Enhance ==========
async def enhance_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    img_bytes = await file.download_as_bytearray()

    image = Image.open(BytesIO(img_bytes))
    image = image.convert("RGB")

    bio = BytesIO()
    bio.name = "enhanced.jpg"
    image.save(bio, "JPEG", quality=95)
    bio.seek(0)

    await update.message.reply_photo(photo=bio, caption="وێنەکەت جوان کرا ✨")


# ========== Downloader ==========
async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    try:
        r = requests.get(url)
        file = BytesIO(r.content)
        file.name = "downloaded_file"
        await update.message.reply_document(document=file)
    except:
        await update.message.reply_text("هەڵەیە لە لینکەکە ❌")


# ========== Admin Panel ==========
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text("بەخێربێیت بۆ Admin Panel ✅")


# ========== Main ==========
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))
    app.add_handler(MessageHandler(filters.PHOTO, enhance_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, downloader))

    app.add_handler(MessageHandler(filters.ALL, buttons))

    app.run_polling()


if __name__ == "__main__":
    main()