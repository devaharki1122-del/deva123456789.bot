import logging
import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8251863494:AAFeoPstXFmg0pQTRCD2qJxDE1VfFGUG0Fc"
ADMIN_ID = 8186735286
CHANNELS = ["@chanaly_boot", "@team_988"]

logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher(bot)

# ---------------- KEYBOARDS ----------------

def force_kb():
    kb = InlineKeyboardMarkup()
    for ch in CHANNELS:
        kb.add(InlineKeyboardButton(f"جوینی {ch}", url=f"https://t.me/{ch.replace('@','')}"))
    kb.add(InlineKeyboardButton("♻️ پشکنینەوە", callback_data="recheck"))
    return kb

def main_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📥 دابەزاندن", callback_data="down"),
        InlineKeyboardButton("🤖 AI", callback_data="ai"),
    )
    kb.add(
        InlineKeyboardButton("👑 ئەدمین", callback_data="admin"),
        InlineKeyboardButton("📩 خاوەن بوت", callback_data="owner"),
    )
    return kb

# ---------------- FORCE JOIN ----------------

async def check_join(user_id):
    for ch in CHANNELS:
        try:
            m = await bot.get_chat_member(ch, user_id)
            if m.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# ---------------- UNIVERSAL DOWNLOADER ----------------

async def universal_download(url):
    api = f"https://save-api.xyz/api/download?url={url}"
    async with aiohttp.ClientSession() as s:
        async with s.get(api) as r:
            data = await r.json()
            return data["url"]

# ---------------- START ----------------

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    if not await check_join(msg.from_user.id):
        await msg.answer("🔒 تکایە جوینی کەناڵەکان بکە", reply_markup=force_kb())
        return

    await msg.answer(
        "🇭🇺 بەخێربێیت\nدووگمەکان بەکاربهێنە 👇",
        reply_markup=main_kb()
    )

# ---------------- RECHECK ----------------

@dp.callback_query_handler(lambda c: c.data == "recheck")
async def recheck(call: types.CallbackQuery):
    if await check_join(call.from_user.id):
        await call.message.edit_text("✅ ئێستا ئامادەیە", reply_markup=main_kb())
    else:
        await call.answer("هێشتا جوین نەکراوە ❌", show_alert=True)

# ---------------- CALLBACKS ----------------

@dp.callback_query_handler()
async def callbacks(call: types.CallbackQuery):
    if call.data == "owner":
        await call.message.answer("📩 @YourUsername")

    elif call.data == "admin":
        if call.from_user.id == ADMIN_ID:
            await call.message.answer("👑 تۆ ئەدمینیت")
        else:
            await call.answer("تۆ ئەدمین نیت ❌", show_alert=True)

    elif call.data == "ai":
        await call.message.answer("🤖 پرسیارەکەت بنووسە")

# ---------------- MESSAGE ----------------

@dp.message_handler()
async def handle(msg: types.Message):

    if not await check_join(msg.from_user.id):
        await msg.answer("🔒 سەرەتا جوین بکە", reply_markup=force_kb())
        return

    text = msg.text

    if "http" in text:
        wait = await msg.answer("⏳ چاوەڕوان بە...")

        try:
            video_url = await universal_download(text)
            await bot.send_video(msg.chat.id, video_url, reply_markup=main_kb())
        except:
            await msg.answer("❌ نەتوانرا دابەزێندرێت")

        await wait.delete()
        return

    await msg.answer(f"🤖 AI:\n{text}", reply_markup=main_kb())

# ---------------- RUN ----------------

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)