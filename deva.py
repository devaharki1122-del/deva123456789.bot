import telebot
import subprocess
import os

TOKEN = "8251863494:AAHOcpnaLVubeeX-tNVEixtnr2jHkSG8fXQ"
bot = telebot.TeleBot(TOKEN)

CHANNEL = "@chanaly_boot"

def check_join(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status not in ["left", "kicked"]
    except:
        return False

def join_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("📢 جۆینی کەناڵ", url=f"https://t.me/{CHANNEL[1:]}")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
        "👋 بەخێربێیت\n\nلینک بنێرە بۆ دابەزاندنی ڤیدیۆ")

@bot.message_handler(func=lambda m: True)
def download(message):
    if not check_join(message.from_user.id):
        bot.send_message(message.chat.id,
            "❌ تکایە سەرەتا جۆینی کەناڵ بکە",
            reply_markup=join_markup())
        return

    url = message.text.strip()

    if "http" not in url:
        return

    msg = bot.send_message(message.chat.id, "⏳ چاوەڕوان بە...")

    filename = "video.mp4"

    cmd = [
        "yt-dlp",
        "-f", "mp4",
        "-o", filename,
        url
    ]

    try:
        subprocess.run(cmd, check=True)
        bot.send_video(message.chat.id, open(filename, "rb"))
        os.remove(filename)
        bot.delete_message(message.chat.id, msg.message_id)
    except:
        bot.edit_message_text("❌ نەتوانرا ڤیدیۆ دابەزێنرێت", message.chat.id, msg.message_id)

print("Bot running...")
bot.infinity_polling()