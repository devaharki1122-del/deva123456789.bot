# -*- coding: utf-8 -*-
# ==================================================
#  TELEGRAM VIDEO / MP3 DOWNLOADER BOT (ONE FILE)
# ==================================================

import os
import time
import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= ENV ONLY =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

OWNER_ID = 8186735286
OWNER_USERNAME = "Deva_harki"

CHANNELS = ["team_988", "chanaly_boot"]  # Force Join channels
DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# ================= BOT =================
app = Client(
    "ai_downloader_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

USER_MODE = {}  # video | mp3

# ================= FORCE JOIN =================
async def check_join(client, user_id):
    """
    Check if user joined required channels.
    For testing, you can temporarily disable by returning True
    """
    try:
        for ch in CHANNELS:
            m = await client.get_chat_member(ch, user_id)
            if m.status == "left":
                return False
    except:
        return False
    return True

def join_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(" Join Channel", url=f"https://t.me/{c}")]
         for c in CHANNELS]
    )

# ================= BUTTONS =================
MAIN_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(" ", callback_data="mode_video"),
        InlineKeyboardButton(" MP3", callback_data="mode_mp3")
    ],
    [InlineKeyboardButton("    ", url=f"https://t.me/{OWNER_USERNAME}")]
])

ADMIN_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton(" Stats", callback_data="admin_stats")],
    [InlineKeyboardButton(" Owner", url=f"https://t.me/{OWNER_USERNAME}")]
])

# ================= DOWNLOAD FUNCTIONS =================
def download_video(url):
    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_PATH}/%(title)s.%(ext)s",
        "format": "mp4/best",
        "merge_output_format": "mp4",
        "quiet": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return info, ydl.prepare_filename(info)

def download_audio(url):
    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_PATH}/%(title)s.mp3",
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }],
        "quiet": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return info, f"{DOWNLOAD_PATH}/{info['title']}.mp3"

# ================= START COMMAND =================
@app.on_message(filters.command("start"))
async def start(client, msg):
    await client.send_message(
        OWNER_ID,
        f" New user\n {msg.from_user.id}"
    )

    if not await check_join(client, msg.from_user.id):
        return await msg.reply(
            "     ",
            reply_markup=join_keyboard()
        )

    USER_MODE[msg.from_user.id] = "video"

    kb = MAIN_KEYBOARD
    if msg.from_user.id == OWNER_ID:
        kb.inline_keyboard.append(
            [InlineKeyboardButton(" Admin", callback_data="admin")]
        )

    await msg.reply(" \n  ", reply_markup=kb)

# ================= CALLBACK QUERY =================
@app.on_callback_query()
async def callbacks(client, cb):
    uid = cb.from_user.id

    if cb.data == "mode_video":
        USER_MODE[uid] = "video"
        await cb.message.reply("  ")

    elif cb.data == "mode_mp3":
        USER_MODE[uid] = "mp3"
        await cb.message.reply(" MP3 ")

    elif cb.data == "admin" and uid == OWNER_ID:
        await cb.message.reply(" Admin Panel", reply_markup=ADMIN_KEYBOARD)

    elif cb.data == "admin_stats" and uid == OWNER_ID:
        await cb.message.reply(
            " Stats\n\n"
            " Bot Running\n"
            " Railway OK"
        )

    await cb.answer()

# ================= HANDLE LINKS =================
@app.on_message(filters.text & ~filters.command())
async def handle_link(client, msg):
    if not await check_join(client, msg.from_user.id):
        return await msg.reply(
            "    ",
            reply_markup=join_keyboard()
        )

    mode = USER_MODE.get(msg.from_user.id, "video")
    await msg.reply("   …")

    start_time = time.time()

    if mode == "mp3":
        info, file_path = await asyncio.to_thread(download_audio, msg.text)
        await msg.reply_audio(
            file_path,
            caption=f" {info.get('title')}\n @{OWNER_USERNAME}"
        )
    else:
        info, file_path = await asyncio.to_thread(download_video, msg.text)
        took = int(time.time() - start_time)
        await msg.reply_video(
            video=file_path,
            caption=(
                f" {info.get('title')}\n"
                f" {took} sec\n"
                f" @{OWNER_USERNAME}"
            )
        )

    if os.path.exists(file_path):
        os.remove(file_path)

# ================= RUN BOT =================
app.run()