import os
from io import BytesIO
from PIL import Image
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
CHANNEL_USERNAME = "@chanaly_boot"
ADMIN_ID = 8186735286


# ========== Force Join ==========
async def is_joined(user_id, bot):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# ========== Start ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not await is_joined(user.id, context.bot):
        btn = [[InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")]]
        await update.message.reply_text(
            "تکایە سەرەتا جۆینی چەنەڵ بکە:",
            reply_markup=InlineKeyboardMarkup(btn),
        )
        return

    buttons = [
        [InlineKeyboardButton("🤖 AI", callback_data="ai")],
        [InlineKeyboardButton("🖼 وێنە جوانکرد", callback_data="photo")],
        [InlineKeyboardButton("⬇️ Download", callback_data="download")],
    ]

    await update.message.reply_text(
        "بەخێربێیت 👋\nدووگمەی خوارەوە هەڵبژێرە:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ========== Button Click ==========
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "ai":
        context.user_data["mode"] = "ai"
        await query.message.reply_text("پرسیارەکەت بنووسە 🤖")

    elif query.data == "photo":
        context.user_data["mode"] = "photo"
        await query.message.reply_text("وێنەکەت بنێرە 🖼")

    elif query.data == "download":
        context.user_data["mode"] = "download"
        await query.message.reply_text("لینک بنێرە ⬇️")


# ========== Text ==========
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")

    if mode == "ai":
        await update.message.reply_text("AI وەڵام: " + update.message.text)

    elif mode == "download":
        await update.message.reply_text("داونلۆد دەستی پێکرد ⏳")


# ========== Photo ==========
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("mode") != "photo":
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()
    img_bytes = await file.download_as_bytearray()

    image = Image.open(BytesIO(img_bytes)).convert("RGB")

    bio = BytesIO()
    bio.name = "enhanced.jpg"
    image.save(bio, "JPEG", quality=95)
    bio.seek(0)

    await update.message.reply_photo(bio, caption="وێنەکەت جوان کرا ✨")


# ========== Admin ==========
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("Admin Panel ✅")


# ========== Main ==========
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(button_click))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    app.run_polling()


if __name__ == "__main__":
    main()