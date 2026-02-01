import asyncio
import time
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

BOT_TOKEN = "8251863494:AAGkoAom8yb7JKSo2k6Vm4Yp3VLwWtCk-0k"
ADMIN_ID = 8186735286
FORCE_CHANNELS = ["@chanaly_boot"]

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

users_lang = {}
queue = []
cooldown = {}

# ---------- TEXTS ----------
def t(text_ku, text_en):
    return {"ku": text_ku, "en": text_en}

TEXTS = {
    "force": t("🔒 تکایە جوینی کەناڵ بکە", "🔒 Join channel first"),
    "choose": t("🌍 زمان هەڵبژێرە", "🌍 Choose language"),
    "home": t("🏠 سەرەکی", "🏠 Home"),
    "about": t("ℹ️ زانیاری بوت", "ℹ️ About bot"),
    "stats": t("📊 ئامار", "📊 Stats"),
    "rank": t("🎖 پلە", "🎖 Rank"),
    "owner": t("📩 ناردن بۆ خاوەن", "📩 Contact owner"),
    "snap": t("❌ لە سناپ قەدەغەیە", "❌ Snapchat disabled"),
}

# ---------- KEYBOARDS ----------
def lang_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🇭🇺 کوردی", callback_data="lang_ku"),
        InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
    )
    return kb

def home_kb(lang):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(TEXTS["about"][lang], callback_data="about"),
        InlineKeyboardButton(TEXTS["stats"][lang], callback_data="stats"),
        InlineKeyboardButton(TEXTS["rank"][lang], callback_data="rank"),
        InlineKeyboardButton(TEXTS["owner"][lang], url="https://t.me/Deva_harki"),
    )
    return kb

def admin_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("👑 Admin Stats", callback_data="admin_stats"))
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
    await msg.answer(TEXTS["force"]["ku"])

# ---------- LANGUAGE ----------
@dp.callback_query_handler(lambda c: c.data.startswith("lang_"))
async def set_lang(call: types.CallbackQuery):
    lang = call.data.split("_")[1]
    users_lang[call.from_user.id] = lang
    await call.message.answer("✅", reply_markup=home_kb(lang))

# ---------- ADMIN ----------
@dp.message_handler(commands=["admin"])
async def admin(msg: types.Message):
    if msg.from_user.id == ADMIN_ID:
        await msg.answer("Admin Panel", reply_markup=admin_kb())

@dp.callback_query_handler(lambda c: c.data == "admin_stats")
async def admin_stats(call: types.CallbackQuery):
    await call.message.answer(f"Users: {len(users_lang)}")

# ---------- BUTTONS ----------
@dp.callback_query_handler(lambda c: c.data in ["about","stats","rank"])
async def buttons(call: types.CallbackQuery):
    lang = users_lang.get(call.from_user.id, "ku")
    if call.data == "about":
        await call.message.answer("Professional downloader bot\n@Deva_harki")
    elif call.data == "stats":
        await call.message.answer("📊 0")
    elif call.data == "rank":
        await call.message.answer("🎖 New")

# ---------- LINKS ----------
@dp.message_handler(lambda m: m.text and "http" in m.text)
async def links(msg: types.Message):
    user = msg.from_user.id
    lang = users_lang.get(user, "ku")

    if not await check_force(user):
        await msg.answer(TEXTS["force"][lang])
        return

    if user not in users_lang:
        await msg.answer(TEXTS["choose"]["ku"], reply_markup=lang_kb())
        return

    if "snapchat" in msg.text:
        await msg.answer(TEXTS["snap"][lang])
        return

    if user in cooldown and time.time() - cooldown[user] < 5:
        return
    cooldown[user] = time.time()

    queue.append(user)
    pos = len(queue)
    wait = await msg.answer(f"⏳ #{pos}")

    await asyncio.sleep(3)

    await msg.answer("✅ Done", reply_markup=home_kb(lang))
    await wait.delete()
    queue.remove(user)

# ---------- AI ----------
@dp.message_handler()
async def ai(msg: types.Message):
    lang = users_lang.get(msg.from_user.id, "ku")
    await msg.answer("🤖 AI", reply_markup=home_kb(lang))

# ---------- RUN ----------
if __name__ == "__main__":
    executor.start_polling(dp)