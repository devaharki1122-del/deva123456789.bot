import os
import sqlite3
from datetime import date
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

# ========================
# ENV (Railway Variables)
# ========================
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

CHANNELS = [
    os.getenv("CHANNEL_1"),
    os.getenv("CHANNEL_2")
]

SUPPORT = "https://t.me/Deva_harki"

# ========================
# DB
# ========================
db = sqlite3.connect("db.sqlite", check_same_thread=False)
cur = db.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
cur.execute("CREATE TABLE IF NOT EXISTS vip (id INTEGER PRIMARY KEY)")
cur.execute("CREATE TABLE IF NOT EXISTS downloads (id INTEGER, day TEXT, count INTEGER)")
db.commit()

# ========================
app = Client(
    "bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

# ========================
# Helpers
# ========================
def is_admin(uid):
    return uid == ADMIN_ID

def is_vip(uid):
    cur.execute("SELECT id FROM vip WHERE id=?", (uid,))
    return cur.fetchone() is not None

def add_user(uid):
    cur.execute("INSERT OR IGNORE INTO users VALUES (?)", (uid,))
    db.commit()

def get_limit(uid):
    return 100 if is_vip(uid) else 5

def get_today(uid):
    today = str(date.today())
    cur.execute("SELECT count FROM downloads WHERE id=? AND day=?", (uid, today))
    row = cur.fetchone()
    return row[0] if row else 0

def add_download(uid):
    today = str(date.today())
    cur.execute("SELECT count FROM downloads WHERE id=? AND day=?", (uid, today))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE downloads SET count=count+1 WHERE id=? AND day=?", (uid, today))
    else:
        cur.execute("INSERT INTO downloads VALUES (?,?,1)", (uid, today))
    db.commit()

def check_join(client, uid):
    for ch in CHANNELS:
        try:
            client.get_chat_member(ch, uid)
        except:
            return False
    return True

# ========================
# START
# ========================
@app.on_message(filters.private & filters.command("start"))
def start(client, m):
    add_user(m.from_user.id)

    if not check_join(client, m.from_user.id):
        m.reply(
            "❗ تکایە سەرەتا ئەندام ببە لە جەناڵەکان 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("جەناڵ 1", url="https://t.me/chanaly_boot")],
                [InlineKeyboardButton("جەناڵ 2", url="https://t.me/team_988")],
                [InlineKeyboardButton("✅ پشکنین", callback_data="check")]
            ])
        )
        return

    m.reply(
        "🎥 بەخێربێیت بۆ بوتی داونلۆدی ڤیدیۆ\n\n"
        "🔗 لینک بنێرە بۆ داونلۆد",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 پەیوەندی بە دیڤە", url=SUPPORT)]
        ])
    )

# ========================
# CHECK JOIN
# ========================
@app.on_callback_query(filters.regex("check"))
def chk(client, q):
    if check_join(client, q.from_user.id):
        q.message.edit("✅ سوپاس، ئێستا دەتوانیت لینک بنێریت")
    else:
        q.answer("هێشتا ئەندام نەبوویت!", show_alert=True)

# ========================
# DOWNLOAD
# ========================
@app.on_message(filters.private & filters.text)
def download(client, m):
    uid = m.from_user.id
    add_user(uid)

    if m.text.startswith("/"):
        return

    if not check_join(client, uid):
        m.reply("❗ تکایە سەرەتا ئەندام ببە لە جەناڵەکان")
        return

    limit = get_limit(uid)
    today = get_today(uid)

    if today >= limit:
        m.reply(
            "❌ سنووری ڕۆژانەت تەواو بوو\n"
            "بۆ 100 ڤیدیۆ / ڕۆژ نامە بۆ دیڤە بنێرە 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 نامە بۆ دیڤە", url=SUPPORT)]
            ])
        )
        return

    msg = m.reply("⏳ داونلۆد دەکرێت...")

    try:
        ydl_opts = {
            "outtmpl": "video.mp4",
            "format": "mp4",
            "quiet": True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([m.text])

        client.send_video(uid, "video.mp4")
        add_download(uid)
        msg.delete()
        os.remove("video.mp4")

    except Exception as e:
        msg.edit("❌ هەڵە ڕوویدا، لینکێکی تر تاقی بکەوە")

# ========================
# ADMIN PANEL
# ========================
@app.on_message(filters.private & filters.command("admin"))
def admin(client, m):
    if not is_admin(m.from_user.id):
        return

    m.reply(
        "🎛 پانێلی ئەدمین",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐ VIP زیاد بکە", callback_data="addvip")],
            [InlineKeyboardButton("➖ VIP لاببە", callback_data="rmvip")],
            [InlineKeyboardButton("📊 ئامار", callback_data="stats")],
            [InlineKeyboardButton("❌ داخستن", callback_data="close")]
        ])
    )

@app.on_callback_query(filters.regex("addvip"))
def addvip(client, q):
    q.message.reply("ID بنێرە بۆ VIP کردن")
    q.message.stop_propagation()

@app.on_callback_query(filters.regex("rmvip"))
def rmvip(client, q):
    q.message.reply("ID بنێرە بۆ لابردنی VIP")
    q.message.stop_propagation()

@app.on_callback_query(filters.regex("stats"))
def stats(client, q):
    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM vip")
    vips = cur.fetchone()[0]
    q.message.edit(f"👥 بەکارهێنەران: {users}\n⭐ VIP: {vips}")

@app.on_callback_query(filters.regex("close"))
def close(client, q):
    q.message.delete()

# ========================
app.run()