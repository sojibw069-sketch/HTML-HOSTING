import logging
import json
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# --- কনফিগারেশন ---
API_TOKEN = '8810638360:AAFaBcQPNfs5_VsDWMEXhD6IOz0KxFPIoeo'
ADMIN_ID = 7275133182
WEB_SERVER_URL = "http://mahfuzahmedchy.com/host.php"
SECRET_TOKEN = "CXOFB_SECURE_TOKEN_2026"
CHANNELS = ["@CYBER_X_OF_BANGLADESHH", "@Cyber_x_of_bangladesh1"]

# --- ডাটাবেস ---
DB_FILE = "database.json"
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {"users": {}, "config": {"bonus": 2, "refer": 4}}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

db = load_db()
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# --- কীবোর্ডস ---
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("🚀 Host File"))
    kb.row(KeyboardButton("💰 Balance"), KeyboardButton("🎁 Bonus"))
    kb.row(KeyboardButton("👥 Refer"), KeyboardButton("📊 Stats"))
    return kb

def join_kb():
    mk = InlineKeyboardMarkup(row_width=1)
    for ch in CHANNELS:
        mk.add(InlineKeyboardButton(f"📢 Join {ch}", url=f"https://t.me/{ch[1:]}"))
    mk.add(InlineKeyboardButton("✅ Verify Membership", callback_data="check_v"))
    return mk

# মেম্বারশিপ চেক
async def is_joined(uid):
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(ch, uid)
            if member.status in ["left", "kicked"]: return False
        except: return False
    return True

# --- হ্যান্ডলারস ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    uid = str(message.from_id)
    if uid not in db["users"]:
        db["users"][uid] = {"points": 0, "claimed": False}
        args = message.get_args()
        if args and args.isdigit() and args in db["users"] and args != uid:
            db["users"][args]["points"] += db["config"]["refer"]
            try: await bot.send_message(args, f"🎉 Refer Success! +{db['config']['refer']} Pts")
            except: pass
        save_db(db)
    await message.answer("👋 <b>Welcome!</b> Join our channels to start.", reply_markup=join_kb())

@dp.callback_query_handler(text="check_v")
async def verify(call: types.CallbackQuery):
    if await is_joined(call.from_user.id):
        await call.message.answer("✨ <b>Verified!</b> Menu Unlocked.", reply_markup=main_menu())
        await call.answer()
    else:
        await call.answer("❌ Please join all channels first!", show_alert=True)

@dp.message_handler(lambda m: m.text in ["🚀 Host File", "💰 Balance", "🎁 Bonus", "👥 Refer", "📊 Stats"])
async def handle_menu(message: types.Message):
    if not await is_joined(message.from_id):
        return await message.answer("⚠️ Join Channels First!", reply_markup=join_kb())
    
    uid = str(message.from_id)
    txt = message.text

    if txt == "💰 Balance":
        await message.answer(f"💳 <b>Balance:</b> {db['users'][uid]['points']} Points")
    elif txt == "🎁 Bonus":
        if db["users"][uid].get("claimed"):
            await message.answer("❌ Already claimed today!")
        else:
            db["users"][uid]["points"] += db["config"]["bonus"]
            db["users"][uid]["claimed"] = True
            save_db(db)
            await message.answer(f"🎁 Bonus +{db['config']['bonus']} Points added!")
    elif txt == "👥 Refer":
        me = await bot.get_me()
        await message.answer(f"👥 <b>Referral Link:</b>\n<code>https://t.me/{me.username}?start={uid}</code>")
    elif txt == "📊 Stats":
        await message.answer(f"📊 <b>Total Users:</b> {len(db['users'])}\n🌐 <b>Server:</b> Online")
    elif txt == "🚀 Host File":
        await message.answer("💎 <b>CXOFB Hosting</b>\n━━━━━━━━━━━━\n📥 এখন আপনার ফাইল বা ফটোটি পাঠান।")

@dp.message_handler(content_types=['document', 'photo'])
async def handle_upload(message: types.Message):
    if not await is_joined(message.from_id): return
    uid = str(message.from_id)
    if db["users"][uid]["points"] < 1:
        return await message.answer("⚠️ Need 1 point.")

    file_obj = message.document if message.document else message.photo[-1]
    f_info = await bot.get_file(file_obj.file_id)
    f_name = getattr(file_obj, 'file_name', f"img_{uid}.jpg")

    if f_name.endswith('.php'): return await message.answer("🚫 PHP Restricted.")

    status_msg = await message.answer("⌛ <b>Hosting...</b>")
    t_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{f_info.file_path}"
    
    # হেডার যুক্ত করা হয়েছে যাতে সার্ভার ব্লক না করে
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    payload = {'token': SECRET_TOKEN, 'file_url': t_url, 'name': f_name}

    try:
        req = requests.post(WEB_SERVER_URL, data=payload, headers=headers, timeout=30)
        res = req.json()
        if res.get("status") == "success":
            db["users"][uid]["points"] -= 1
            save_db(db)
            await status_msg.edit_text(f"✅ <b>Successfully Hosted!</b>\n\n🌐 <b>URL:</b> {res['url']}", disable_web_page_preview=True)
        else:
            await status_msg.edit_text(f"❌ Error: {res.get('message')}")
    except Exception as e:
        await status_msg.edit_text(f"❌ <b>Server Error!</b>\nResponse: {str(e)[:50]}")

# --- অ্যাডমিন কমান্ডস ---
@dp.message_handler(commands=['broadcast'])
async def broadcast(message: types.Message):
    if message.from_id != ADMIN_ID: return
    txt = message.get_args()
    count = 0
    for u in db["users"]:
        try:
            await bot.send_message(u, f"📢 <b>Broadcast:</b>\n\n{txt}")
            count += 1
        except: pass
    await message.answer(f"✅ Sent to {count} users.")

@dp.message_handler(commands=['bonus', 'refer'])
async def edit_pts(message: types.Message):
    if message.from_id != ADMIN_ID: return
    val = message.get_args()
    if val.isdigit():
        key = message.get_command()[1:]
        db["config"][key] = int(val)
        save_db(db)
        await message.answer(f"✅ {key} points set to {val}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
