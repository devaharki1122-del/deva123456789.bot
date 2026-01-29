# -*- coding: utf-8 -*-
# =========================================
#    (AI + Download)
# deva.py -  
# 100%  | Emoji | Railway Ready
#    @Deva_harki
# =========================================

import os, time, asyncio
import yt_dlp
import openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# ==================   ==================
FLAG = ""
BOT_TOKEN = "8251863494:AAHLJgGgXvK4ZRkzELq3lWVPS7U7Jb4jsLU"
OPENAI_API_KEY = "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"
OWNER_ID = 8186735286

openai.api_key = OPENAI_API_KEY

CHANNELS = [
    {"title": f"{FLAG}  ", "link": "https://t.me/chanaly_boot", "id": -1002101234567},
    {"title": f"{FLAG}  ", "link": "https://t.me/team_988", "id": -1002101234568},
]

START_TIME = time.time()
USERS = set()
DOWNLOADS = 0
MODE_AI = set()
MODE_DOWNLOAD = set()

# ==================  AI ==================
async def ai_reply(text):
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": " AI     "},
            {"role": "user", "content": text}
        ]
    )
    return res.choices[0].message["content"]

# ==================   ==================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{FLAG} AI ", callback_data="ai")],
        [InlineKeyboardButton(f"{FLAG} ", callback_data="download")],
        [InlineKeyboardButton(f"{FLAG} ", callback_data="info")]
    ])

def back_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{FLAG} ", callback_data="back")]
    ])

# ==================  Force Join ==================
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
    kb.append([InlineKeyboardButton(f"{FLAG} ", callback_data="recheck")])
    await update.message.reply_text(
        f"{FLAG}     ",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================== /start ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context):
        await join_message(update)
        return

    USERS.add(update.effective_user.id)
    await update.message.reply_text(
        f"{FLAG}   \n\n"
        f" AI \n"
        f"   \n\n"
        f"{FLAG}   ",
        reply_markup=main_menu()
    )

# ==================   ==================
async def handle_message(update: Update, context):
    global DOWNLOADS
    uid = update.effective_user.id
    text = update.message.text

    if uid in MODE_AI:
        reply = await ai_reply(text)
        await update.message.reply_text(reply, reply_markup=back_menu())
        return

    if uid in MODE_DOWNLOAD:
        MODE_DOWNLOAD.remove(uid)
        msg = await update.message.reply_text(f"{FLAG} ...")

        try:
            ydl_opts = {
                "format": "best",
                "outtmpl": "/tmp/%(id)s.%(ext)s",
                "quiet": True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                file = ydl.prepare_filename(info)

            size = os.path.getsize(file)
            DOWNLOADS += 1

            if size > 2 * 1024 * 1024 * 1024:
                await msg.edit_text("   ")
                os.remove(file)
                return

            await update.message.reply_video(
                video=open(file, "rb"),
                caption=f"{FLAG} {info.get('title')}"
            )
            os.remove(file)
            await msg.delete()

        except Exception as e:
            await msg.edit_text(f" : {e}")

# ==================  Callback ==================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    if q.data == "recheck":
        if await check_join(update, context):
            await q.edit_message_text("  ", reply_markup=main_menu())
        else:
            await join_message(update)

    elif q.data == "ai":
        MODE_AI.add(uid)
        MODE_DOWNLOAD.discard(uid)
        await q.edit_message_text("   ", reply_markup=back_menu())

    elif q.data == "download":
        MODE_DOWNLOAD.add(uid)
        MODE_AI.discard(uid)
        await q.edit_message_text("  ", reply_markup=back_menu())

    elif q.data == "back":
        MODE_AI.discard(uid)
        MODE_DOWNLOAD.discard(uid)
        await q.edit_message_text(" ", reply_markup=main_menu())

    elif q.data == "info":
        uptime = int(time.time() - START_TIME)
        await q.edit_message_text(
            f"{FLAG} {uptime}s\n"
            f"{FLAG} {len(USERS)}\n"
            f"{FLAG} {DOWNLOADS}",
            reply_markup=main_menu()
        )

# ==================  MAIN ==================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print(" Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()