# deva.py
import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================   ==================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8251863494:AAHLJgGgXvK4ZRkzELq3lWVPS7U7Jb4jsLU")
OWNER_ID = 8186735286

#   (ID   !)
SOURCE_CHANNELS = [
    {"title": " ", "link": "https://t.me/chanaly_boot", "id": -1002101234567},  #    ID 
    {"title": " ", "link": "https://t.me/team_988", "id": -1002101234568}     #    ID 
]

# ==================    ==================
async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == OWNER_ID:
        return True
    for channel in SOURCE_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
            return False
    return True

async def force_join_message(update: Update):
    buttons = [
        [InlineKeyboardButton(chan["title"], url=chan["link"])] for chan in SOURCE_CHANNELS
    ]
    buttons.append([InlineKeyboardButton("  ", callback_data="check_join")])
    await update.message.reply_text(
        "       :",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ==================    ( !) ==================
async def download_video(url: str) -> str:
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': '/tmp/%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'geo_bypass': True,
        'socket_timeout': 20,    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# ==================   ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_membership(update, context):
        await force_join_message(update)
        return
    await update.message.reply_text(
        f" {update.effective_user.first_name}! \n   (TikTok, Instagram, YouTube, Twitter, Facebook, Reddit, Vimeo, Snapchat...)"
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_membership(update, context):
        await force_join_message(update)
        return
    url = update.message.text.strip()
    if "http" not in url:
        await update.message.reply_text("  !")
        return
    msg = await update.message.reply_text(" ...")

    try:
        file_path = await download_video(url)
        if os.path.getsize(file_path) > 50 * 1024 * 1024:  # 50MB limit for Telegram
            await msg.edit_text("    (  50MB).")
        else:
            await update.message.reply_video(video=open(file_path, 'rb'), caption="  !")
        os.remove(file_path)
    except Exception as e:
        error_msg = str(e)[:200]
        await msg.edit_text(f" : {error_msg}")
    finally:
        if 'msg' in locals():
            try:
                await msg.delete()
            except:
                pass

# ==================   ==================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "check_join":
        if await check_membership(update, context):
            await query.edit_message_text(" !   .")
            await start(update, context)
        else:            await force_join_message(update)

# ==================   ==================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("   ...")
    app.run_polling()

if __name__ == "__main__":
    main()