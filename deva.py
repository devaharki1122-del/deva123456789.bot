import os
import asyncio
import time
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# ========= CONFIG =========
BOT_TOKEN = "8251863494:AAHxYFCPXUg9h1AEigCEu7DqbXVTP9zJ8QU"
ADMIN_ID = 8186735286
FORCE_CHANNELS = ["@chanaly_boot"]

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

# ========= MEMORY =========
users_lang = {}
cooldown = {}
link_memory = {}
user_download_count = {}
legendary_users = {}
queue_list = []

# ========= LANGUAGE DETECT =========
def detect_lang(code):
    if not code: return "en"
    if code.startswith("ku"): return "ku"
    if code.startswith("ar"): return "ar"
    if code.startswith("tr"): return "tr"
    if code.startswith("fa"): return "fa"
    if code.startswith("de"): return "de"
    if code.startswith("fr"): return "fr"
    return "en"

# ========= TEXTS =========
TEXTS = {
    "start": {
        "ku": "👑 بەخێربێیت بۆ VVVVVVIP AI Downloader Bot",
        "en": "👑 Welcome to VVVVVVIP AI Downloader Bot",
        "ar": "👑 أهلاً بك في بوت التحميل الذكي",
        "tr": "👑 VIP AI indirici bota hoş geldiniz",
        "fa": "👑 به ربات دانلود AI خوش آمدید",
        "de": "👑 Willkommen beim VIP AI Downloader Bot",
        "fr": "👑 Bienvenue sur le bot AI Downloader VIP",
    },
    "force": {
        "ku": "🔒 تکایە سەرەتا جوینی کەناڵەکان بکە",
        "en": "🔒 Please join channels first",
        "ar": "🔒 يرجى الانضمام للقنوات أولاً",
        "tr": "🔒 Önce kanallara katılın",
        "fa": "🔒 ابتدا عضو کانال‌ها شوید",
        "de": "🔒 Bitte zuerst Kanälen beitreten",
        "fr": "🔒 Veuillez rejoindre les chaînes d'abord",
    },
    "snap": {
        "ku": "❌ لە سناپ دابەزاندن قەدەغەیە",
        "en": "❌ Snapchat download disabled",
        "ar": "❌ التحميل من سناب ممنوع",
        "tr": "❌ Snapchat indirilemez",
        "fa": "❌ دانلود از اسنپ غیرفعال است",
        "de": "❌ Snapchat nicht erlaubt",
        "fr": "❌ Snapchat désactivé",
    },
    "about": {
        "ku": "ℹ️ زانیاری بوت\nبوتی دابەزاندنی پیشەیی\n👑 @Deva_harki",
        "en": "ℹ️ Bot Information\nProfessional downloader bot\n👑 @Deva_harki",
        "ar": "ℹ️ معلومات البوت\nبوت تحميل احترافي\n👑 @Deva_harki",
        "tr": "ℹ️ Bot bilgisi\nProfesyonel indirici bot\n👑 @Deva_harki",
        "fa": "ℹ️ اطلاعات ربات\nربات دانلود حرفه‌ای\n👑 @Deva_harki",
        "de": "ℹ️ Bot Info\nProfessioneller Downloader Bot\n👑 @Deva_harki",
        "fr": "ℹ️ Infos Bot\nBot de téléchargement professionnel\n👑 @Deva_harki",
    },
}

# ========= KEYBOARD =========
def main_kb(lang):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("ℹ️ About", callback_data="about"),
        InlineKeyboardButton("📊 Stats", callback_data="stats"),
        InlineKeyboardButton("🎖 Rank", callback_data="rank"),
        InlineKeyboardButton("📩 Owner", url="https://t.me/Deva_harki"),
    )
    return kb

# ========= FORCE JOIN =========
async def check_force(user_id):
    for ch in FORCE_CHANNELS:
        try:
            member = await bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# ========= FAKE DOWNLOAD =========
async def fake_download():
    await asyncio.sleep(3)
    return "sample.mp4"  # دەتوانیت بگۆڕیت

# ========= START =========
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    lang = detect_lang(msg.from_user.language_code)
    users_lang[msg.from_user.id] = lang
    await msg.answer(TEXTS["start"][lang], reply_markup=main_kb(lang))

# ========= BUTTONS =========
@dp.callback_query_handler(lambda c: c.data == "about")
async def about(call: types.CallbackQuery):
    lang = users_lang.get(call.from_user.id, "en")
    await call.message.answer(TEXTS["about"][lang])

@dp.callback_query_handler(lambda c: c.data == "stats")
async def stats(call: types.CallbackQuery):
    count = user_download_count.get(call.from_user.id, 0)
    await call.message.answer(f"📊 Downloads: {count}")

@dp.callback_query_handler(lambda c: c.data == "rank")
async def rank(call: types.CallbackQuery):
    c = legendary_users.get(call.from_user.id, 0)
    badge = "Legendary" if c >= 50 else "Gold" if c >= 20 else "Silver" if c >= 10 else "New"
    await call.message.answer(f"🎖 Rank: {badge}")

# ========= HANDLE LINKS =========
@dp.message_handler(lambda m: m.text and "http" in m.text)
async def handle_link(msg: types.Message):
    user_id = msg.from_user.id
    lang = users_lang.get(user_id, "en")
    url = msg.text.strip()

    if not await check_force(user_id):
        await msg.answer(TEXTS["force"][lang])
        return

    if "snapchat" in url:
        await msg.answer(TEXTS["snap"][lang])
        return

    now = time.time()
    if user_id in cooldown and now - cooldown[user_id] < 6:
        return
    cooldown[user_id] = now

    queue_list.append(user_id)
    pos = len(queue_list)
    status = await msg.answer(f"🇭🇺 لینکەکەت وەرگیرا\n⏳ نوبەی تۆ: #{pos}")

    if url in link_memory:
        file_path = link_memory[url]
    else:
        file_path = await fake_download()
        link_memory[url] = file_path

    user_download_count[user_id] = user_download_count.get(user_id, 0) + 1
    legendary_users[user_id] = legendary_users.get(user_id, 0) + 1

    try:
        await msg.answer_video(open(file_path, "rb"), reply_markup=main_kb(lang))
    except:
        await msg.answer("⚠️ File not found. Change sample.mp4")

    await status.delete()
    await bot.send_message(ADMIN_ID, f"Download: {url}")
    queue_list.remove(user_id)

# ========= AI MODE =========
@dp.message_handler()
async def ai_mode(msg: types.Message):
    await msg.answer("🤖 AI Ready", reply_markup=main_kb("en"))

# ========= RUN =========
if __name__ == "__main__":
    executor.start_polling(dp)