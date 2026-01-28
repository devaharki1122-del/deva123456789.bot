import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_1 = os.getenv("CHANNEL_1")
CHANNEL_2 = os.getenv("CHANNEL_2")

users = {}

def check_limit(user_id):
    if user_id not in users:
        users[user_id] = {"count": 0}
    return users[user_id]["count"] < 5

def add_count(user_id):
    users[user_id]["count"] += 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 جۆین بوون", url=f"https://t.me/{CHANNEL_1.replace('@','')}")],
        [InlineKeyboardButton("📢 جۆین بوون", url=f"https://t.me/{CHANNEL_2.replace('@','')}")],
        [InlineKeyboardButton("▶️ دابەزاندن", callback_data="download")]
    ]
    await update.message.reply_text(
        "👋 بەخێربێیت\n\nبۆ بەکارهێنانی بۆت پێویستە جۆین بیت 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if not check_limit(user_id):
        btn = [[InlineKeyboardButton("✉️ نامە بنێرە بۆ ئەدمین", url="https://t.me/Deva_harki")]]
        await query.answer()
        await query.message.reply_text(
            "❌ سنووری ڕۆژانەت تەواو بوو\n\nبۆ 100 ڤیدیۆ نامە بنێرە 👇",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return

    add_count(user_id)
    await query.answer()
    await query.message.reply_text("✅ ڤیدیۆ دابەزرا (نموونە)")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("download", download))

    print("BOT STARTED...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())