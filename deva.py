import os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

# ================== SETTINGS ==================
BOT_TOKEN = "8251863494:AAF721wUAAIoOFPTZgvkwqKqYFuojUVRM_4"

FORCE_CHANNEL = "chanaly_boot"  # بدون @
CHANNEL_LINK = "https://t.me/chanaly_boot"
# =============================================

app = Client(
    "video_downloader_bot",
    bot_token=BOT_TOKEN
)

# ---------- Force Join Check ----------
async def check_force_join(client, message):
    user_id = message.from_user.id
    try:
        member = await client.get_chat_member(FORCE_CHANNEL, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except UserNotParticipant:
        pass

    await message.reply(
        "🔔 تکایە سەرەتا جۆینی چەناڵ بکە بۆ بەکارهێنانی بوت",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔔 جۆینی چەناڵ", url=CHANNEL_LINK)],
                [InlineKeyboardButton("✅ دووبارە هەوڵ بدە", callback_data="recheck_join")]
            ]
        )
    )
    return False

# ---------- Recheck Join Button ----------
@app.on_callback_query(filters.regex("recheck_join"))
async def recheck_join(client, callback_query):
    if await check_force_join(client, callback_query.message):
        await callback_query.message.delete()
        await callback_query.message.reply("✅ سوپاس، ئێستا دەتوانیت بوت بەکاربهێنیت")
    await callback_query.answer()

# ---------- Start ----------
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await check_force_join(client, message):
        return
    await message.reply("👋 بەخێربێیت\nلینک بنێرە بۆ داگرتنی ڤیدیۆ")

# ---------- Download Function ----------
def download_video(url):
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'best',
        'quiet': True,
        'noplaylist': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir():
        if file.startswith("video."):
            return file

# ---------- Handle Links ----------
@app.on_message(filters.private & filters.text)
async def handle_links(client, message):
    if not await check_force_join(client, message):
        return

    url = message.text.strip()

    if "http" not in url:
        return

    msg = await message.reply("⏳ چاوەڕوان بە... داگرتن دەستپێکرد")

    try:
        file_path = download_video(url)
        await message.reply_video(file_path)
        os.remove(file_path)
        await msg.delete()
    except Exception as e:
        await msg.edit(f"❌ هەڵەیەک ڕوویدا\n{e}")

# ---------- Run Bot ----------
app.run()