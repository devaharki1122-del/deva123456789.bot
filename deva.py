import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 8186735286

SOURCE_CHANNELS = [
    {"title": "Channel 1", "link": "https://t.me/chanaly_boot", "id": -1002101234567},
    {"title": "Channel 2", "link": "https://t.me/team_988", "id": -1002101234568}
]

USERS = set()
DOWNLOADS = 0

# ================= FORCE JOIN =================
async def check_join(update, context):
    user_id = update.effective_user.id
    if user_id == OWNER_ID:
        return True
    for ch in SOURCE_CHANNELS:
        try:
            m = await context.bot.get_chat_member(ch["id"], user_id)
            if m.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

async def join_msg(update):
    buttons = [[InlineKeyboardButton(c["title"], url=c["link"])] for c in SOURCE_CHANNELS]
    buttons.append([InlineKeyboardButton("  ", callback_data="check")])
    await update.message.reply_text(
        "   :",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context):
        await join_msg(update)
        return

    USERS.add(update.effective_user.id)

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(" ", callback_data="download")],
        [InlineKeyboardButton("  ", callback_data="admin")]
    ])

    await update.message.reply_text(" !\n  ", reply_markup=kb)

# ================= DOWNLOAD =================
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global DOWNLOADS
    if not await check_join(update, context):
        await join_msg(update)
        return

    url = update.message.text.strip()
    msg = await update.message.reply_text(" ...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': '/tmp/%(id)s.%(ext)s',
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        size = os.path.getsize(file_path)
        DOWNLOADS += 1

        stats = f"""
 {info.get('title')}
 View: {info.get('view_count',0)}
 Like: {info.get('like_count',0)}
 Comment: {info.get('comment_count',0)}
 Share: {info.get('repost_count',0)}
 Size: {size//1024//1024}MB
"""

        if size > 2*1024*1024*1024:
            await msg.edit_text("   2GB\n\n " + url)
        else:
            await update.message.reply_video(video=open(file_path, "rb"), caption=stats)
            await msg.delete()

        os.remove(file_path)

    except Exception as e:
        await msg.edit_text(f" : {e}")

# ================= ADMIN PANEL =================
async def admin_panel(update: Update, context):
    if update.effective_user.id != OWNER_ID:
        return
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(" Users", callback_data="users")],
        [InlineKeyboardButton(" Downloads", callback_data="downloads")]
    ])
    await update.callback_query.edit_message_text(" Admin Panel", reply_markup=kb)

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "check":
        if await check_join(update, context):
            await q.edit_message_text(" !   ")
        else:
            await join_msg(update)

    elif q.data == "admin":
        await admin_panel(update, context)

    elif q.data == "users":
        await q.edit_message_text(f" Users: {len(USERS)}")

    elif q.data == "downloads":
        await q.edit_message_text(f" Downloads: {DOWNLOADS}")

# ================= MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(buttons))
    app.run_polling()

if __name__ == "__main__":
    main()