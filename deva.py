import os
import requests
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "chanaly_boot"
OWNER_USERNAME = "Deva_harki"

# ================= SAVE USERS =================
USERS_FILE = "users.txt"
def save_user(user_id):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w").close()
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

# ================= FORCE JOIN =================
async def force_join_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", update.effective_user.id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ================= KEYBOARDS =================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 داونلۆد", callback_data="download")],
        [InlineKeyboardButton("ℹ️ زانیاری", callback_data="about")],
        [InlineKeyboardButton("📨 خاوەن بۆت", callback_data="owner")]
    ])
def back_btn():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 گەڕانەوە", callback_data="home")]])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)
    if not await force_join_check(update, context):
        await update.message.reply_text(
            "🔒 تکایە چۆینی چانەل بکە",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join", url=f"https://t.me/{CHANNEL_USERNAME}")],
                [InlineKeyboardButton("✅ پشکنینەوە", callback_data="check_join")]
            ])
        )
        return
    await update.message.reply_text(
        "🔗 لینک بنێرە بۆ داونلۆد",
        reply_markup=main_menu()
    )

# ================= BUTTONS =================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "home":
        await q.edit_message_text("🏠", reply_markup=main_menu())
    elif q.data == "about":
        await q.edit_message_text(
            "TikTok • Instagram • YouTube • Snapchat • Facebook • Twitter/X\n\n"
            "❌ yt-dlp\n✅ API Downloader with retry & fallback",
            reply_markup=back_btn()
        )
    elif q.data == "owner":
        await q.edit_message_text(f"https://t.me/{OWNER_USERNAME}", reply_markup=back_btn())
    elif q.data == "download":
        await q.edit_message_text("🔗 لینک ڤیدیۆ بنێرە", reply_markup=back_btn())
    elif q.data == "check_join":
        if await force_join_check(update, context):
            await q.edit_message_text("✅", reply_markup=main_menu())
        else:
            await q.answer("❌ هێشتا چۆینت نەکردووە", show_alert=True)

# ================= UNIVERSAL API + RETRY =================
APIS = [
    {"name": "cobalt", "url": "https://api.cobalt.tools/api/json"},
    {"name": "snapx", "url": "https://api.snapx.download/tiktok"},
    {"name": "tikmate", "url": "https://api.tikmate.app/api/lookup"},
    {"name": "saveinsta", "url": "https://api.saveinsta.app/api"},
    {"name": "ytdown", "url": "https://ytdownloaderapi.com/api"},
]

def download_video(url, filename="video.mp4", retries=3):
    headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
    for attempt in range(retries):
        for api in APIS:
            try:
                payload = {"url": url,"vQuality": "max","vCodec": "h264","isAudioOnly": False}
                r = requests.post(api["url"], json=payload, headers=headers, timeout=30)
                data = r.json()
                video_url = None
                if "url" in data:
                    video_url = data["url"]
                elif "data" in data and "play" in data["data"]:
                    video_url = data["data"]["play"]
                else:
                    continue
                video = requests.get(video_url, stream=True, timeout=30)
                with open(filename, "wb") as f:
                    for chunk in video.iter_content(1024):
                        if chunk:
                            f.write(chunk)
                return True
            except Exception as e:
                print(f"[API {api['name']}] failed: {e}")
        time.sleep(2)
    raise Exception("All APIs failed after retries")

# ================= HANDLE LINK =================
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        return
    await update.message.reply_text("⏳ داونلۆد دەستی پێکرد...")
    try:
        file = "video.mp4"
        download_video(url, file)
        await update.message.reply_video(video=open(file, "rb"), caption="✅ داونلۆد کرا")
        os.remove(file)
    except Exception as e:
        await update.message.reply_text(f"❌ نەتوانرا داونلۆد بکرێت\n{e}")

# ================= MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.run_polling()

if __name__ == "__main__":
    main()