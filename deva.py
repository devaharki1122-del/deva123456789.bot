import telebot
import aiohttp
import asyncio

TOKEN = "8251863494:AAFEtDIe8Gj-zdB4DrlXmErwfbUSEhaMZpc"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

CHANNELS = ["@chanaly_boot"]   # forci join

# ============ Force Join Check ============
async def is_joined(user_id):
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

def join_buttons():
    markup = telebot.types.InlineKeyboardMarkup()
    for ch in CHANNELS:
        markup.add(telebot.types.InlineKeyboardButton("📢 جۆینی کەناڵ", url=f"https://t.me/{ch[1:]}"))
    markup.add(telebot.types.InlineKeyboardButton("✅ دووبارە هەوڵ بدە", callback_data="check"))
    return markup

# ============ URL Expander ============
async def expand_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, allow_redirects=True) as resp:
            return str(resp.url)

# ============ Universal Downloader ============
async def universal_download(url):
    api = f"https://saveapi.me/api/v1/download?url={url}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api) as resp:
            data = await resp.json()
            if data.get("success"):
                return data["data"]["url"]
            return None

# ============ Start ============
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🌍 هەڵبژاردنی زمان")
    bot.send_message(message.chat.id,
        "👋 بەخێربێیت بۆ Universal Video Downloader Bot\n\n"
        "📥 لینک بنێرە بۆ دابەزاندنی ڤیدیۆ",
        reply_markup=markup)

# ============ Handle Messages ============
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    asyncio.run(process(message))

async def process(message):
    user_id = message.from_user.id

    if not await is_joined(user_id):
        await bot.send_message(
            message.chat.id,
            "❌ تکایە سەرەتا جۆینی کەناڵ بکە",
            reply_markup=join_buttons()
        )
        return

    text = message.text.strip()

    if text.startswith("http"):
        msg = await bot.send_message(message.chat.id, "⏳ تکایە چاوەڕوان بە...")

        real = await expand_url(text)
        video = await universal_download(real)

        if video:
            await bot.send_video(message.chat.id, video)
            await bot.delete_message(message.chat.id, msg.message_id)
        else:
            await bot.edit_message_text("❌ نەتوانرا ڤیدیۆ دابەزێنرێت", message.chat.id, msg.message_id)

# ============ Run ============
print("Bot Running...")
bot.infinity_polling()