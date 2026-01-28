import os
import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

# ====== ENV ======
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_1 = os.getenv("CHANNEL_1")  # https://t.me/xxx
CHANNEL_2 = os.getenv("CHANNEL_2")  # https://t.me/xxx
ADMIN_ID = int(os.getenv("ADMIN_ID"))
SUPPORT = os.getenv("SUPPORT")

# ====== BOT ======
app = Client("deva", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

users = {}

# ====== FORCE JOIN ======
async def force_join(client, message):
    try:
        await client.get_chat_member(CHANNEL_1, message.from_user.id)
        await client.get_chat_member(CHANNEL_2, message.from_user.id)
        return True
    except UserNotParticipant:
        await message.reply(
            "❌ تکایە سەرەتا جەناڵەکان join بکە",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 جەناڵ 1", url=CHANNEL_1)],
                [InlineKeyboardButton("📢 جەناڵ 2", url=CHANNEL_2)]
            ])
        )
        return False

# ====== START ======
@app.on_message(filters.command("start"))
async def start(client, message):
    if not await force_join(client, message):
        return

    await message.reply(
        "👋 سڵاو!\n\n"
        "🎥 ڤیدیۆ دابەزێنە\n"
        "📥 ڕۆژانە 5 ڤیدیۆ بۆ بەکارهێنەر\n\n"
        "🆘 پشتیوانی",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 Support", url=SUPPORT)]
        ])
    )

# ====== LIMIT SYSTEM ======
def can_download(user_id):
    today = datetime.date.today()
    if user_id not in users:
        users[user_id] = {"date": today, "count": 0}

    if users[user_id]["date"] != today:
        users[user_id] = {"date": today, "count": 0}

    return users[user_id]["count"] < 5

def add_download(user_id):
    users[user_id]["count"] += 1

# ====== VIDEO LINK ======
@app.on_message(filters.text & ~filters.command)
async def download(client, message):
    if not await force_join(client, message):
        return

    uid = message.from_user.id

    if uid != ADMIN_ID and not can_download(uid):
        await message.reply(
            "⚠️ سنوور تەواو بوو\n\n"
            "نامە بنێرە بۆ support بۆ زیادکردنی سنوور 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 Support", url=SUPPORT)]
            ])
        )
        return

    add_download(uid)

    await message.reply(
        "⏳ ڤیدیۆ دابەزێنرێت...\n\n"
        "⚙️ (ئەم نمونەیە، دەتوانیت yt-dlp زیاد بکەیت)"
    )

# ====== ADMIN PANEL ======
@app.on_message(filters.command("admin") & filters.user(ADMIN_ID))
async def admin(client, message):
    await message.reply(
        "👑 Admin Panel",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Users", callback_data="users")],
            [InlineKeyboardButton("🔄 Restart", callback_data="restart")]
        ])
    )

@app.on_callback_query(filters.regex("users"))
async def users_count(client, cb):
    await cb.message.edit(f"👥 Users: {len(users)}")

@app.on_callback_query(filters.regex("restart"))
async def restart(client, cb):
    await cb.message.edit("♻️ Restarting...")
    os.system("kill 1")

# ====== RUN ======
print("Bot started")
app.run()