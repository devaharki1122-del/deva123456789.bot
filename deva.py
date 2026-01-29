# -*- coding: utf-8 -*-
# =========================================
# 🇭🇺⬇️ بوتی داولۆدی کوردی (یەک فایل)
# دروستکراوە لەلایەن @Deva_harki
# =========================================

import os, time, asyncio, random, sys
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# ================= ⚙️ ڕێکخستن =================
BOT_TOKEN = "8251863494:AAEpF0YDGTxV3JVn7VCJGUb8_1n_HzUUqhM"
OWNER_ID = 8186735286
FORCE_JOIN_CHANNELS = ["@team_988", "@chanaly_boot"]

USERS = set()
DOWNLOADS = 0
START_TIME = time.time()

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
        [InlineKeyboardButton("🔄🇭🇺 نوی‌کردنەوەی بوت", callback_data="admin_restart")],
        [InlineKeyboardButton("🔙🇭🇺 گەڕانەوە", callback_data="back")]
    ])

# ================= 🔒 FORCE JOIN =================
async def check_force_join(update, context):
    uid = update.effective_user.id
    for ch in FORCE_JOIN_CHANNELS:
        try:
            m = await context.bot.get_chat_member(ch, uid)
            if m.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# ================= /start =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        btns = [[InlineKeyboardButton("🔔 جوین", url=f"https://t.me/{c.replace('@','')}")] for c in FORCE_JOIN_CHANNELS]
        await update.message.reply_text(
            "🔒 تکایە سەرەتا جوینی جەناڵەکان بکە",
            reply_markup=InlineKeyboardMarkup(btns)
        )
        return

    USERS.add(update.effective_user.id)
    await update.message.reply_text(
        "🇭🇺❤️ سڵاو دڵی جوان\n"
        "من بوتی داولۆدی زیرەکم 🤖\n"
        "دووگمە هەڵبژێرە 👇",
        reply_markup=main_menu()
    )

# ================= 🎬 داولۆد =================
EMOJIS = ["🙂","😋","😎","😭","💓","🔥","⚡","😍","🤖","🚀","💚"]

async def animate(msg):
    for _ in range(3):
        await msg.edit_text(f"⬇️🇭🇺 داولۆد دەستپێکرا {random.choice(EMOJIS)}")
        await asyncio.sleep(1)

async def download_video(update, url):
    global DOWNLOADS
    msg = await update.message.reply_text("⬇️🇭🇺 داولۆد دەستپێکرا 🙂")
    await animate(msg)

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": "/tmp/%(id)s.%(ext)s",
        "merge_output_format": "mp4",
        "concurrent_fragment_downloads": 8,
        "retries": 3,
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "age_limit": 99,
        "http_chunk_size": 10485760,  # ⚡ خێرای زیاتر
    }

    for _ in range(3):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if not info:
                    continue
                file = ydl.prepare_filename(info)

            await update.message.reply_video(
                open(file, "rb"),
                supports_streaming=True
            )

            DOWNLOADS += 1
            os.remove(file)
            await msg.delete()
            return
        except:
            await asyncio.sleep(1)

    await msg.edit_text(
        "⚠️ ببورە دڵی جوان 💚\n\n"
        "ئەم ڤیدیۆیە پارێزراوە یان تایبەتیە 🚫\n\n"
        "🔓 تکایە ڤیدیۆی ئاسایی بنێرە\n"
        "من هەموو ئەوانەی تر دابەزینم 😌✨"
    )

# ================= 💬 نامە =================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        await update.message.reply_text("🔒 تکایە جوین بکە")
        return

    if update.message.text.startswith("http"):
        await download_video(update, update.message.text)
    else:
        await update.message.reply_text("🔗 تکایە لینک بنێرە")

# ================= 🔘 Callback =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "download":
        await q.edit_message_text("⬇️ لینک بنێرە")

    elif q.data == "info":
        await q.edit_message_text(
            "🤖✨ زانیاری بوت\n\n"
            "سڵاو دڵی جوان 💚\n"
            "من بوتێکی زیرەک و خێرامم 🤖⚡\n"
            "دروستکراوم بۆ ئاسانکردنی ژیانت 😌🚀\n\n"
            "⬇️ دەتوانم:\n"
            "• لە هەموو شوێنێک ڤیدیۆ دابەزینم 🌍\n"
            "• تا 2GB داولۆد بکەم 📦\n"
            "• وێنە دابەزینم 🖼️\n\n"
            "❌ ناتوانم:\n"
            "• ڤیدیۆی تایبە 🔒\n"
            "• ستۆری Snapchat 👻\n\n"
            "ئەمە بۆ پاراستنی یاسا و ئاسایشە ⚖️\n"
            "👑 خاوەن بوت: @Deva_harki",
            reply_markup=main_menu()
        )

    elif q.data == "admin":
        if q.from_user.id != OWNER_ID:
            await q.edit_message_text("❌ تۆ ئەدمین نیت")
            return
        await q.edit_message_text("🛠 ئەدمین پانیل", reply_markup=admin_menu())

    elif q.data == "admin_users":
        await q.edit_message_text(f"👥 {len(USERS)}", reply_markup=admin_menu())

    elif q.data == "admin_downloads":
        await q.edit_message_text(f"⬇️ {DOWNLOADS}", reply_markup=admin_menu())

    elif q.data == "admin_uptime":
        uptime = int(time.time() - START_TIME)
        await q.edit_message_text(f"⏱ {uptime} چرکە", reply_markup=admin_menu())

    elif q.data == "admin_restart":
        if q.from_user.id != OWNER_ID:
            await q.edit_message_text("❌ تۆ ئەدمین نیت")
            return
        await q.edit_message_text("🔄 بوت نوێ دەکرێتەوە ...")
        os.execl(sys.executable, sys.executable, *sys.argv)

    elif q.data == "back":
        await q.edit_message_text("🏠 منو", reply_markup=main_menu())

# ================= 🚀 MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()