# ===========================
#    + AI (100% )
#   – deva.py
# ===========================

import os, time
import yt_dlp
from openai import OpenAI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

# ==================  ==================
BOT_TOKEN = "8251863494:AAHLJgGgXvK4ZRkzELq3lWVPS7U7Jb4jsLU"
OPENAI_API_KEY = "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"
OWNER_ID = 8186735286

CHANNELS = [
    {"title": "  ", "link": "https://t.me/chanaly_boot", "id": -1002101234567},
    {"title": "  ", "link": "https://t.me/team_988", "id": -1002101234568},
]

client = OpenAI(api_key=OPENAI_API_KEY)

START_TIME = time.time()
USERS = set()
DOWNLOADS = 0
WAITING_LINK = set()
AI_USERS = set()

# ==================  ==================
def ():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("  ", callback_data="download")],
        [InlineKeyboardButton("   AI", callback_data="ai")],
        [InlineKeyboardButton("  ", callback_data="info")],
        [InlineKeyboardButton("  ", callback_data="admin")]
    ])

def ai_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("   ", callback_data="download")],
        [InlineKeyboardButton("   ", callback_data="back")]
    ])

# ==================   ==================
async def _(update, context):
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

async def _(update):
    kb = [[InlineKeyboardButton(c["title"], url=c["link"])] for c in CHANNELS]
    kb.append([InlineKeyboardButton("  ", callback_data="recheck")])
    await update.message.reply_text(
        "       ",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================== AI ==================
async def _ai(text):
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "         "},
            {"role": "user", "content": text}
        ]
    )
    return r.choices[0].message.content

# ================== /start ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _(update, context):
        await _(update)
        return

    USERS.add(update.effective_user.id)
    await update.message.reply_text(
        "   \n"
        "    \n\n"
        "     AI\n"
        "     \n"
        "     ( /  / )\n\n"
        "    ",
        reply_markup=()
    )

# ==================  ==================
async def (update: Update, context):
    global DOWNLOADS
    uid = update.effective_user.id
    text = update.message.text

    #  AI 
    if uid in AI_USERS:
        msg = await update.message.reply_text("  ...")
        reply = await _ai(text)
        await msg.edit_text(reply, reply_markup=ai_menu())
        return

    #  
    if uid in WAITING_LINK:
        WAITING_LINK.remove(uid)
        msg = await update.message.reply_text(" ...")

        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': '/tmp/%(id)s.%(ext)s',
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                file = ydl.prepare_filename(info)

            size = os.path.getsize(file)
            DOWNLOADS += 1

            caption = f"""
 {info.get('title')}
 : {info.get('view_count',0)}
 : {info.get('like_count',0)}
 : {info.get('comment_count',0)}
 : {size//1024//1024} MB
"""

            if size <= 2*1024*1024*1024:
                await update.message.reply_video(video=open(file,'rb'), caption=caption)
            else:
                await update.message.reply_text("    (  2GB)")

            os.remove(file)
            await msg.delete()

        except Exception as e:
            await msg.edit_text(f" : {e}")

# ==================  ==================
async def (update: Update, context):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    if q.data == "recheck":
        if await _(update, context):
            await q.edit_message_text("   ", reply_markup=())
        else:
            await _(update)

    elif q.data == "download":
        AI_USERS.discard(uid)
        WAITING_LINK.add(uid)
        await q.edit_message_text("     ", reply_markup=())

    elif q.data == "ai":
        WAITING_LINK.discard(uid)
        AI_USERS.add(uid)
        await q.edit_message_text(
            "  AI  !\n   ",
            reply_markup=ai_menu()
        )

    elif q.data == "back":
        AI_USERS.discard(uid)
        await q.edit_message_text("   ", reply_markup=())

    elif q.data == "info":
        uptime = int(time.time() - START_TIME)
        await q.edit_message_text(
            f"  \n : {uptime} \n : {len(USERS)}\n : {DOWNLOADS}",
            reply_markup=()
        )

    elif q.data == "admin" and uid == OWNER_ID:
        await q.edit_message_text(
            f"  \n : {len(USERS)}\n : {DOWNLOADS}",
            reply_markup=()
        )

# ================== MAIN ==================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ))
    app.add_handler(CallbackQueryHandler())
    app.run_polling()

if __name__ == "__main__":
    main()