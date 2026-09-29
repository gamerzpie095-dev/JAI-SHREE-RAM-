BOT_TOKEN = os.getenv("BOT_TOKEN")
print(f"Token loaded: {BOT_TOKEN}") # ye line add kar
if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN nahi mila! Render Environment me add karo")
    import os, json, telebot, qrcode, io
from flask import Flask
import threading
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5735299456
SUPPORT_ID = 6014936495
BOT_USERNAME = "Dubeyfflikesbot"
UPI_ID = "dubeyadarsh17@fam" # Yaha apna UPI ID daal

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Live"

def load_json(f):
    try:
        with open(f,'r') as x: return json.load(x)
    except: return {}
def save_json(f,d):
    with open(f,'w') as x: json.dump(x,d)

user_data = {}

PACKAGES = {
    "100 Likes - Rs 40": 40,
    "200 Likes - Rs 75": 75,
    "500 Likes - Rs 150": 150,
    "1000 Likes - Rs 280": 280
}

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = str(message.from_user.id)
    args = message.text.split()
    if len(args) > 1:
        referrer = args[1]
        if referrer!= user_id:
            data = load_json('referrals.json')
            if referrer not in data: data[referrer] = []
            if user_id not in data[referrer]:
                data[referrer].append(user_id)
                save_json('referrals.json', data)
                count = len(data[referrer])
                if count % 5 == 0:
                    likes = (count // 5) * 100
                    try:
                        bot.send_message(ADMIN_ID, f"🔥 5 REFERRAL COMPLETE\nWinner ID: {referrer}\nUsername: @{message.from_user.username}\nMention: [{message.from_user.first_name}](tg://user?id={message.from_user.id})\nTotal: {count}\nReward: {likes} Likes", parse_mode="Markdown")
                    except: pass
    if user_id not in load_json('referrals.json'):
        d = load_json('referrals.json')
        d[user_id] = []
        save_json('referrals.json', d)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛒 Order Likes", "👥 Referral")
    markup.add("📞 Support")
    bot.send_message(message.chat.id, f"Welcome {message.from_user.first_name}! Name auto le liya.", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🛒 Order Likes")
def order_start(message):
    user_data[message.from_user.id] = {}
    bot.send_message(message.chat.id, "FF UID bhejo:")
    bot.register_next_step_handler(message, get_uid)

def get_uid(message):
    user_data[message.from_user.id]['uid'] = message.text
    user_data[message.from_user.id]['name'] = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    bot.send_message(message.chat.id, "Region bhejo:")
    bot.register_next_step_handler(message, get_region)

def get_region(message):
    user_data[message.from_user.id]['region'] = message.text
    markup = types.InlineKeyboardMarkup()
    for p in PACKAGES:
        markup.add(types.InlineKeyboardButton(p, callback_data=f"pack_{p}"))
    bot.send_message(message.chat.id, "Package select karo:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("pack_"))
def pack_select(call):
    pack = call.data.replace("pack_","")
    uid = call.from_user.id
    user_data[uid]['pack'] = pack
    price = PACKAGES[pack]
    user_data[uid]['price'] = price

    # AUTO QR GENERATE FROM TEXT
    upi_link = f"upi://pay?pa={UPI_ID}&pn=FFLikes&am={price}&cu=INR"
    qr = qrcode.make(upi_link)
    bio = io.BytesIO()
    qr.save(bio, 'PNG')
    bio.seek(0)

    bot.send_photo(call.message.chat.id, bio, caption=f"UID: {user_data[uid]['uid']}\nPack: {pack}\nPrice: Rs {price}\nUPI: {UPI_ID}\n\nIs QR ko scan karke pay karo.")

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Paid", callback_data="paid"), types.InlineKeyboardButton("❌ Cancel", callback_data="cancel"))
    bot.send_message(call.message.chat.id, "Pay ho gaya?", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data in ["paid","cancel"])
def pay_handle(call):
    if call.data == "cancel":
        bot.send_message(call.message.chat.id, "Cancel ho gaya")
        return
    info = user_data.get(call.from_user.id, {})
    bot.send_message(ADMIN_ID, f"💰 PAID\nFrom: {info.get('name')} ID:{call.from_user.id}\nUID:{info.get('uid')}\nRegion:{info.get('region')}\nPack:{info.get('pack')} Rs {info.get('price')}")
    bot.send_message(call.message.chat.id, "Paid bhej diya admin ko ✅")

@bot.message_handler(commands=['referral'])
@bot.message_handler(func=lambda m: m.text == "👥 Referral")
def ref_cmd(message):
    user_id = str(message.from_user.id)
    data = load_json('referrals.json')
    count = len(data.get(user_id, []))
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    bot.send_message(message.chat.id, f"👥 Referral\nLink: {link}\nTotal: {count}\nEvery 5 = 100 Likes")

@bot.message_handler(commands=['support'])
@bot.message_handler(func=lambda m: m.text == "📞 Support")
def sup_cmd(message):
    bot.send_message(message.chat.id, "Problem bhejo:")
    bot.register_next_step_handler(message, lambda m: (bot.send_message(SUPPORT_ID, f"SUPPORT From @{m.from_user.username} {m.from_user.id}: {m.text}"), bot.send_message(m.chat.id, "Support bhej diya")))

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
