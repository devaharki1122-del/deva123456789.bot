# deva.py
#    
# : @Deva_harki | ID: 8186735286

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import yt_dlp
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError(" BOT_TOKEN  !  Railway  Variables  .")

OWNER_ID = 8186735286
GROUP_LINKS = [
    ("  ", "https://t.me/team_988"),
    ("  ", "https://t.me/chanaly_boot")
]
LANGUAGES = {"ku": "", "en": ""}
user_lang = {}
os.makedirs("downloads", exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    if uid != OWNER_ID:
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f" *  !*\n\n"
                 f": {user.full_name}\nID: `{uid}`\n"
                 f": @{user.username or 'None'}\n"
                 f": {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode="Markdown"
        )
    lang = user_lang.get(uid, "ku")
    greeting = {"ku": f" ****! ", "en": f"Hello, **Devit**! "}[lang]
    buttons = [
        [InlineKeyboardButton(" ", callback_data="download")],
        [InlineKeyboardButton(" ", callback_data="info")],
        [InlineKeyboardButton(GROUP_LINKS[0][0], url=GROUP_LINKS[0][1])],
        [InlineKeyboardButton(GROUP_LINKS[1][0], url=GROUP_LINKS[1][1])],
        [InlineKeyboardButton("    @Deva_harki", callback_data="contact_owner")]
    ]
    await update.message.reply_text(
        f"{greeting}\n\n      TikTok, YouTube, Instagram!\n .",        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

async def info_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = user_lang.get(query.from_user.id, "ku")
    info_text = {
        "ku": "          !\n\n•   \n•  +   \n•   @Deva_harki",
        "en": "This bot downloads videos from all platforms!\n\n• Owner-only access\n• Audio+Video merged\n• Customized for @Deva_harki"
    }[lang]
    buttons = [[InlineKeyboardButton("    @Deva_harki", callback_data="contact_owner")]]
    await query.edit_message_text(info_text, reply_markup=InlineKeyboardMarkup(buttons))

async def contact_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("   @Deva_harki:")

async def forward_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text and update.message.from_user.id != OWNER_ID:
        user = update.message.from_user
        msg = f" * !*\n\n: {user.full_name}\nID: `{user.id}`\n\n{update.message.text}"
        await context.bot.send_message(chat_id=OWNER_ID, text=msg, parse_mode="Markdown")
        await update.message.reply_text("   ! ")

async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("  ! ")
        return

    url = update.message.text.strip()
    supported = ["tiktok.com", "instagram.com", "youtube.com", "youtu.be"]
    if not any(domain in url for domain in supported):
        await update.message.reply_text("  ! ")
        return

    msg = await update.message.reply_text("   …!")

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'socket_timeout': 20,
        'retries': 3    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
            if not os.path.exists(filepath):
                raise Exception(" !")

        await context.bot.send_document(chat_id=OWNER_ID, document=open(filepath, 'rb'), caption=" !")
        await msg.edit_text("   !")
        os.remove(filepath)

    except Exception as e:
        error_msg = f" : {str(e)[:400]}"
        await msg.edit_text(error_msg)
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, forward_to_owner))
    app.add_handler(CallbackQueryHandler(info_section, pattern="^info$"))
    app.add_handler(CallbackQueryHandler(contact_owner, pattern="^contact_owner$"))
    app.add_handler(CallbackQueryHandler(lambda u,c: u.callback_query.edit_message_text("    :"), pattern="^download$"))

    logger.info("   !  @Deva_harki ")
    app.run_polling()

if __name__ == "__main__":
    main()