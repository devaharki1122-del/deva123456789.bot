import os
import re
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
import logging

#     ID 
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 8186735286
OWNER_USERNAME = "@Deva_harki"

#  
logging.basicConfig(level=logging.INFO)

#    TikTok  
def fix_tiktok_url(url):
    if "tiktok.com" in url:
        match = re.search(r'/video/(\d+)', url)
        if match:
            return f"https://vm.tiktok.com/{match.group(1)}/"
    return url

#  /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f" * !*\n\n"
                 f": {user.full_name}\n"
                 f"ID: `{user.id}`\n"
                 f": tg://user?id={user.id}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"   : {e}")

    keyboard = [
        [InlineKeyboardButton("  ", callback_data="download")],
        [InlineKeyboardButton(" ", callback_data="info"),
         InlineKeyboardButton("  ", callback_data="admin")],
        [InlineKeyboardButton("    ", url="https://t.me/Deva_harki")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f" {user.first_name}! \n"        "   (YouTube, TikTok, Instagram...) ",
        reply_markup=reply_markup
    )

#  
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_url = update.message.text.strip()
    url = fix_tiktok_url(raw_url)

    #  
    valid_domains = ["http", "youtu", "instagram", "tiktok", "facebook", "twitter", "x.com", "snapchat", "vimeo"]
    if not any(domain in url for domain in valid_domains):
        await update.message.reply_text("   !")
        return

    msg = await update.message.reply_text("   ...")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': '%(title).50s.%(ext)s',  #      
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
        'retries': 3,
        'socket_timeout': 15,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # 
        title = info.get('title', '')
        views = info.get('view_count', '')
        likes = info.get('like_count', '')
        comments = info.get('comment_count', '')
        shares = info.get('repost_count', '') or info.get('share_count', '')

        caption = (
            f" *{title}*\n\n"
            f" : {views}\n"
            f" : {likes}\n"
            f" : {comments}\n"
            f" : {shares}\n\n"
            f" @Deva_harki"
        )

        await update.message.reply_video(video=open(filename, 'rb'), caption=caption, parse_mode="Markdown")        os.remove(filename)

        #  
        await context.bot.send_message(
            OWNER_ID,
            f" * !*\n"
            f": [{update.effective_user.full_name}](tg://user?id={update.effective_user.id})",
            parse_mode="Markdown"
        )

    except Exception as e:
        error_msg = str(e)
        if "Log in for access" in error_msg:
            reply = (
                "   !\n"
                "  **vm.tiktok.com** .\n\n"
                "  :\n"
                ".  Share \n"
                ". Copy link \n"
                ".    !"
            )
        else:
            reply = f" : {error_msg[:200]}..."

        await msg.edit_text(reply)
        logging.error(f"  : {e}")

#  
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "download":
        await query.message.reply_text("    (YouTube, TikTok, Instagram...)")

    elif query.data == "info":
        info_text = (
            " * *\n\n"
            ": Glitch Media Downloader\n"
            ": 2.2 (-)\n"
            ": yt-dlp + Telegram Bot API\n"
            ": @Deva_harki\n"
            ":   \n"
            "    @Deva_harki "
        )
        await query.message.reply_text(info_text, parse_mode="Markdown")

    elif query.data == "admin":
        join1 = "https://t.me/GlitchGroup1"
        join2 = "https://t.me/GlitchGroup2"        admin_kb = [
            [InlineKeyboardButton("  ", url=join1)],
            [InlineKeyboardButton("  ", url=join2)],
            [InlineKeyboardButton("   ", url="https://t.me/Deva_harki")],
            [InlineKeyboardButton(" ", callback_data="back")]
        ]
        await query.message.reply_text(
            " * *", 
            reply_markup=InlineKeyboardMarkup(admin_kb),
            parse_mode="Markdown"
        )

    elif query.data == "back":
        await start(query, context)

#  
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("   ...")
    app.run_polling()

if __name__ == "__main__":
    main()