import os
import re
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from yt_dlp import YoutubeDL

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = -1001234567890  # 👈 chat id ی جەناڵەکەت دابنێ
CHANNEL_LINK = "https://t.me/yourchannel"

bot = Bot(TOKEN)
dp = Dispatcher()

# ========== Force Join Check ==========
async def is_joined(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def join_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔔 جۆینی جەناڵ بکە", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ دووبارە هەوڵ بدە", callback_data="recheck")]
    ])

# ========== Start ==========
@dp.message(CommandStart())
async def start(msg: Message):
    if not await is_joined(msg.from_user.id):
        await msg.answer("🚫 بۆ بەکارهێنانی بوت پێویستە جۆینی جەناڵ بکەیت", reply_markup=join_kb())
        return
    await msg.answer("👋 بەخێربێیت\n\n🔗 لینک بنێرە بۆ دابەزاندنی ڤیدیۆ")

@dp.callback_query(F.data == "recheck")
async def recheck(call):
    if await is_joined(call.from_user.id):
        await call.message.edit_text("✅ دەتوانیت ئێستا لینک بنێریت")
    else:
        await call.answer("هێشتا جۆینت نەکردووە", show_alert=True)

# ========== Download ==========
def download_video(url):
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'best',
        'quiet': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

@dp.message(F.text.regexp(r'https?://'))
async def downloader(msg: Message):
    if not await is_joined(msg.from_user.id):
        await msg.answer("🚫 سەرەتا جۆینی جەناڵ بکە", reply_markup=join_kb())
        return

    await msg.answer("⏳ چاوەڕوان بە... دابەزاندن دەستپێکرد")

    try:
        loop = asyncio.get_event_loop()
        file = await loop.run_in_executor(None, download_video, msg.text)

        await msg.answer_video(video=open(file, 'rb'))
        os.remove(file)

    except Exception as e:
        await msg.answer("❌ هەڵە ڕوویدا")

# ========== Run ==========
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())