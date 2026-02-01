import os
import subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

api_id = 32052427
api_hash = "d9e14b1e99ac33e20d41479a47d2622f"
bot_token = "
8251863494:AAGWAWdEEmMLDr6qdTISSmXHgE8msGZdkUg"

# ===== Force Join بە @ =====
CHANNELS = ["@chanaly_boot", "@chanaly_boot"]

app = Client(
    "video_bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

# ===== دوگمەی جۆین =====
def join_kb():
    buttons = []
    for ch in CHANNELS:
        link = f"https://t.me/{ch.replace('@','')}"
        buttons.append([InlineKeyboardButton(f"🔔 جۆینی {ch}", url=link)])
    buttons.append([InlineKeyboardButton("✅ جۆینم کردووە", callback_data="check")])
    return InlineKeyboardMarkup(buttons)

# ===== چێککردنی جۆین =====
async def is_joined(client, user_id):
    for ch in CHANNELS:
        try:
            member = await client.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except UserNotParticipant:
            return False
        except:
            return False
    return True

# ===== start =====
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await is_joined(client, message.from_user.id):
        await message.reply(
            "🚫 سەرەتا جۆینی چەنەلەکان بکە",
            reply_markup=join_kb()
        )
        return

    await message.reply("👋 لینک بنێرە بۆ دابەزاندنی ڤیدیۆ 🎬")

# ===== دووبارە چێککردن =====
@app.on_callback_query(filters.regex("check"))
async def check(client, cq):
    if await is_joined(client, cq.from_user.id):
        await cq.message.edit_text("✅ جۆینت کرد — لینک بنێرە")
    else:
        await cq.answer("هێشتا جۆینت نەکردووە", show_alert=True)

# ===== دابەزاندن =====
def download_video(url, uid):
    name = f"{uid}.mp4"
    subprocess.run(["yt-dlp", "-o", name, url])
    return name

# ===== وەرگرتنی لینک =====
@app.on_message(filters.private & filters.text)
async def handle(client, message):
    if not await is_joined(client, message.from_user.id):
        await message.reply("🚫 سەرەتا جۆینی چەنەلەکان بکە", reply_markup=join_kb())
        return

    if "http" not in message.text:
        return

    wait = await message.reply("⏳ دابەزاندن دەستپێکرد...")
    file = download_video(message.text, message.from_user.id)

    await message.reply_video(file)
    os.remove(file)
    await wait.delete()

app.run()