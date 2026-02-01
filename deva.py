import os
import re
import cv2
import numpy as np
import requests
from yt_dlp import YoutubeDL
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

TOKEN = "8251863494:AAFFw_Hn4ddynxq7hvql4JVHetENhvi0Dfk"
OPENAI_KEY = "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"

FORCE_CHANNELS = ["@chanaly_boot", "@team_988"]

client = OpenAI(api_key=OPENAI_KEY)

# ---------- Helpers ----------

def join_buttons():
    buttons = [[InlineKeyboardButton("📢 جۆینی جەناڵ", url=f"https://t.me/{ch[1:]}")] for ch in FORCE_CHANNELS]
    return InlineKeyboardMarkup(buttons)

async def check_join(user_id, bot):
    for ch in FORCE_CHANNELS:
        member = await bot.get_chat_member(ch, user_id)
        if member.status in ["left", "kicked"]:
            return False
    return True

def enhance_image(path):
    img = cv2.imread(path)
    img = cv2.detailEnhance(img, sigma_s=10, sigma_r=0.15)
    img = cv2.GaussianBlur(img, (0,0), 1.5)
    cv2.imwrite("enhanced.jpg", img)
    return "enhanced.jpg"

def download_video(url):
    ydl_opts = {'outtmpl': 'video.%(ext)s'}
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for f in os.listdir():
        if f.startswith("video."):
            return f

def detect_link(text):
    if "tiktok" in text: return "TikTok"
    if "instagram" in text: return "Instagram"
    if "youtube" in text: return "YouTube"
    return "Link"

# ---------- Handlers ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update.effective_user.id, context.bot):
        await update.message.reply_text(
            "🔒 تکایە سەرەتا جۆینی جەناڵەکان بکە",
            reply_markup=join_buttons()
        )
        return

    keyboard = [
        [InlineKeyboardButton("🤖 AI قسە بکە", callback_data="ai")],
        [InlineKeyboardButton("🖼 وێنە جوان بکە", callback_data="img")],
    ]
    await update.message.reply_text(
        "👋 بەخێربێیت\nهەموو شتەکان بۆت کراون ✨",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if re.search(r'http', text):
        site = detect_link(text)
        await update.message.reply_text(f"🔗 لینکی {site} ـە\n⏬ داونلۆد دەستی پێکرد...")
        file = download_video(text)
        await update.message.reply_video(video=open(file, 'rb'))
        return

    # AI reply
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": text}]
    )
    await update.message.reply_text(response.choices[0].message.content)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    await photo.download_to_drive("input.jpg")
    out = enhance_image("input.jpg")
    await update.message.reply_photo(photo=open(out, 'rb'))

# ---------- Run ----------

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

app.run_polling()