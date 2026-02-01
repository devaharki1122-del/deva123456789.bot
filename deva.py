import os
import replicate
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY")
ADMIN_ID = 8186735286

CHANNELS = ["@chanaly_boot", "@team_988"]

replicate_client = replicate.Client(api_token=REPLICATE_API_KEY)

keyboard = [
    ["🖼 جوانکردنی وێنە"],
    ["🎬 جوانکردنی ڤیدیۆ"]
]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def force_join(update, context):
    user_id = update.effective_user.id
    for ch in CHANNELS:
        member = await context.bot.get_chat_member(ch, user_id)
        if member.status in ["left", "kicked"]:
            await update.message.reply_text(
                f"تکایە سەرەتا بچۆ ناو {ch} پاشان دوبارە هەوڵبدە."
            )
            return False
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ok = await force_join(update, context)
    if not ok:
        return
    await update.message.reply_text("🤖 AI Enhancer Bot بەخێربێیت", reply_markup=markup)


async def enhance_image(file_url):
    output = replicate_client.run(
        "nightmareai/real-esrgan",
        input={
            "image": file_url,
            "scale": 4,
            "face_enhance": True
        }
    )
    return output


async def enhance_video(file_url):
    output = replicate_client.run(
        "nightmareai/real-esrgan",
        input={
            "image": file_url,
            "scale": 4
        }
    )
    return output


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ok = await force_join(update, context)
    if not ok:
        return

    await context.bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    url = file.file_path

    await update.message.reply_text("⏳ وێنەکەت AI جوان دەکرێت...")

    result = await enhance_image(url)

    await update.message.reply_photo(photo=result)


async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ok = await force_join(update, context)
    if not ok:
        return

    video = update.message.video
    file = await context.bot.get_file(video.file_id)
    url = file.file_path

    await update.message.reply_text("⏳ ڤیدیۆ AI جوان دەکرێت...")

    result = await enhance_video(url)

    await update.message.reply_video(video=result)


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
app.add_handler(MessageHandler(filters.VIDEO, video_handler))

app.run_polling()