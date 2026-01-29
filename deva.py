# -*- coding: utf-8 -*-
# =========================================
# 🇭🇺⬇️ بوتی داولۆدی کوردی (یەک فایل)
# دروستکراوە لەلایەن @Deva_harki
# =========================================

import os, time, asyncio, random
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# ================= ⚙️ ڕێکخستن =================
BOT_TOKEN = "8251863494:AAHYWiOWvgq2q2_x4HlZqGf5YRhaX3XpgcU"
OWNER_ID = 8186735286

FORCE_CHANNEL_1 = "@chanaly_boot"
FORCE_CHANNEL_2 = "@team_988"

USERS = set()
DOWNLOADS = 0
START_TIME = time.time()

# ================= 🔒 FORCE JOIN =================
async def force_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot = context.bot
    try:
        m1 = await bot.get_chat_member(FORCE_CHANNEL_1, user_id)
        m2 = await bot.get_chat_member(FORCE_CHANNEL_2, user_id)
        if m1.status in ["left","kicked"] or m2.status in ["left","kicked"]:
            raise Exception()
    except:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 کەناڵی یەکەم 🇭🇺", url=f"https://t.me/{FORCE_CHANNEL_1.replace('@','')}")],
            [InlineKeyboardButton("📢 کەناڵی دووەم 🇭🇺", url=f"https://t.me/{FORCE_CHANNEL_2.replace('@','')}")],
            [InlineKeyboardButton("✅ دووبارە پشکنین", callback_data="recheck")]
        ])
        if update.message:
            await update.message.reply_text("🔒 تکایە سەرەتا جۆین بکە بۆ هەردوو کەناڵ 👇", reply_markup=keyboard)
        else:
            await update.callback_query.edit_message_text("🔒 تکایە سەرەتا جۆین بکە بۆ هەردوو کەناڵ 👇", reply_markup=keyboard)
        return False
    return True

# ================= 🔘 منو =================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬇️🇭🇺 داولۆد", callback_data="download")],
        [InlineKeyboardButton("ℹ️🇭🇺 زانیاری بوت", callback_data="info")],
        [InlineKeyboardButton("🛠🇭🇺 ئەدمین پانیل", callback_data="admin")],
        [InlineKeyboardButton("📩🇭🇺 نامە بۆ خاوەن بوت", url="https://t.me/Deva_harki")]
    ])

# ================= 🛠 ADMIN PANEL =================
def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥🇭🇺 ژمارەی بەکارهێنەر", callback_data="admin_users")],
        [InlineKeyboardButton("⬇️🇭🇺 ژمارەی داولۆد", callback_data="admin_downloads")],
        [InlineKeyboardButton("⏱🇭🇺 ماوەی کارکردن", callback_data="admin_uptime")],
        [InlineKeyboardButton("🔙🇭🇺 گەڕانەوە", callback_data="back")]
    ])

# ================= /start =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await force_join(update, context):
        return
    USERS.add(update.effective_user.id)
    await update.message.reply_text(
        "🇭🇺❤️ سڵاو دڵی جوان\n"
        "من بوتی داولۆدی زیرەکم 🤖\n"
        "دووگمە هەڵبژێرە 👇",
        reply_markup=main_menu()
    )

# ================= 🎬 داولۆد =================
EMOJIS = ["🙂","😋","😎","😭","💓","🔥","⚡","😍","🤖","🚀","💚","✨","🌍"]

async def animate(msg):
    for _ in range(7):
        await msg.edit_text(f"⬇️🇭🇺 داولۆد دەستپێکرا {random.choice(EMOJIS)}")
        await asyncio.sleep(1)

async def download_video(update, url):
    global DOWNLOADS
    msg = await update.message.reply_text("⬇️🇭🇺 داولۆد دەستپێکرا 🙂")
    await animate(msg)

    try:
        ydl_opts = {"format": "best", "outtmpl": "/tmp/%(id)s.%(ext)s", "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)

        await update.message.reply_video(open(file, "rb"))
        DOWNLOADS += 1
        os.remove(file)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌🇭🇺 هەڵە: {e}")

# ================= 💬 نامە =================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await force_join(update, context):
        return
    if update.message.text.startswith("http"):
        await download_video(update, update.message.text)
    else:
        await update.message.reply_text("🔗🇭🇺 تکایە لینک بنێرە")

# ================= 🔘 Callback =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "recheck":
        await start(update, context)

    elif q.data == "download":
        await q.edit_message_text("⬇️🇭🇺 لینک بنێرە بۆ داولۆد")

    elif q.data == "info":
        await q.edit_message_text(
            "🤖✨ زانیاری بوت\n\n"
            "ڤیدیۆ دابەزینم لە چەند شوێنێکەوە 🌍\n"
            "دەتوانم لە هەموو شوێنێک ڤیدیۆ دابەزینم 📥✨\n\n"
            "❌ ناتوانم ئەمانە بکەم:\n"
            "– ڤیدیۆی تایبە 🔒\n"
            "– ستۆری Snapchat 👻\n"
            "– ستۆری تایبەی هەر پلاتفۆرمێک\n\n"
            "ئەمە ناکەم چونکە خاوەنی بوت\n"
            "@Deva_harki ئاگەدار کراوەتەوە لەلایەن حوکمەتەوە 🚨\n"
            "تاوەکو توشی کاری نایاسایی نەبێت ⚖️💚\n\n"
            "👉 تەنها ئەمانە ناتوانم بکەم 😌❤️\n\n"
            "🖼️ دەتوانم وێنەش دابەزینم لە هەموو شوێنێک 🌍\n"
            "❤️ لایک | 👁 ڤیوو | 💬 کۆمێنت | 🔁 شێر\n"
            "🎬 کوالێتی بەرز | ⚡ خێرا | 🤖 زیرەک\n\n"
            "هەر شتێکت پێویست بێت، من لێرەم 🤖💚✨",
            reply_markup=main_menu()
        )

    elif q.data == "admin":
        if q.from_user.id != OWNER_ID:
            await q.edit_message_text("❌🇭🇺 تۆ ئەدمین نیت")
            return
        await q.edit_message_text("🛠🇭🇺 ئەدمین پانیل", reply_markup=admin_menu())

    elif q.data == "admin_users":
        await q.edit_message_text(f"👥🇭🇺 ژمارەی بەکارهێنەر: {len(USERS)}", reply_markup=admin_menu())

    elif q.data == "admin_downloads":
        await q.edit_message_text(f"⬇️🇭🇺 ژمارەی داولۆد: {DOWNLOADS}", reply_markup=admin_menu())

    elif q.data == "admin_uptime":
        uptime = int(time.time() - START_TIME)
        await q.edit_message_text(f"⏱🇭🇺 ماوەی کارکردن: {uptime} چرکە", reply_markup=admin_menu())

    elif q.data == "back":
        await q.edit_message_text("🇭🇺 گەڕایەوە بۆ منو", reply_markup=main_menu())

# ================= 🚀 MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🇭🇺 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()