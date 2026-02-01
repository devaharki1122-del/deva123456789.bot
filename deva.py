import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

BOT_TOKEN = "8251863494:AAGBmbamw2BVtCY1AiNq0Q1PafEPywZ-Dhc"
ADMIN_ID = 8186735286
FORCE_CHANNEL = "@chanaly_boot"

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

users_lang = {}

# ---------- KEYBOARDS ----------
def force_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📢 جوینی کەناڵ", url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}"),
        InlineKeyboardButton("✅ من جوینم کرد", callback_data="check_join")
    )
    return kb

def lang_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🇭🇺 کوردی", callback_data="lang_ku"),
        InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
    )
    return kb

def home_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("ℹ️ About", callback_data="about"),
        InlineKeyboardButton("📊 Stats", callback_data="stats"),
        InlineKeyboardButton("🎖 Rank", callback_data="rank"),
        InlineKeyboardButton("📩 Owner", url="https://t.me/Deva_harki"),
    )
    return kb

# ---------- FORCE JOIN CHECK ----------
async def is_joined(user_id):
    member = await bot.get_chat_member(FORCE_CHANNEL, user_id)
    return member.status not in ["left", "kicked"]

# ---------- START ----------
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer(
        "🔒 تکایە سەرەتا جوینی کەناڵ بکە",
        reply_markup=force_kb()
    )

# ---------- CHECK JOIN BUTTON ----------
@dp.callback_query_handler(lambda c: c.data == "check_join")
async def check_join(call: types.CallbackQuery):
    try:
        if await is_joined(call.from_user.id):
            await call.message.answer("🌍 زمان هەڵبژێرە", reply_markup=lang_kb())
        else:
            await call.answer("هێشتا جوینت نەکردووە", show_alert=True)
    except:
        await call.answer("بوت admin نیە لە کەناڵ", show_alert=True)

# ---------- SET LANGUAGE ----------
@dp.callback_query_handler(lambda c: c.data.startswith("lang_"))
async def set_lang(call: types.CallbackQuery):
    users_lang[call.from_user.id] = call.data.split("_")[1]
    await call.message.answer("🏠 سەرەکی", reply_markup=home_kb())

# ---------- HOME BUTTONS ----------
@dp.callback_query_handler(lambda c: c.data in ["about", "stats", "rank"])
async def menu(call: types.CallbackQuery):
    if call.data == "about":
        await call.message.answer("ℹ️ Professional downloader bot\n👑 @Deva_harki")
    elif call.data == "stats":
        await call.message.answer("📊 Downloads: 0")
    elif call.data == "rank":
        await call.message.answer("🎖 Rank: New")

# ---------- AI MODE ----------
@dp.message_handler()
async def ai_mode(msg: types.Message):
    await msg.answer("🤖 AI Ready", reply_markup=home_kb())

# ---------- RUN ----------
if __name__ == "__main__":
    executor.start_polling(dp)