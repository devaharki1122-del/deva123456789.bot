import os
import re
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

TOKEN = "8251863494:AAHkxXI_qSBYRjuHyKn2W0KkOlI7-P2qzu4"
CHANNELS = ["@chanaly_boot"]
ADMIN = 8186735286

bot = Bot(TOKEN)
dp = Dispatcher(bot)

# ---------------- AI Kurdish Reply ----------------
def ai_reply(text):
    return f"""🤖 AI:
تۆ ناردت:
{text}

ئەگەر ئەمە لینکەکە نیە، تکایە تەنها لینک بنێرە بۆ دابەزاندن 📥"""

# ---------------- Keyboards ----------------
def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📥 دابەزاندن", callback_data="download"),
        InlineKeyboardButton("📊 ئامار", callback_data="stats"),
    )
    kb.add(
        InlineKeyboardButton("ℹ️ دەربارەی بوت", callback_data="about"),
        InlineKeyboardButton("📩 پەیوەندی", url="https://t.me/Deva_harki"),
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


# ---------------- Force Join Check ----------------
async def check_join(user_id):
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True


# ---------------- Link Detect ----------------
def is_link(text):
    patterns = [
        r"tiktok\.com", r"vt\.tiktok\.com",
        r"instagram\.com",
        r"facebook\.com",
        r"youtu\.be", r"youtube\.com",
        r"twitter\.com", r"x\.com",
    ]
    return any(re.search(p, text) for p in patterns)


# ---------------- Fake Download ----------------
async def download_media(url):
    await asyncio.sleep(3)
    return "sample.mp4"


# ---------------- Start ----------------
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    ok = await check_join(msg.from_user.id)
    if not ok:
        await msg.answer(
            "🔒 تکایە سەرەتا جوینی کەناڵ بکە",
            reply_markup=force_join_kb(),
        )
        return

    await msg.answer(
        "🇭🇺 بەخێربێیت بۆ VVVVVIP AI Downloader Bot",
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


# ---------------- Menu Buttons ----------------
@dp.callback_query_handler(lambda c: c.data == "about")
async def about(call: types.CallbackQuery):
    await call.message.edit_text(
        "ℹ️ ئەم بوتە بۆ دابەزاندنی ڤیدیۆی TikTok, Instagram, Facebook, YouTube دروستکراوە.",
        reply_markup=main_menu(),
    )


@dp.callback_query_handler(lambda c: c.data == "stats")
async def stats(call: types.CallbackQuery):
    await call.answer("📊 ئامار بەردەست نیە", show_alert=True)


@dp.callback_query_handler(lambda c: c.data == "download")
async def download_btn(call: types.CallbackQuery):
    await call.message.edit_text(
        "📥 تکایە لینک بنێرە بۆ دابەزاندن",
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

    if is_link(text):
        wait = await msg.answer("⏳ لینکەکەت وەرگیرا، چاوەڕوان بە...")

        file_path = await download_media(text)
        size = os.path.getsize(file_path)

        if size < 50 * 1024 * 1024:
            await msg.answer_video(open(file_path, "rb"), reply_markup=main_menu())
        else:
            await msg.answer_document(open(file_path, "rb"), reply_markup=main_menu())

        await wait.delete()
    else:
        await msg.answer(ai_reply(text), reply_markup=main_menu())


if __name__ == "__main__":
    executor.start_polling(dp)