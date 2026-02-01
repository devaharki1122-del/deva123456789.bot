import logging
import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8251863494:AAHXSwJPCiEWCB-5E2nBc3gR0W7IiocUimk"
ADMIN_ID = 8186735286
CHANNELS = ["@chanaly_boot", "@team_988"]

logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher(bot)

# ------------------ KEYBOARDS ------------------

def force_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    for ch in CHANNELS:
        kb.add(InlineKeyboardButton(f"جوینی {ch}", url=f"https://t.me/{ch.replace('@','')}"))
    kb.add(InlineKeyboardButton("♻️ پشکنینەوە", callback_data="recheck"))
    return kb

def main_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📥 دابەزاندنی ڤیدیۆ", callback_data="down"),
        InlineKeyboardButton("🤖 AI", callback_data="ai"),
    )
    kb.add(
        InlineKeyboardButton("👑 ئەدمین پانیل", callback_data="admin"),
        InlineKeyboardButton("📩 پەیوەندی", callback_data="owner"),
    )
    return kb

# ------------------ FORCE JOIN ------------------

async def check_join(user_id):
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# ------------------ API DOWNLOAD ------------------

async def api_download(url):
    api = f"https://api.tiklydown.me/api/download?url={url}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api) as r:
            data = await r.json()
            return data["video"]

# ------------------ START ------------------

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    if not await check_join(msg.from_user.id):
        await msg.answer("🔒 تکایە جوینی کەناڵەکان بکە", reply_markup=force_kb())
        return

    await msg.answer(
        "🇭🇺 بەخێربێیت بۆ VVVIP BOT\n\nدووگمەکان بەکاربهێنە 👇",
        reply_markup=main_kb()
    )

# ------------------ RECHECK ------------------

@dp.callback_query_handler(lambda c: c.data == "recheck")
async def recheck(call: types.CallbackQuery):
    if await check_join(call.from_user.id):
        await call.message.edit_text("✅ ئێستا دەتوانیت بەکاربهێنیت", reply_markup=main_kb())
    else:
        await call.answer("هێشتا جوین نەکراوە ❌", show_alert=True)

# ------------------ CALLBACKS ------------------

@dp.callback_query_handler()
async def callbacks(call: types.CallbackQuery):

    if call.data == "owner":
        await call.message.answer("📩 @YourUsername")

    elif call.data == "ai":
        await call.message.answer("🤖 پرسیارەکەت بنووسە")

    elif call.data == "admin":
        if call.from_user.id == ADMIN_ID:
            await call.message.answer("👑 تۆ ئەدمینیت")
        else:
            await call.answer("تۆ ئەدمین نیت ❌", show_alert=True)

# ------------------ MESSAGE ------------------

@dp.message_handler()
async def handle(msg: types.Message):

    if not await check_join(msg.from_user.id):
        await msg.answer("🔒 سەرەتا جوینی کەناڵەکان بکە", reply_markup=force_kb())
        return

    text = msg.text

    if "http" in text:
        wait = await msg.answer("⏳ چاوەڕوان بە...")

        try:
            video = await api_download(text)
            await bot.send_video(msg.chat.id, video, reply_markup=main_kb())
        except:
            await msg.answer("❌ ئەم لینکە پشتگیری ناکرێت")

        await wait.delete()
        return

    # AI simple reply
    await msg.answer(
        f"🤖 AI وەڵام:\n{text}",
        reply_markup=main_kb()
    )

# ------------------ RUN ------------------

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)