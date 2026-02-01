import os
import re
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from playwright.async_api import async_playwright

TOKEN = "8251863494:AAH9aaBBHzUXrWku1XFCSKVSCthYuwWft34"
CHANNELS = ["@chanaly_boot"]  # change
OWNER = "https://t.me/Deva_harki"

bot = Bot(TOKEN)
dp = Dispatcher(bot)

# ---------------- Keyboards ----------------
def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📥 دابەزاندن", callback_data="download"),
        InlineKeyboardButton("ℹ️ زانیاری بوت", callback_data="about"),
    )
    kb.add(
        InlineKeyboardButton("📩 نامە بۆ خاوەن بوت", url=OWNER),
    )
    return kb


def force_join_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    for ch in CHANNELS:
        kb.add(
            InlineKeyboardButton(f"جوینی {ch}", url=f"https://t.me/{ch.replace('@','')}")
        )
    kb.add(InlineKeyboardButton("✅ من جوینم کرد", callback_data="recheck"))
    return kb


# ---------------- Force Join ----------------
async def check_join(user_id):
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True


# ---------------- Snapchat Block ----------------
def is_snap(text):
    return "snapchat.com" in text or "snap.com" in text


# ---------------- Link Detect ----------------
def is_link(text):
    return "http" in text


# ---------------- AI Reply ----------------
def ai_reply(text):
    return f"""🤖 AI:
تۆ ناردت:
{text}

تکایە تەنها لینک بنێرە بۆ دابەزاندن 📥"""


# ---------------- Playwright Download ----------------
async def download_media(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(5000)

        video_url = await page.evaluate("""
        () => {
            const v = document.querySelector('video');
            return v ? v.src : null;
        }
        """)

        if not video_url:
            await browser.close()
            return None

        file_path = "video.mp4"

        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as resp:
                with open(file_path, "wb") as f:
                    f.write(await resp.read())

        await browser.close()
        return file_path


# ---------------- Start ----------------
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    ok = await check_join(msg.from_user.id)
    if not ok:
        await msg.answer("🔒 سەرەتا جوینی کەناڵ بکە", reply_markup=force_join_kb())
        return

    await msg.answer(
        "🇭🇺 بەخێربێیت\nتەنها لینک بنێرە بۆ دابەزاندن",
        reply_markup=main_menu(),
    )


# ---------------- Recheck ----------------
@dp.callback_query_handler(lambda c: c.data == "recheck")
async def recheck(call: types.CallbackQuery):
    ok = await check_join(call.from_user.id)
    if ok:
        await call.message.edit_text("✅ ئێستا دەتوانیت بەکاربهێنیت", reply_markup=main_menu())
    else:
        await call.answer("هێشتا جوین نەکراوە ❌", show_alert=True)


# ---------------- About ----------------
@dp.callback_query_handler(lambda c: c.data == "about")
async def about(call: types.CallbackQuery):
    await call.message.edit_text(
        "ℹ️ ئەم بوتە بۆ دابەزاندنی TikTok, Instagram, Facebook, YouTube دروستکراوە.",
        reply_markup=main_menu(),
    )


@dp.callback_query_handler(lambda c: c.data == "download")
async def download_btn(call: types.CallbackQuery):
    await call.message.edit_text(
        "📥 لینک بنێرە بۆ دابەزاندن",
        reply_markup=main_menu(),
    )


# ---------------- Message Handler ----------------
@dp.message_handler()
async def handle(msg: types.Message):
    text = msg.text or ""

    ok = await check_join(msg.from_user.id)
    if not ok:
        await msg.answer("🔒 سەرەتا جوینی کەناڵ بکە", reply_markup=force_join_kb())
        return

    if is_snap(text):
        await msg.answer(
            "ببورە، بە فەرمانی @Deva_harki ناتوانم لە Snapchat دابەزێنم 🇭🇺"
        )
        return

    if is_link(text):
        wait = await msg.answer(
            "🇭🇺 لینکەکەت وەرگیرا\n⏳ چاوەڕوان بە..."
        )

        file_path = await download_media(text)

        if not file_path:
            await wait.edit_text("❌ نەتوانرا ڤیدیۆ بدۆزرێتەوە")
            return

        size = os.path.getsize(file_path)

        if size < 50 * 1024 * 1024:
            await msg.answer_video(open(file_path, "rb"), reply_markup=main_menu())
        else:
            await msg.answer_document(open(file_path, "rb"), reply_markup=main_menu())

        await wait.delete()
        return

    await msg.answer(ai_reply(text), reply_markup=main_menu())


if __name__ == "__main__":
    executor.start_polling(dp)