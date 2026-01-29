import os, asyncio, yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
OWNER_ID = 8186735286
MAX_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

SOURCE_CHANNELS = [
    {"title": " ", "link": "https://t.me/chanaly_boot", "id": -1002101234567},
    {"title": " ", "link": "https://t.me/team_988", "id": -1002101234568},
]

# ==================  Force Join ==================
async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        return True
    for ch in SOURCE_CHANNELS:
        try:
            m = await context.bot.get_chat_member(ch["id"], update.effective_user.id)
            if m.status in ("left", "kicked"):
                return False
        except:
            return False
    return True

async def force_join_message(update: Update):
    buttons = [[InlineKeyboardButton(c["title"], url=c["link"])] for c in SOURCE_CHANNELS]
    buttons.append([InlineKeyboardButton("  ", callback_data="check_join")])

    text = "    "
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# ==================  Download ==================
def _info(url):
    ydl_opts = {"quiet": True, "noplaylist": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def _download(url):
    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": "/tmp/%(id)s.%(ext)s",
        "noplaylist": True,
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

async def get_info(url):
    return await asyncio.to_thread(_info, url)

async def download(url):
    return await asyncio.to_thread(_download, url)

# ==================  Handlers ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_membership(update, context):
        await force_join_message(update)
        return
    await update.message.reply_text("   ")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_membership(update, context):
        await force_join_message(update)
        return

    url = update.message.text.strip()
    if not url.startswith("http"):
        return await update.message.reply_text("   ")

    msg = await update.message.reply_text(" ...")

    try:
        info = await get_info(url)
        size = info.get("filesize") or info.get("filesize_approx", 0)

        if size > MAX_SIZE:
            await msg.edit_text(
                f"   \n\n"
                f" : {size/1024/1024/1024:.2f}GB\n\n"
                f" :\n{info['webpage_url']}"
            )
            return

        await msg.edit_text(" ...")
        file_path = await download(url)

        await msg.edit_text(" ...")
        with open(file_path, "rb") as f:
            await update.message.reply_video(f, caption="  ")

        os.remove(file_path)

    except Exception as e:
        await msg.edit_text(f" : {str(e)[:200]}")

# ==================  Buttons ==================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "check_join":
        if await check_membership(update, context):
            await q.edit_message_text("  ")
        else:
            await force_join_message(update)

# ==================  Main ==================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_handler))
    print(" Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()