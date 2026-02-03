import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
import openai

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # بۆ AI chat

CHANNEL_USERNAME = "chanaly_boot"
OWNER_USERNAME = "Deva_harki"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

openai.api_key = OPENAI_API_KEY

# ================== USER STATE ==================
USER_STATE = {}  # store temporary states like 'waiting_link' or 'ai_chat'

# ================== FORCE JOIN ==================
async def force_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        m = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", update.effective_user.id)
        return m.status in ("member", "administrator", "creator")
    except:
        return False

# ================== MENUS ==================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 داونلۆد ڤیدیۆ / MP3", callback_data="download")],
        [InlineKeyboardButton("🗨️ قسە لە بوت", callback_data="chat")],
        [InlineKeyboardButton("ℹ️ زانیاری", callback_data="about")],
        [InlineKeyboardButton("📨 پەیوەندی", callback_data="owner")]
    ])

def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 گەڕانەوە", callback_data="home")]])

def media_type_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎥 ڤیدیۆ", callback_data="video")],
        [InlineKeyboardButton("🎵 MP3", callback_data="audio")],
        [InlineKeyboardButton("🔙 گەڕانەوە", callback_data="download")]
    ])

def quality_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1080p", callback_data="1080")],
        [InlineKeyboardButton("720p", callback_data="720")],
        [InlineKeyboardButton("480p", callback_data="480")],
        [InlineKeyboardButton("🔙 گەڕانەوە", callback_data="media_type")]
    ])

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await force_join(update, context):
        kb = [
            [InlineKeyboardButton("📢 چۆین بکە", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("✅ پشکنینەوە", callback_data="check")]
        ]
        await update.message.reply_text(
            "🔒 تکایە سەرەتا چۆینی چانەل بکە 👇",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return

    await update.message.reply_text(
        "👋 بەخێربێیت\n\n"
        "🔗 لینک ڤیدیۆ یان پەیامەکەت بنێرە",
        reply_markup=main_menu()
    )

# ================== BUTTON HANDLER ==================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    data = q.data

    if data == "home":
        USER_STATE.pop(user_id, None)
        await q.edit_message_text("🏠 سەرەتا", reply_markup=main_menu())

    elif data == "download":
        USER_STATE[user_id] = "waiting_link"
        await q.edit_message_text("🔗 لینک بنێرە", reply_markup=back_menu())

    elif data == "chat":
        USER_STATE[user_id] = "ai_chat"
        await q.edit_message_text("💬 دەتوانی قسە لە بوت بکەیت (Sorani)", reply_markup=back_menu())

    elif data == "about":
        await q.edit_message_text(
            f"🤖 Universal Downloader Bot\n🎥 TikTok/Instagram/YouTube/Facebook/X\n"
            f"⚡ خێرا و پارێزراو\n👨‍💻 @{OWNER_USERNAME}",
            reply_markup=back_menu()
        )

    elif data == "owner":
        await q.edit_message_text(f"https://t.me/{OWNER_USERNAME}", reply_markup=back_menu())

    elif data == "check":
        if await force_join(update, context):
            await q.edit_message_text("✅ سەرکەوتوو بوو", reply_markup=main_menu())
        else:
            await q.answer("❌ هێشتا چۆینت نەکردووە", show_alert=True)

# ================== DOWNLOAD FUNCTION ==================
def download_video(url, media_type="video", quality=None):
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title).50s.%(ext)s",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "retries": 5,
        "fragment_retries": 5,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        "cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
    }

    if media_type == "audio":
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}]
    elif quality:
        ydl_opts["format"] = f"bestvideo[height<={quality}]+bestaudio/best"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if info is None:
            raise Exception("ڤیدیۆکە private یان age-restricted ـە (cookies پێویستە)")
        return ydl.prepare_filename(info)

# ================== HANDLE MESSAGES ==================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = USER_STATE.get(user_id)
    text = update.message.text.strip()
    msg = await update.message.reply_text("⏳ کاردەکەم...")

    try:
        if state == "waiting_link":
            # default video download
            file_path = download_video(text, media_type="video")
            await update.message.reply_video(video=open(file_path, "rb"), caption="✅ داونلۆد سەرکەوتوو بوو")
            os.remove(file_path)
            USER_STATE.pop(user_id, None)

        elif state == "ai_chat":
            # AI Chat
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"user","content":text}]
            )
            answer = response['choices'][0]['message']['content']
            await msg.edit_text(f"💬 {answer}")
            USER_STATE.pop(user_id, None)

        else:
            await msg.edit_text("❌ تکایە لینک یان پەیامەکەت بنێرە", reply_markup=main_menu())

    except Exception as e:
        await msg.edit_text(f"❌ هەڵە ڕوویدا:\n{str(e)[:350]}")

# ================== MAIN ==================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()