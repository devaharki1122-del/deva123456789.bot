import os
import re
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8251863494:AAGB7Wwt0j82hAyB-WRY7tnjefDD05_jQEM"
ADMIN_ID = 8186735286

CHANNEL_1 = "@chanaly_boot"
CHANNEL_2 = "@team_988"

WEBHOOK_URL = "https://YOUR-RAILWAY-URL.up.railway.app"


# ================= KEYBOARD =================
keyboard = [
    ["🤖 AI زیرەک", "🖼 وێنە جوانکرد"],
    ["⬇️ داونلۆدی ڤیدیۆ"],
]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ================= FORCE JOIN =================
async def force_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member1 = await context.bot.get_chat_member(CHANNEL_1, user_id)
        member2 = await context.bot.get_chat_member(CHANNEL_2, user_id)

        if member1.status in ["left", "kicked"] or member2.status in ["left", "kicked"]:
            await update.message.reply_text(
                f"""🚫 بۆ بەردەوامبوون پێویستە جۆینی ئەم جەنالانە بکەیت:

{CHANNEL_1}
{CHANNEL_2}

دوای جۆین /start بنووسە."""
            )
            return False
        return True
    except:
        return True


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await force_join(update, context):
        return

    text = """
👋 بەخێربێیت بۆ AI Bot

🤖 AI زیرەک  
🖼 جوانکردنی وێنەکانت (سافکردنی دەموچا)  
⬇️ داونلۆدی ڤیدیۆ لە هەموو شۆینەکان  

تەنها دووگمەی خوارەوە هەڵبژێرە 👇
"""
    await update.message.reply_text(text, reply_markup=markup)


# ================= BUTTONS =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🤖 AI زیرەک":
        await update.message.reply_text("پرسیارەکەت بنووسە 👇")
        context.user_data["mode"] = "ai"
        return

    if text == "🖼 وێنە جوانکرد":
        await update.message.reply_text("وێنەکەت بنێرە 👇")
        context.user_data["mode"] = "image"
        return

    if text == "⬇️ داونلۆدی ڤیدیۆ":
        await update.message.reply_text("لینکی ڤیدیۆکە بنێرە 👇")
        context.user_data["mode"] = "download"
        return


# ================= AI / DOWNLOAD =================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")

    if mode == "ai":
        await update.message.reply_text("🤖 وەڵامی AI لێرە دەردەکەوێت.")
        return

    if mode == "download":
        url = update.message.text
        if re.match(r"https?://", url):
            await update.message.reply_text(
                "⬇️ داونلۆد دەستی پێکرد...\n⏳ تکایە ئارام بگرە..."
            )
        else:
            await update.message.reply_text("تکایە لینکێکی دروست بنێرە.")
        return


# ================= IMAGE =================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("mode") == "image":
        await update.message.reply_text("🖼 وێنەکە جوان دەکرێت...")
        return


# ================= MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    PORT = int(os.environ.get("PORT", 8080))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
    )


if __name__ == "__main__":
    main()