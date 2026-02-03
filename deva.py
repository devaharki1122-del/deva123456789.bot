import os
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= CONFIG =================
API_ID = 32052427
API_HASH = "d9e14b1e99ac33e20d41479a47d2622f"
BOT_TOKEN = "8251863494:AAFzs3f7JVjIgpTrWgdMsoQWFDkG7Vjax48"  # <-- تۆکن لێرە زیاد بکە
OWNER_ID = 8186735286

FORCE_JOIN = ["@team_988", "@chanaly_boot"]

# زمانەکان
LANGS = {
    "ku": "🤖 دەست خۆش! ڤیدیۆی TikTok داونلود بکە.",
    "en": "🤖 Welcome! Download a TikTok video.",
    "ar": "🤖 أهلا! قم بتنزيل فيديو TikTok.",
    "fa": "🤖 خوش آمدید! ویدیو TikTok دانلود کنید.",
    "tr": "🤖 Hoşgeldiniz! TikTok videosu indir.",
    "ru": "🤖 Добро пожаловать! Скачать видео TikTok.",
    "de": "🤖 Willkommen! TikTok-Video herunterladen.",
    "fr": "🤖 Bienvenue! Télécharger une vidéo TikTok.",
    "es": "🤖 ¡Bienvenido! Descarga un video de TikTok.",
    "it": "🤖 Benvenuto! Scarica un video TikTok."
}

# ==========================================

app = Client("tiktok_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

ADMINS = [OWNER_ID]

# --- Start Command ---
@app.on_message(filters.private & filters.command("start"))
async def start_cmd(client, message):
    text = LANGS.get("ku", "🤖 Welcome!")
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Download TikTok", callback_data="download")],
        [InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin")],
        [InlineKeyboardButton("🎵 Download Audio", callback_data="audio")]
    ])
    await message.reply_text(text, reply_markup=buttons)

# --- Callback Buttons ---
@app.on_callback_query()
async def button_cb(client, callback_query):
    data = callback_query.data
    if data == "download":
        await callback_query.message.edit_text("📎 لینک ڤیدیۆ TikTok بنێرە")
    elif data == "audio":
        await callback_query.message.edit_text("🎵 لینک ڤیدیۆ TikTok بنێرە بۆ داونلودی دەنگ")
    elif data == "admin":
        if callback_query.from_user.id in ADMINS:
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Users Stats", callback_data="stats")],
                [InlineKeyboardButton("📝 Broadcast", callback_data="broadcast")]
            ])
            await callback_query.message.edit_text("⚙️ خۆشحاڵم بەخێر بێیت بە Admin Panel", reply_markup=buttons)
        else:
            await callback_query.message.edit_text("❌ تۆ Admin نەیت!")

# --- TikTok Download ---
@app.on_message(filters.private & filters.text)
async def tiktok_download(client, message):
    url = message.text
    if "tiktok.com" in url:
        await message.reply_text("⏳ داونلود دەکرێت...")
        try:
            # download video unofficial
            video_url = url.replace("www", "vm")  # TikTok unofficial endpoint
            resp = requests.get(video_url)
            filename = f"{message.from_user.id}.mp4"
            with open(filename, "wb") as f:
                f.write(resp.content)
            await message.reply_video(filename, caption="🤖 AI TikTok Downloader")
            os.remove(filename)

            # Notify Owner
            await client.send_message(OWNER_ID, f"👤 User {message.from_user.id} downloaded a video:\n{url}")
        except Exception as e:
            await message.reply_text(f"❌ هەڵە ڕوویدا: {e}")

# --- Audio Download ---
@app.on_message(filters.private & filters.text)
async def audio_download(client, message):
    url = message.text
    if "tiktok.com" in url:
        await message.reply_text("🎵 داونلودی دەنگ دەکرێت...")
        try:
            video_url = url.replace("www", "vm")
            resp = requests.get(video_url)
            filename = f"{message.from_user.id}.mp3"
            with open(filename, "wb") as f:
                f.write(resp.content)  # simple, real audio extraction needs moviepy/ffmpeg
            await message.reply_audio(filename, caption="🤖 AI TikTok Audio")
            os.remove(filename)
            await client.send_message(OWNER_ID, f"👤 User {message.from_user.id} downloaded audio:\n{url}")
        except Exception as e:
            await message.reply_text(f"❌ هەڵە ڕوویدا: {e}")

# --- Run Bot ---
app.run()