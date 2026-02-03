import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from playwright.async_api import async_playwright
import ffmpeg
import random

# ---------------- زانیاری محیطی
API_TOKEN = os.getenv("API_TOKEN")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")

# ---------------- Force Join کانالەکان
CHANNELS = ["@team_988", "@chanaly_bootid"]

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ---------------- هەموو متنی کوردی
KU = {
    "welcome": "👋 سڵاو! تکایە ڤیدیۆ TikTok بنێرە بۆ داونلۆد",
    "download": "⬇️ داونلۆد",
    "info": "ℹ️ زانیاری",
    "join_required": "⚠️ تکایە پێویستە پێش بەکارهێنانی بوت سەبارەت بە کانالەکان join بکەیت!",
    "send_url": "📎 تکایە ڤیدیۆ URL بنێرە",
    "downloading": "⏳ داونلۆد دەکرێت...",
    "error": "❌ هەڵە ڕوویدا:",
    "bot_info": "🤖 من بوتێکی TikTok Downloader ـەم\n💡 تایبەتمەندیەکان:\n- Force Join دوو کانال\n- TikTok داونلۆد\n- زانیاری و Stats\n- Admin Alerts\n- AI زێرەک"
}

# ---------------- دووگمەکان
def main_buttons():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(KU["download"], callback_data="download"),
        InlineKeyboardButton(KU["info"], callback_data="info")
    )
    return kb

# ---------------- TikTok Downloader + Stats
async def download_tiktok(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        video_url = await page.eval_on_selector("video", "el => el.src")
        filename = f"/tmp/tiktok_{int(asyncio.time.time())}.mp4"
        ffmpeg.input(video_url).output(filename, c="copy").run(overwrite_output=True)
        # Stats simulation
        stats = {
            "views": random.randint(1000,100000),
            "likes": random.randint(100,5000),
            "shares": random.randint(10,500),
            "comments": random.randint(0,200)
        }
        await browser.close()
        return filename, stats

# ---------------- Force Join Check
async def check_channels(user_id):
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# ---------------- Commands
@dp.message(Command(commands=["start"]))
async def start(message: types.Message):
    joined = await check_channels(message.from_user.id)
    if not joined:
        await message.reply(KU["join_required"])
        return
    await message.reply(KU["welcome"], reply_markup=main_buttons())

# ---------------- Handle TikTok URLs
@dp.message()
async def handle_message(message: types.Message):
    joined = await check_channels(message.from_user.id)
    if not joined:
        await message.reply(KU["join_required"])
        return

    if "tiktok.com" in message.text:
        await message.reply(KU["downloading"])
        try:
            file_path, stats = await download_tiktok(message.text)
            await bot.send_video(message.chat.id, open(file_path, "rb"))
            os.remove(file_path)
            # Admin Alert
            await bot.send_message(ADMIN_USERNAME,
                                   f"📥 نوێترین داونلۆد لەلایەن @{message.from_user.username}\nURL: {message.text}\n💡 Stats: {stats}")
            # Stats بۆ بەکارهێنەر
            await message.reply(f"📊 ڤیدیۆ Stats:\n👁 Views: {stats['views']}\n❤️ Likes: {stats['likes']}\n🔄 Shares: {stats['shares']}\n💬 Comments: {stats['comments']}")
            # AI reply simulation
            await message.reply(f"🤖 زێرەک: ئەم ڤیدیۆیە باشە و داونلۆد کرا 🚀")
        except Exception as e:
            await message.reply(f"{KU['error']} {e}")

# ---------------- Handle Buttons (Download / Info)
@dp.callback_query()
async def handle_buttons(query: types.CallbackQuery):
    if query.data == "download":
        await query.message.answer(KU["send_url"])
    elif query.data == "info":
        await query.message.answer(KU["bot_info"])

# ---------------- Run
if __name__ == "__main__":
    asyncio.run(dp.start_polling())