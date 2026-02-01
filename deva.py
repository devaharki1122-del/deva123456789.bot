import os
import subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

# ===== API =====
api_id = 32052427
api_hash = "d9e14b1e99ac33e20d41479a47d2622f"
bot_token = "8251863494:AAGs9DbPWxM3UE6y9-zi4T-Sk_MJIKBslsk"

# ===== CHANNEL INFO =====
FORCE_CHANNEL = -1002252176207
CHANNEL_LINK = "https://t.me/chanaly_boot"

app = Client(
    "video_downloader_bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

# ===== JOIN KEYBOARD =====
def join_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 جۆینی چەنەل", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ جۆینم کردووە", callback_data="check_join")]
    ])

# ===== CHECK JOIN =====
async def is_joined(client, user_id):
    try:
        member = await client.get_chat_member(FORCE_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except UserNotParticipant:
        return False
    except:
        return False

# ===== START =====
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await is_joined(client, message.from_user.id):
        await message.reply(
            "🚫 بۆ بەکارهێنانی بۆت، سەرەتا جۆینی چەنەل بکە",
            reply_markup=join_kb()
        )
        return

    await message.reply("👋 لینک بنێرە بۆ دابەزاندنی ڤیدیۆ 🎬")

# ===== RECHECK JOIN =====
@app.on_callback_query(filters.regex("check_join"))
async def check_join(client, cq):
    if await is_joined(client, cq.from_user.id):
        await cq.message.edit_text("✅ جۆینت کرد — لینک بنێرە")
    else:
        await cq.answer("هێشتا جۆینت نەکردووە", show_alert=True)

# ===== DOWNLOAD VIDEO =====
def download_video(url, user_id):
    filename = f"video_{user_id}.mp4"
    cmd = ["yt-dlp", "-o", filename, url]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return filename

# ===== HANDLE LINKS =====
@app.on_message(filters.private & filters.text)
async def handle_links(client, message):
    user_id = message.from_user.id

    if not await is_joined(client, user_id):
        await message.reply(
            "🚫 سەرەتا جۆینی چەنەل بکە",
            reply_markup=join_kb()
        )
        return

    url = message.text.strip()

    if "http" not in url:
        return

    wait = await message.reply("⏳ چاوەڕێ بکە... دابەزاندن دەستپێکرد")

    try:
        file_path = download_video(url, user_id)
        await message.reply_video(file_path)
        os.remove(file_path)
        await wait.delete()
    except Exception as e:
        await wait.edit(f"❌ هەڵە ڕوویدا\n{e}")

# ===== RUN =====
app.run()