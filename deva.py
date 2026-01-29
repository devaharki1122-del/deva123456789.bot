# -*- coding: utf-8 -*-
# =========================================
# 🤖⬇️ بوتی داولۆدی کوردی (یەک فایل)
# دروستکراوە لەلایەن @Deva_harki
# Railway Ready | python-telegram-bot v20
# =========================================

import os
import asyncio
import random
import time
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# ================= ⚙️ ڕێکخستن =================
BOT_TOKEN = "8251863494:AAGfxsXmvNbGAJXvz0d4_mOceMCVDvFqpTs"
OWNER_ID = 8186735286

CHANNELS = [
    {"title": "🇭🇺 چەناڵی یەکەم", "link": "https://t.me/chanaly_boot", "id": -1001111111111},
    {"title": "🇭🇺 چەناڵی دووەم", "link": "https://t.me/team_988", "id": -1002222222222},
]

USERS = set()
DOWNLOADS = 0
START_TIME = time.time()

# ================= 🔒 Force Join =================
async def check_join(update, context):
    uid = update.effective_user.id
    if uid == OWNER_ID:
        return True
    for ch in CHANNELS:
        try:
            m = await context.bot.get_chat_member(ch["id"], uid)
            if m.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

async def join_msg(update):
    kb = [[InlineKeyboardButton(c["title"], url=c["link"])] for c in CHANNELS]
    kb.append([InlineKeyboardButton("✅ دووبارە پشکنین", callback_data="recheck")])
    await update.message.reply_text(
        "🔒 تکایە سەرەتا جۆین بکە بۆ بەکارهێنانی بوت 👇",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= 🔘 منو =================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬇️ داولۆد", callback_data="download")],
        [InlineKeyboardButton("ℹ️ زانیاری بوت", callback_data="info")],
        [InlineKeyboardButton("📩 نامە ناردن بۆ خاوەن بوت", url="https://t.me/Deva_harki")]
    ])

# ================= /start =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context):
        await join_msg(update)
        return

    USERS.add(update.effective_user.id)
    await update.message.reply_text(
        "🤖❤️ سڵاو دڵی جوان\n\n"
        "من بوتی داولۆدم 😌\n"
        "ڤیدیۆ و وێنە دابەزینم لە هەموو شوێنێک 🌍\n\n"
        "دووگمە هەڵبژێرە 👇",
        reply_markup=main_menu()
    )

# ================= 🎬 داولۆد =================
EMOJIS = ["🙂","😋","😎","😭","💓","🔥","⚡","😍","🤖","🚀","💚"]

async def animate(msg):
    for _ in range(7):
        await msg.edit_text(f"⬇️ داولۆد دەستپێکرا {random.choice(EMOJIS)}")
        await asyncio.sleep(1)

async def download_video(update, url):
    global DOWNLOADS
    msg = await update.message.reply_text("⬇️ داولۆد دەستپێکرا 🙂")
    await animate(msg)

    try:
        ydl_opts = {
            "format": "best",
            "outtmpl": "/tmp/%(id)s.%(ext)s",
            "quiet": True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)

        size = os.path.getsize(file)
        caption = (
            f"🎬 {info.get('title','')}\n"
            f"❤️ لایک: {info.get('like_count',0)}\n"
            f"👁 ڤیوو: {info.get('view_count',0)}\n"
            f"💬 کۆمێنت: {info.get('comment_count',0)}\n"
            f"🔁 شێر: {info.get('repost_count',0)}\n"
            f"📦 {size//1024//1024} MB"
        )

        if size < 2 * 1024 * 1024 * 1024:
            await update.message.reply_video(open(file, "rb"), caption=caption)
            DOWNLOADS += 1
        else:
            await update.message.reply_text("❌ ڤیدیۆ زۆر گەورەیە")

        os.remove(file)
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ هەڵە: {e}")

# ================= 💬 نامە =================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context):
        await join_msg(update)
        return

    text = update.message.text
    if text.startswith("http"):
        await download_video(update, text)
    else:
        await update.message.reply_text("🔗 تکایە لینک بنێرە")

# ================= 🔘 Callback =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "recheck":
        if await check_join(update, context):
            await q.edit_message_text("✅ جۆینت کرد، ئێستا لینک بنێرە 👇", reply_markup=main_menu())
        else:
            await join_msg(update)

    elif q.data == "download":
        await q.edit_message_text("⬇️ لینک بنێرە بۆ داولۆد 👇")

    elif q.data == "info":
        await q.edit_message_text(
            "🤖✨ زانیاری بوت\n\n"
            "سڵاو دڵی جوان 💚\n"
            "من بوتێکی زیرەک و خێرام، دروستکراوم بۆ ئاسانکردنی ژیانت 😌🚀\n\n"
            "⬇️ چی دەتوانم بکەم؟\n"
            "• ڤیدیۆ دابەزینم لە چەند شوێنێکەوە 🌍\n"
            "(YouTube, TikTok, Instagram, Facebook, Twitter, Reddit …)\n"
            "• دەتوانم لە هەموو شوێنێک ڤیدیۆ دابەزینم 📥✨\n\n"
            "بەڵام ❌ ناتوانم ئەمانە بکەم:\n"
            "– ڤیدیۆی تایبە 🔒\n"
            "– ستۆری Snapchat 👻\n"
            "– ستۆری تایبەی هەر پلاتفۆرمێک\n\n"
            "ئەمە بۆ پاراستنی یاسا و ئاسایشە ⚖️💚\n"
            "چونکە خاوەنی بوت @Deva_harki\n"
            "ئاگەدار کراوەتەوە لەلایەن حوکمەتەوە 🚨\n"
            "تاوەکو توشی هیچ کاری نایاسایی نەبێت 🙏✨\n\n"
            "👉 تەنها ئەمانە ناتوانم بکەم، هەموو شتی تر بە دڵی خۆش دەکەم 😌❤️\n\n"
            "• دەتوانم وێنەش دابەزینم لە هەموو شوێنێک 🖼️🌍\n"
            "• لایک ❤️ ڤیوو 👁 کۆمێنت 💬 شێر 🔁 پیشان دەدەم\n"
            "• ڤیدیۆ بە کوالێتی بەرز دەنێرم 🎬✨\n"
            "• خێرا، پاک و بێ کێشە ⚡\n"
            "• هەموو شت بە دووگمە و بە ئاسانی 👇\n\n"
            "🧠 من وەک AI زیرەکم\n"
            "قسە دەکەم، تێدەگەم، و هەوڵ دەدەم دڵت خۆش بکەم ❤️🙂\n"
            "هەر شتێکت پێویست بێت، من لێرەم 🤖💚\n\n"
            "⚙️ ڕێنمایی تەواو بۆ بەکارهێنان\n"
            "🔐 بوت پارێزراو و ئاسایشدارە\n\n"
            "👑 خاوەن بوت هەمیشە چاودێری کارەکان دەکات 💚✨",
            reply_markup=main_menu()
        )

# ================= 🚀 MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()