import telebot
from telebot.types import *
import random
import yt_dlp
import os

TOKEN = "TOKEN_LERA_DANێ"
ADMIN_ID = 123456789
OWNER = "@Deva_harki"

CHANNEL_1 = "@channel1"
CHANNEL_2 = "@channel2"

bot = telebot.TeleBot(TOKEN)

EMOJIS = ["🔥","❤️","😍","😂","😎","🤖","⚡","💎","🚀","🎉","🌈","🧠","👑","✨","🥰","🫶","💖","💫","🎯","📩","🔮"]

def e500():
    return "".join(random.choices(EMOJIS, k=500))

def forced_join(user_id):
    try:
        bot.get_chat_member(CHANNEL_1, user_id)
        bot.get_chat_member(CHANNEL_2, user_id)
        return True
    except:
        return False

def join_buttons():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🔗 چەنالی یەکەم", url=f"https://t.me/{CHANNEL_1.replace('@','')}"),
        InlineKeyboardButton("🔗 چەنالی دووەم", url=f"https://t.me/{CHANNEL_2.replace('@','')}")
    )
    kb.add(InlineKeyboardButton("✅ پشکنین", callback_data="check_join"))
    return kb

def main_buttons():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("⬇️ داونلۆدی ڤیدیۆ", callback_data="download"),
        InlineKeyboardButton("📩 نامە بۆ خاوەن بوت", callback_data="owner")
    )
    kb.add(
        InlineKeyboardButton("⚙️ ئەدمین پانێڵ", callback_data="admin")
    )
    return kb

def admin_panel():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📊 ئامار", callback_data="stats"),
        InlineKeyboardButton("📢 ناردنی نامە بۆ هەموو", callback_data="broadcast")
    )
    kb.add(
        InlineKeyboardButton("🔒 گۆڕینی چەنال", callback_data="channels"),
        InlineKeyboardButton("🔙 گەڕانەوە", callback_data="back")
    )
    return kb

@bot.message_handler(commands=["start"])
def start(message):
    if not forced_join(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "🔒 تکایە سەرەتا جۆین بکە بۆ چەنالەکان\n👇",
            reply_markup=join_buttons()
        )
        return

    bot.send_message(
        message.chat.id,
        "🤖✨ بەخێربێیت بۆ بوتی زێرەک\n⬇️ لینک بنێرە بۆ داونلۆد",
        reply_markup=main_buttons()
    )

@bot.callback_query_handler(func=lambda c: c.data=="check_join")
def check(c):
    if forced_join(c.from_user.id):
        bot.edit_message_text(
            "✅ باشە! ئێستا لینک بنێرە 😎",
            c.message.chat.id,
            c.message.message_id,
            reply_markup=main_buttons()
        )
    else:
        bot.answer_callback_query(c.id, "❌ هێشتا جۆینت نەکردووە", show_alert=True)

@bot.callback_query_handler(func=lambda c: c.data=="owner")
def owner_msg(c):
    bot.send_message(
        OWNER,
        f"📩 نامەی نوێ\n\n{e500()}"
    )
    bot.answer_callback_query(c.id, "✅ نێردرا", show_alert=True)

@bot.callback_query_handler(func=lambda c: c.data=="admin")
def admin(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "⛔ تۆ ئەدمین نیت", show_alert=True)
        return
    bot.edit_message_text(
        "⚙️ ئەدمین پانێڵ",
        c.message.chat.id,
        c.message.message_id,
        reply_markup=admin_panel()
    )

@bot.callback_query_handler(func=lambda c: c.data=="back")
def back(c):
    bot.edit_message_text(
        "🤖 سەرەکی",
        c.message.chat.id,
        c.message.message_id,
        reply_markup=main_buttons()
    )

@bot.message_handler(func=lambda m: m.text.startswith("http"))
def download(m):
    bot.send_message(m.chat.id, "⬇️ داونلۆد دەستپێکرا...")
    ydl_opts = {
        'outtmpl': 'video.mp4',
        'format': 'mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([m.text])

    bot.send_video(
        m.chat.id,
        open("video.mp4","rb"),
        caption="❤️🔥 لایک = ❤️\n👁 ڤیوو = 👁\n💬 کۆمێنت = 💬\n🔁 شێر = 🔁"
    )
    os.remove("video.mp4")

bot.infinity_polling()