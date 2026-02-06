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
OWNER_ID = 8186735286
GROUP_LINKS = [
    ("  ", "https://t.me/team_988"),
    ("  ", "https://t.me/chanaly_boot")
]
LANGUAGES = {
    "ku": "",
    "ar": "",
    "en": "",
    "fa": "",
    "tr": "",
    "es": "",
    "fr": "",
    "ru": "",
    "zh": "",
    "de": ""
}
user_lang = {}
os.makedirs("downloads", exist_ok=True)

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
    greeting = {"ku": f" ****! ", "en": f"Hello, **Devit**! "}.get(lang, f"Hello, **Devit**! ")
    buttons = [
        [InlineKeyboardButton(" ", callback_data="download")],
        [InlineKeyboardButton(" ", callback_data="info")],
        [InlineKeyboardButton(" ", callback_data="language")],        [InlineKeyboardButton(" VIP", callback_data="vip")],
        [InlineKeyboardButton(" Student Mode", callback_data="student")],
        [InlineKeyboardButton(GROUP_LINKS[0][0], url=GROUP_LINKS[0][1])],
        [InlineKeyboardButton(GROUP_LINKS[1][0], url=GROUP_LINKS[1][1])],
        [InlineKeyboardButton("    @Deva_harki", callback_data="contact_owner")]
    ]
    await update.message.reply_text(
        f"{greeting}\n\n          !\n   .",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

async def language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    buttons = [[InlineKeyboardButton(name, callback_data=f"set_lang_{code}")] for code, name in LANGUAGES.items()]
    buttons.append([InlineKeyboardButton(" ", callback_data="back_start")])
    await query.edit_message_text(" :", reply_markup=InlineKeyboardMarkup(buttons))

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang_code = query.data.split("_")[-1]
    user_lang[query.from_user.id] = lang_code
    await query.answer(" ! ")
    await start(query, context)

async def info_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = user_lang.get(query.from_user.id, "ku")
    info_text = {
        "ku": "        TikTok, Instagram, YouTube,  !\n\n"
              "•    \n•  +   \n• AI + \n•    \n\n  @Deva_harki",
        "en": "This bot downloads videos & images from TikTok, Instagram, YouTube, and more!\n\n"
              "• Most powerful downloader\n• Audio + Video merged\n• AI + Emojis\n• Full owner control\n\nCustomized for @Deva_harki"
    }.get(lang, info_text["en"])
    buttons = [
        [InlineKeyboardButton("    @Deva_harki", callback_data="contact_owner")],
        [InlineKeyboardButton(" ", callback_data="back_start")]
    ]
    await query.edit_message_text(info_text, reply_markup=InlineKeyboardMarkup(buttons))

async def contact_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("   @Deva_harki:")

async def forward_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text and update.message.from_user.id != OWNER_ID:
        user = update.message.from_user        msg = f" *   !*\n\n: {user.full_name}\nID: `{user.id}`\n\n{update.message.text}"
        await context.bot.send_message(chat_id=OWNER_ID, text=msg, parse_mode="Markdown")
        await update.message.reply_text("   ! ")

async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != OWNER_ID:
        lang = user_lang.get(user_id, "en")
        no_access = {"ku": "  ! ", "en": "Access denied! "}
        await update.message.reply_text(no_access.get(lang, "Access denied! "))
        return

    url = update.message.text.strip()
    supported = ["tiktok.com", "instagram.com", "youtube.com", "youtu.be", "facebook.com", "fb.watch"]
    if not any(domain in url for domain in supported):
        await update.message.reply_text("  ! ")
        return

    lang = user_lang.get(user_id, "ku")
    wait_msg = {"ku": "    …!", "en": " Devit, please wait a moment…!"}
    msg = await update.message.reply_text(wait_msg.get(lang, " Please wait…!"))

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'socket_timeout': 20,
        'retries': 3
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
            if not os.path.exists(filepath):
                raise Exception("   !")

            title = info.get('title', 'Video')
            views = info.get('view_count', 'N/A')
            likes = info.get('like_count', 'N/A')
            comments = info.get('comment_count', 'N/A')
            shares = info.get('repost_count', info.get('share_count', 'N/A'))

        report = (
            f" ** !**\n\n"
            f": {title}\n"
            f" : {views}\n"            f" : {likes}\n"
            f" : {comments}\n"
            f" : {shares}"
        )
        await context.bot.send_message(chat_id=OWNER_ID, text=report, parse_mode="Markdown")
        await context.bot.send_document(chat_id=OWNER_ID, document=open(filepath, 'rb'), caption="  ")
        await msg.edit_text("   !    .")
        os.remove(filepath)

    except Exception as e:
        error_msg = f" : {str(e)[:500]}"
        await msg.edit_text(error_msg)
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)

async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(query, context)

def main():
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, forward_to_owner))
    app.add_handler(CallbackQueryHandler(language_menu, pattern="^language$"))
    app.add_handler(CallbackQueryHandler(set_language, pattern="^set_lang_"))
    app.add_handler(CallbackQueryHandler(info_section, pattern="^info$"))
    app.add_handler(CallbackQueryHandler(contact_owner, pattern="^contact_owner$"))
    app.add_handler(CallbackQueryHandler(back_to_start, pattern="^back_start$"))
    app.add_handler(CallbackQueryHandler(lambda u,c: u.callback_query.edit_message_text("    :"), pattern="^download$"))
    app.add_handler(CallbackQueryHandler(lambda u,c: u.callback_query.edit_message_text(" VIP ..."), pattern="^vip$"))
    app.add_handler(CallbackQueryHandler(lambda u,c: u.callback_query.edit_message_text(" Student Mode..."), pattern="^student$"))

    print("   !  @Deva_harki ")
    app.run_polling()

if __name__ == "__main__":
    main()