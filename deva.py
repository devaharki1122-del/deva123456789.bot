import os
import subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = 32052427
API_HASH = "d9e14b1e99ac33e20d41479a47d2622f"
BOT_TOKEN = "8251863494:AAHDCtcDD-O9_VLHv0TCfi4qxUA5p7go8r4"

FORCE_CHANNEL = "chanaly_boot"
CHANNEL_LINK = "https://t.me/chanaly_boot"

app = Client(
    "video_downloader_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

def join_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 چۆنی چەناڵ بکە", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ دووبارە هەوڵ بدە", callback_data="check_join")]
    ])

async def is_joined(client, user_id):
    try:
        member = await client.get_chat_member(FORCE_CHANNEL, user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False

@app.on_message(filters.command("start"))
async def start(client, message):
    if not await is_joined(client, message.from_user.id):
        await message.reply(
            "⚠️ بۆ بەکارهێنانی بۆت پێویستە چۆنی چەناڵ بکەیت",
            reply_markup=join_buttons()
        )
        return

    await message.reply("👋 لینک بنێرە بۆ دابەزاندنی ڤیدیۆ")

@app.on_callback_query(filters.regex("check_join"))
async def check_join(client, query):
    if await is_joined(client, query.from_user.id):
        await query.message.edit("✅ دەتوانیت ئێستا لینک بنێریت")
    else:
        await query.answer("هێشتا چۆنی چەناڵ نەکردووە", show_alert=True)

@app.on_message(filters.text & ~filters.command(["start"]))
async def download_video(client, message):
    if not await is_joined(client, message.from_user.id):
        await message.reply(
            "⚠️ سەرەتا چۆنی چەناڵ بکە",
            reply_markup=join_buttons()
        )
        return

    url = message.text.strip()
    await message.reply("⏳ تکایە چاوەڕێ بکە...")

    try:
        file = f"video_{message.from_user.id}.mp4"
        subprocess.run(["yt-dlp", "-o", file, url], check=True)

        await message.reply_video(file)
        os.remove(file)

    except Exception as e:
        await message.reply(f"❌ هەڵە: {e}")

app.run()