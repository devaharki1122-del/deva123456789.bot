# -*- coding: utf-8 -*-
# =========================================
# 🇭🇺⬇️ بوتی داولۆدی ڤیدیۆ (Hungary Flag)
# یەک فایل – deva.py
# تەنها Download Bot
# Forci Join 2 چەنال
# Admin Panel
# هەموو شت بە دووگمە
# =========================================

import os
import time
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# ================== ⚙️ ڕێکخستن ==================
FLAG = "🇭🇺"
BOT_TOKEN = "8251863494:AAERsUmTD3GgfeEAkHNsHMd2g-ded4XWT5w"
OWNER_ID = 8186735286

CHANNELS = [
    {"title": f"{FLAG} چەنال یەکەم", "link": "https://t.me/chanal1", "id": -1001111111111},
    {"title": f"{FLAG} چەنال دووەم", "link": "https://t.me/chanal2", "id": -1002222222222},
]

USERS = set()
DOWNLOADS = 0
START_TIME = time.time()
MODE_DOWNLOAD = set()

# ================== 🔒 Force Join ==================
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

async def join_message(update):
    kb = [[InlineKeyboardButton(c["title"], url=c["link"])] for c in CHANNELS]
    kb.append([InlineKeyboardButton(f"{FLAG}✅ پشکنین", callback_data="recheck")])
    await update.message.reply_text(
        f"{FLAG}🔒 تکایە سەرەتا جۆین بکە 👇",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================== 🔘 دووگمەکان ==================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{FLAG}⬇️ داولۆد", callback_data="download")],
        [InlineKeyboardButton(f"{FLAG}ℹ️ زانیاری", callback_data="info")]
    ])

def back_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{FLAG}⬅️ گەڕانەوە", callback_data="back")]
    ])

def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{FLAG}👥 بەکارهێنەر", callback_data="users")],
        [InlineKeyboardButton(f"{FLAG}⬇️ داولۆد", callback_data="downloads")],
        [InlineKeyboardButton(f"{FLAG}⏱ کات", callback_data="uptime")]
    ])

# ================== /start ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context):
        await join_message(update)
        return

    USERS.add(update.effective_user.id)

    await update.message.reply_text(
        f"{FLAG} سڵاو ❤️\n"
        f"{FLAG} ئەم بوتە هەموو ڤیدیۆیەک داگرێت\n\n"
        f"{FLAG} دووگمە هەڵبژێرە 👇",
        reply_markup=main_menu()
    )

# ================== 💬 Message ==================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global DOWNLOADS
    uid = update.effective_user.id
    text = update.message.text

    if uid in MODE_DOWNLOAD:
        MODE_DOWNLOAD.remove(uid)
        msg = await update.message.reply_text(f"{FLAG}⏳ داولۆد دەستپێکرد...")

        try:
            ydl_opts = {
                "format": "best",
                "outtmpl": "/tmp/%(id)s.%(ext)s",
                "noplaylist": True,
                "quiet": True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                file = ydl.prepare_filename(info)

            size = os.path.getsize(file)
            DOWNLOADS += 1

            caption = (
                f"{FLAG}🎬 {info.get('title')}\n"
                f"{FLAG}👁 {info.get('view_count',0)}\n"
                f"{FLAG}👍 {info.get('like_count',0)}\n"
                f"{FLAG}💬 {info.get('comment_count',0)}\n"
                f"{FLAG}📦 {size//1024//1024} MB"
            )

            await update.message.reply_video(
                video=open(file, "rb"),
                caption=caption
            )

            os.remove(file)
            await msg.delete()

        except Exception as e:
            await msg.edit_text(f"{FLAG}❌ هەڵە: {e}")

# ================== 🔘 Callback ==================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    if q.data == "recheck":
        if await check_join(update, context):
            await q.edit_message_text(f"{FLAG}✅ سەرکەوتوو", reply_markup=main_menu())
        else:
            await join_message(update)

    elif q.data == "download":
        MODE_DOWNLOAD.add(uid)
        await q.edit_message_text(
            f"{FLAG}⬇️ لینک بنێرە",
            reply_markup=back_menu()
        )

    elif q.data == "back":
        MODE_DOWNLOAD.discard(uid)
        await q.edit_message_text(f"{FLAG}🏠 سەرەکی", reply_markup=main_menu())

    elif q.data == "info":
        await q.edit_message_text(
            f"{FLAG}👥 {len(USERS)}\n"
            f"{FLAG}⬇️ {DOWNLOADS}",
            reply_markup=main_menu()
        )

    # ===== Admin =====
    elif uid == OWNER_ID:
        if q.data == "users":
            await q.edit_message_text(f"{FLAG}👥 {len(USERS)}", reply_markup=admin_menu())
        elif q.data == "downloads":
            await q.edit_message_text(f"{FLAG}⬇️ {DOWNLOADS}", reply_markup=admin_menu())
        elif q.data == "uptime":
            up = int(time.time() - START_TIME)
            await q.edit_message_text(f"{FLAG}⏱ {up} چرکە", reply_markup=admin_menu())

# ================== 🚀 MAIN ==================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(buttons))
    print("🇭🇺⬇️ Bot Running ...")
    app.run_polling()

if __name__ == "__main__":
    main()