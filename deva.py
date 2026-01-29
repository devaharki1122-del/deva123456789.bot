import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = "8251863494:AAHLJgGgXvK4ZRkzELq3lWVPS7U7Jb4jsLU"

ydl_opts = {
    "outtmpl": "downloads/%(title)s.%(ext)s",
    "format": "best[filesize_approx<2000M]/best",
    "noplaylist": True,
}

os.makedirs("downloads", exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("    ( 2GB)")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    msg = await update.message.reply_text("   ...")

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))

        file = os.listdir("downloads")[0]
        path = f"downloads/{file}"

        await update.message.reply_video(video=open(path, "rb"))
        os.remove(path)

    except Exception as e:
        await msg.edit_text(f" : {e}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    app.run_polling()

if __name__ == "__main__":
    main()