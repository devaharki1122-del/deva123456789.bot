# -*- coding: utf-8 -*-
import os
import telebot
import requests
from PIL import Image, ImageEnhance
from io import BytesIO
from openai import OpenAI

TOKEN = "8251863494:AAE97rTPyw-hyQk5hYndd7f1Sa9zgM1Ar80"
OPENAI_KEY = "
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"

bot = telebot.TeleBot(TOKEN)
client = OpenAI(api_key=OPENAI_KEY)

CHANNEL_1 = "@chanaly_boot"
CHANNEL_2 = "@team_988"

ADMIN_ID = 123456789  # ئایدی خۆت دابنێ

# ---------- فەنکشنی دڵنیابوون لە جۆین ----------
def check_join(user_id):
    try:
        c1 = bot.get_chat_member(CHANNEL_1, user_id)
        c2 = bot.get_chat_member(CHANNEL_2, user_id)
        return c1.status != "left" and c2.status != "left"
    except:
        return False

# ---------- ستارت ----------
@bot.message_handler(commands=['start'])
def start(msg):
    if not check_join(msg.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("جۆین ١", url=f"https://t.me/{CHANNEL_1[1:]}"),
            telebot.types.InlineKeyboardButton("جۆین ٢", url=f"https://t.me/{CHANNEL_2[1:]}")
        )
        markup.add(telebot.types.InlineKeyboardButton("دووبارە هەوڵبدە", callback_data="check"))
        bot.send_message(msg.chat.id, "تکایە سەرەتا جۆین بکە 👇", reply_markup=markup)
        return

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🤖 AI", "🖼 وێنە جوانکرد")
    markup.add("⬇️ داونلۆد ڤیدیۆ")

    bot.send_message(msg.chat.id,
    "👋 بەخێربێیت بۆ بوتەکەمان\n"
    "هەر لینکێک بنێرە بۆ داونلۆد 🎬\n"
    "یان دووگمەی خوارەوە بەکاربهێنە 👇",
    reply_markup=markup)

# ---------- AI ----------
@bot.message_handler(func=lambda m: m.text == "🤖 AI")
def ai_mode(msg):
    bot.send_message(msg.chat.id, "پرسیارەکەت بنێرە 🤖")

@bot.message_handler(func=lambda m: True, content_types=['text'])
def ai_chat(msg):
    if msg.text.startswith("http"):
        download_video(msg)
        return
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": msg.text}]
        )
        bot.send_message(msg.chat.id, response.choices[0].message.content)
    except:
        pass

# ---------- جوانکردنی وێنە ----------
@bot.message_handler(func=lambda m: m.text == "🖼 وێنە جوانکرد")
def img_start(msg):
    bot.send_message(msg.chat.id, "وێنەکە بنێرە 📸")

@bot.message_handler(content_types=['photo'])
def enhance_photo(msg):
    file_info = bot.get_file(msg.photo[-1].file_id)
    downloaded = bot.download_file(file_info.file_path)
    image = Image.open(BytesIO(downloaded))

    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)

    bio = BytesIO()
    bio.name = 'enhanced.jpg'
    image.save(bio, 'JPEG')
    bio.seek(0)

    bot.send_photo(msg.chat.id, bio, caption="وێنەکەت جوانکرا ✨")

# ---------- داونلۆد ڤیدیۆ ----------
def download_video(msg):
    url = msg.text
    api = f"https://api.tiklydown.me/api/download?url={url}"
    try:
        r = requests.get(api).json()
        video = r['video']['noWatermark']
        bot.send_video(msg.chat.id, video, caption="دانلۆد کرا ✅")
    except:
        bot.send_message(msg.chat.id, "لینکەکە پشتگیری ناکرێت")

@bot.message_handler(func=lambda m: m.text == "⬇️ داونلۆد ڤیدیۆ")
def how_download(msg):
    bot.send_message(msg.chat.id, "تەنها لینکێکی TikTok / Insta / YouTube بنێرە")

# ---------- ئەدمین پانێڵ ----------
@bot.message_handler(commands=['admin'])
def admin_panel(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    bot.send_message(msg.chat.id, "ئەدمین پانێڵ:\n/send broadcast")

@bot.message_handler(commands=['send'])
def broadcast(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    text = msg.text.replace("/send ", "")
    for user in []:
        try:
            bot.send_message(user, text)
        except:
            pass

print("Bot Running...")
bot.infinity_polling()