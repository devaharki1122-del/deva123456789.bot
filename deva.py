import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

# ========= SETTINGS (هەموو شتێک لێرەیە) =========
BOT_TOKEN = "8251863494:AAFR8r-3Fg1y_qUhbqiXNiH7CWf3yiH931k"

API_ID = 123456
API_HASH = "0123456789abcdef0123456789abcdef"

CHANNEL_ID = -1002252176207
CHANNEL_LINK = "https://t.me/chanaly_boot"
# ================================================

app = Client(
    "video_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

# ---------- Force Join Check ----------
async def not_joined(client, user_id):
    try:
        member = await client.get_chat_member(CHANNEL_ID, user_id)
        return member.status not in ("member", "administrator", "creator")
    except:
        return True

join_buttons = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔔 جوینی چەناڵ بکە", url=CHANNEL_LINK)],
    [InlineKeyboardButton("✅ دووبارە هەوڵ بدە", callback_data="recheck")]
])

# ---------- /start ----------
@app.on_message(filters.command("start"))
async def start(client, message):
    if await not_joined(client, message.from_user.id):
        return await message.reply(
            "⚠️ بۆ بەکارهێنانی بوت پێویستە جوینی چەناڵ بکەیت",
            reply_markup=join_buttons
        )

    await message.reply(
        "👋 بەخێربێیت بۆ Universal Video Downloader Bot\n\n"
        "📥 لینک بنێرە بۆ دابەزاندنی ڤیدیۆ"
    )

# ---------- Recheck Button ----------
@app.on_callback_query(filters.regex("recheck"))
async def recheck(client, query):
    if await not_joined(client, query.from_user.id):
        await query.answer("❌ هێشتا جوین نەکراوە", show_alert=True)
    else:
        await query.message.delete()
        await query.message.reply("✅ سەرکەوتوو بوویت! لینک بنێرە")

# ---------- Download Function ----------
def download_video(url):
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'best',
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# ---------- Handle Links ----------
@app.on_message(filters.text & filters.private)
async def downloader(client, message):
    url = message.text.strip()

    if not url.startswith("http"):
        return

    if await not_joined(client, message.from_user.id):
        return await message.reply(
            "⚠️ سەرەتا جوینی چەناڵ بکە",
            reply_markup=join_buttons
        )

    msg = await message.reply("⏳ دابەزاندن دەست پێکرد...")

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, download_video, url)

        await message.reply_video("video.mp4", caption="✅ تەواو بوو")
        os.remove("video.mp4")

        await msg.delete()

    except Exception as e:
        await msg.edit(f"❌ هەڵە: {e}")

# ---------- Run Bot ----------
app.run()