import asyncio
import time
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

BOT_TOKEN = "8251863494:AAF9FXWkEFguTEY1hsMdIoq72AQcyNSlsQU"
ADMIN_ID = 8186735286
FORCE_CHANNELS = ["@chanaly_boot"]

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

users_lang = {}
cooldown = {}
downloads = {}
queue = []

# ---------- TEXTS ----------
TEXTS = {
    "force": "🔒 تکایە سەرەتا جوینی کەناڵەکان بکە",
    "choose_lang": "🌍 تکایە زمان هەڵبژێرە",
    "snap": "❌ لە سناپ دابەزاندن قەدەغەیە",
}

# ---------- KEYBOARDS ----------
def lang_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🇭🇺 کوردی", callback_data="lang_ku"),
        InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
        InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
        InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
        InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
        InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de"),
        InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"),
    )
    return kb

def main_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("ℹ️ About", callback_data="about"),
        InlineKeyboardButton("📊 Stats", callback_data="stats"),
        InlineKeyboardButton("🎖 Rank", callback_data="rank"),
        InlineKeyboardButton("📩 Owner", url="https://t.me/Deva_harki"),
    )
    return kb

def admin_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("👥 Users", callback_data="a_users"),
        InlineKeyboardButton("📥 Downloads", callback_data="a_down"),
    )
    return kb

# ---------- FORCE JOIN ----------
async def check_force(user_id):
    for ch in FORCE_CHANNELS:
        try:
            m = await bot.get_chat_member(ch, user_id)
            if m.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# ---------- START ----------
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer(TEXTS["force"])

# ---------- LANGUAGE ----------
@dp.callback_query_handler(lambda c: c.data.startswith("lang_"))
async def set_lang(call: types.CallbackQuery):
    lang = call.data.split("_")[1]
    users_lang[call.from_user.id] = lang
    await call.message.answer("✅ Done", reply_markup=main_kb())

# ---------- ADMIN PANEL ----------
@dp.message_handler(commands=["admin"])
async def admin_panel(msg: types.Message):
    if msg.from_user.id == ADMIN_ID:
        await msg.answer("👑 Admin Panel", reply_markup=admin_kb())

@dp.callback_query_handler(lambda c: c.data == "a_users")
async def a_users(call: types.CallbackQuery):
    await call.message.answer(f"Users: {len(users_lang)}")

@dp.callback_query_handler(lambda c: c.data == "a_down")
async def a_down(call: types.CallbackQuery):
    await call.message.answer(f"Downloads: {len(downloads)}")

# ---------- HANDLE LINKS ----------
@dp.message_handler(lambda m: m.text and "http" in m.text)
async def handle_link(msg: types.Message):
    user = msg.from_user.id
    url = msg.text

    if not await check_force(user):
        await msg.answer(TEXTS["force"])
        return

    if user not in users_lang:
        await msg.answer(TEXTS["choose_lang"], reply_markup=lang_kb())
        return

    if "snapchat" in url:
        await msg.answer(TEXTS["snap"])
        return

    now = time.time()
    if user in cooldown and now - cooldown[user] < 5:
        return
    cooldown[user] = now

    queue.append(user)
    pos = len(queue)
    wait = await msg.answer(f"⏳ نوبەی تۆ: {pos}")

    await asyncio.sleep(3)

    downloads[url] = True
    await msg.answer("✅ Downloaded", reply_markup=main_kb())

    await wait.delete()
    queue.remove(user)

# ---------- AI ----------
@dp.message_handler()
async def ai(msg: types.Message):
    await msg.answer("🤖 AI Ready", reply_markup=main_kb())

# ---------- RUN ----------
if __name__ == "__main__":
    executor.start_polling(dp)