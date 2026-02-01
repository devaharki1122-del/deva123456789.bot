import re, cv2, numpy as np
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from openai import OpenAI

# ===== دانەری سەرەکی =====
TOKEN = "8251863494:AAHanRgtqE4QXBtepGfEmYyuNeZFHN5dfXg"
ADMIN_ID = 8186735286
OPENAI_KEY = "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"

# ===== چەناڵە زۆربەزۆرەکان (ناکرێن لاببرێن) =====
FORCED_CHANNEL_1 = "chanaly_boot"
FORCED_CHANNEL_2 = "team_988"

bot = telebot.TeleBot(TOKEN)
client = OpenAI(api_key=OPENAI_KEY)

vip_users = set()
memory = {}
maker_steps = {}

# ===== دووگمەکان =====
def منیو():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💎 نامە بنێرە تا ببیتە VIP", url="https://t.me/Deva_harki"),
        InlineKeyboardButton("🤖 دروستکردنی بوتی خۆت", callback_data="make_bot")
    )
    return kb

def دووگمەی_چەناڵ():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📢 جۆینی چەناڵی یەکەم", url=f"https://t.me/{FORCED_CHANNEL_1}"),
        InlineKeyboardButton("📢 جۆینی چەناڵی دووەم", url=f"https://t.me/{FORCED_CHANNEL_2}")
    )
    return kb

# ===== پشکنینی جۆین =====
def پشکنینی_جۆین(uid):
    try:
        c1 = bot.get_chat_member(f"@{FORCED_CHANNEL_1}", uid).status
        c2 = bot.get_chat_member(f"@{FORCED_CHANNEL_2}", uid).status
        return c1 in ["member","creator","administrator"] and c2 in ["member","creator","administrator"]
    except:
        return False

# ===== /start =====
@bot.message_handler(commands=['start'])
def دەستپێ(msg):
    uid = msg.from_user.id
    name = msg.from_user.first_name
    username = msg.from_user.username or "None"

    زانیاری = f"""👤 بەکارهێنەری نوێ

ناو: {name}
یوزەرنەیم: @{username}
ID: {uid}
"""
    m = bot.send_message(ADMIN_ID, زانیاری)
    try: bot.pin_chat_message(ADMIN_ID, m.message_id)
    except: pass

    if not پشکنینی_جۆین(uid):
        bot.send_message(msg.chat.id, "🔒 تکایە سەرەتا ئەم دوو چەناڵە جۆین بکە 👇", reply_markup=دووگمەی_چەناڵ())
        return

    if uid in vip_users:
        bot.send_message(msg.chat.id, "💎 بەخێربێیت بۆ بەشی VIP AI", reply_markup=منیو())
    else:
        bot.send_message(msg.chat.id, "🔹 تۆ لە بەشی ئاسایی\nبۆ AI نامە بنێرە بۆ @Deva_harki", reply_markup=منیو())

# ===== ناسینی لینک =====
@bot.message_handler(func=lambda m: m.text and "http" in m.text)
def ناسینی_لینک(msg):
    url = re.search(r'(https?://\S+)', msg.text).group(1)
    if "tiktok" in url: t="🎵 لینکی TikTok ـە"
    elif "youtube" in url: t="▶️ لینکی YouTube ـە"
    elif "instagram" in url: t="📸 لینکی Instagram ـە"
    else: t="🔗 لینكە"
    bot.reply_to(msg, t)

# ===== جوانکردنی وێنە =====
@bot.message_handler(content_types=['photo'])
def جوانکردنی_وێنە(msg):
    file = bot.get_file(msg.photo[-1].file_id)
    img = bot.download_file(file.file_path)

    with open("in.jpg","wb") as f: f.write(img)

    image = cv2.imread("in.jpg")
    image = cv2.fastNlMeansDenoisingColored(image,None,10,10,7,21)
    kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    image = cv2.filter2D(image,-1,kernel)
    image = cv2.convertScaleAbs(image, alpha=1.2, beta=20)
    cv2.imwrite("out.jpg", image)

    bot.send_photo(msg.chat.id, open("out.jpg","rb"), caption="✨ وێنەکەت جوان کرا | تەڵخی لابرا | دەموچا ساف کرا")

# ===== AI بۆ VIP =====
def وەڵامی_AI(uid, text):
    if uid not in memory:
        memory[uid] = [{"role":"system","content":"AI زیرەکی کوردی. بابەتی مەترسیدار قبوڵ ناکات."}]
    memory[uid].append({"role":"user","content":text})

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=memory[uid]
    )
    reply = res.choices[0].message.content
    memory[uid].append({"role":"assistant","content":reply})
    return reply

@bot.message_handler(func=lambda m: True)
def چات(msg):
    if msg.text.startswith("/"): return
    uid = msg.from_user.id

    if uid not in vip_users:
        bot.send_message(msg.chat.id,"🔹 تۆ VIP نیت. نامە بنێرە بۆ @Deva_harki")
        return

    bot.send_chat_action(msg.chat.id,"typing")
    bot.send_message(msg.chat.id, وەڵامی_AI(uid, msg.text))

# ===== دروستکردنی بوت لە ناو بوت =====
@bot.callback_query_handler(func=lambda c: c.data=="make_bot")
def دروستکردن(call):
    maker_steps[call.from_user.id] = "token"
    bot.send_message(call.message.chat.id, "🔑 تکایە TOKEN ـی بوتەکەت بنێرە")

@bot.message_handler(func=lambda m: m.from_user.id in maker_steps)
def پرۆسەی_دروستکردن(msg):
    step = maker_steps[msg.from_user.id]

    if step == "token":
        maker_steps[msg.from_user.id] = {"token":msg.text,"step":"channel"}
        bot.send_message(msg.chat.id,"📢 ناوی چەناڵەکەت بنێرە")

    elif isinstance(step,dict):
        token = step["token"]
        user_channel = msg.text
        admin = msg.from_user.id

        code = f'''
import telebot

TOKEN="{token}"
ADMIN_ID={admin}

FORCED1="chanaly_boot"
FORCED2="team_988"
USER_CHANNEL="{user_channel}"

bot=telebot.TeleBot(TOKEN)

print("Bot Ready")
'''
        with open("new_bot.py","w") as f: f.write(code)

        bot.send_document(msg.chat.id, open("new_bot.py","rb"), caption="✅ بوتەکەت ئامادەیە بۆ Railway")
        del maker_steps[msg.from_user.id]

print("Bot Running...")
bot.infinity_polling()