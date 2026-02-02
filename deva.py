import os
import re
import requests
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
USERS_FILE = "users.txt"

# ========= Users =========
def save_user(user_id):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w").close()
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

def get_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return f.read().splitlines()

# ========= Force Join =========
async def force_join(user_id, bot):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ========= Menu =========
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 AI", callback_data="ai")],
        [InlineKeyboardButton("🖼 وێنە جوانکرد", callback_data="photo")],
        [InlineKeyboardButton("⬇️ Download", callback_data="download")],
        [InlineKeyboardButton("👨‍💻 Admin Panel", callback_data="admin_panel")],
        [InlineKeyboardButton("✉️ نامە بۆ خاوەن بوت", url="https://t.me/Deva_harki")]
    ])

# ========= Start =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)

    if not await force_join(user_id, context.bot):
        btn = [[InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")]]
        await update.message.reply_text("تکایە جۆینی چەنەڵ بکە:", reply_markup=InlineKeyboardMarkup(btn))
        return

    await update.message.reply_text("👋 بەخێربێیت", reply_markup=menu())

# ========= Buttons =========
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "ai":
        context.user_data["mode"] = "ai"
        await q.message.reply_text("نامەکەت بنێرە 🤖")

    elif q.data == "photo":
        context.user_data["mode"] = "photo"
        await q.message.reply_text("وێنە بنێرە 🖼")

    elif q.data == "download":
        context.user_data["mode"] = "download"
        await q.message.reply_text("لینک بنێرە ⬇️")

    elif q.data == "admin_panel":
        if q.from_user.id != ADMIN_ID:
            return
        btn = [
            [InlineKeyboardButton("📊 ژمارەی بەکارهێنەران", callback_data="users")],
            [InlineKeyboardButton("📢 Broadcast", callback_data="bc")]
        ]
        await q.message.reply_text(
            f"👨‍💻 Admin Panel\n👥 {len(get_users())} Users",
            reply_markup=InlineKeyboardMarkup(btn)
        )

    elif q.data == "users":
        await q.message.reply_text(f"👥 Users: {len(get_users())}")

    elif q.data == "bc":
        context.user_data["broadcast"] = True
        await q.message.reply_text("نامەکە بنێرە بۆ بڵاوکردنەوە 📢")

# ========= Text =========
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Broadcast
    if context.user_data.get("broadcast") and update.effective_user.id == ADMIN_ID:
        for u in get_users():
            try:
                await context.bot.send_message(u, text)
            except:
                pass
        context.user_data["broadcast"] = False
        await update.message.reply_text("بڵاوکرایەوە ✅")
        return

    # AI
    if context.user_data.get("mode") == "ai":
        await update.message.reply_text(f"AI:\n{text}")
        return

    # Downloader
    if re.match(r'https?://', text):
        msg = await update.message.reply_text("⬇️ داونلۆد دەستی پێکرد...")
        try:
            r = requests.get(text, timeout=20)
            file = BytesIO(r.content)
            file.name = "file"
            await update.message.reply_document(file)
            await msg.delete()
        except:
            await msg.edit_text("❌ هەڵە لە لینک")

# ========= Photo =========
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("mode") != "photo":
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()
    img = Image.open(BytesIO(await file.download_as_bytearray())).convert("RGB")

    bio = BytesIO()
    bio.name = "enhanced.jpg"
    img.save(bio, "JPEG", quality=95)
    bio.seek(0)

    await update.message.reply_photo(bio, caption="✨ وێنەکەت جوان کرا")

# ========= Main =========
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    app.run_polling()

if __name__ == "__main__":
    main()