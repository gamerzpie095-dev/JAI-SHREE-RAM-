import os, json, threading, io
import telebot
from telebot import types
from flask import Flask
import qrcode

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5735299456
SUPPORT_ID = 6014936495
UPI_ID = "dubeyadarsh17@fam"
BOT_USERNAME = "Dubeyfflikebot"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
@app.route('/')
def home(): return "JAI SHREE RAM - Bot Live"

def load_json(f):
    try:
        with open(f,'r') as x: return json.load(x)
    except: return {}
def save_json(f,d):
    with open(f,'w') as x: json.dump(x,d)

PACKAGES = {
    "100 LIKES 35 RS(TRUST)": 35,
    "1.5K LIKES 150 RS": 150,
    "3K LIKES 300 RS": 300,
    "5K LIKES 475 RS": 475,
    "10K LIKES 950 RS": 950,
    "20K LIKES 1900 RS": 1900
}

user_data = {}
MAIN_MARKUP = types.ReplyKeyboardMarkup(resize_keyboard=True)
MAIN_MARKUP.add("🛒 Order", "👥 Referral", "📞 Support")

def show_main_menu(chat_id, text):
    bot.send_message(chat_id, text, reply_markup=MAIN_MARKUP)

@bot.message_handler(commands=['start'])
def start(m):
    user_id = str(m.from_user.id)
    username = m.from_user.username or m.from_user.first_name

    # Referral Logic
    args = m.text.split()
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
                    try:
                        bot.send_message(ADMIN_ID, f"🔥 REFERRAL COMPLETE 🔥\nYe username ka banda hai: @{username} (ID: {referrer}) ne 5 referral complete kiya hai. Total: {count}")
                        bot.send_message(int(referrer), f"🎉 5 Referral Complete! 100 Likes Free milega!")
                    except: pass

    bot.send_message(m.chat.id, f"JAI SHREE RAM 🙏 {username}\n\nApni Free Fire UID bhejo:", reply_markup=MAIN_MARKUP)
    bot.register_next_step_handler(m, get_uid)

def get_uid(m):
    if m.text in ["🛒 Order", "👥 Referral", "📞 Support"]:
        handle_menu(m)
        return
    user_data[m.from_user.id] = {"username": m.from_user.username or m.from_user.first_name, "uid": m.text}
    bot.send_message(m.chat.id, "Region bhejo (Ex: India):", reply_markup=MAIN_MARKUP)
    bot.register_next_step_handler(m, get_region)

def get_region(m):
    if m.text in ["🛒 Order", "👥 Referral", "📞 Support"]:
        handle_menu(m)
        return
    user_data[m.from_user.id]['region'] = m.text
    markup = types.InlineKeyboardMarkup(row_width=1)
    for pkg, price in PACKAGES.items():
        markup.add(types.InlineKeyboardButton(f"{pkg} - {price} RS", callback_data=f"pkg_{price}_{pkg}"))
    bot.send_message(m.chat.id, f"UID: {user_data[m.from_user.id]['uid']}\nRegion: {m.text}\n\nPackage Select Karo:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("pkg_"))
def select_pkg(c):
    parts = c.data.split("_", 2)
    price = parts[1]
    pkg_name = parts[2]
    uid = user_data.get(c.from_user.id, {}).get('uid', 'N/A')
    region = user_data.get(c.from_user.id, {}).get('region', 'N/A')
    user_data[c.from_user.id].update({"pkg": pkg_name, "price": price})

    upi_link = f"upi://pay?pa={UPI_ID}&pn=Dubey&am={price}&cu=INR&tn={uid}"
    qr = qrcode.make(upi_link)
    bio = io.BytesIO()
    qr.save(bio, 'PNG')
    bio.seek(0)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Paid", callback_data="paid"), types.InlineKeyboardButton("❌ Cancel", callback_data="cancel"))

    caption = f"📦 {pkg_name}\n💰 Rs {price}\n🆔 UID: {uid}\n🌍 {region}\n\nUPI ID: {UPI_ID}\nQR Scan karke pay karo."
    bot.send_photo(c.message.chat.id, bio, caption=caption, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data in ["paid", "cancel"])
def paid_cancel(c):
    if c.data == "cancel":
        show_main_menu(c.message.chat.id, "Order Cancelled. /start se dobara shuru karo.")
        return
    bot.send_message(c.message.chat.id, "Payment ka Screenshot bhejo:", reply_markup=MAIN_MARKUP)
    bot.register_next_step_handler(c.message, get_screenshot)

def get_screenshot(m):
    if not m.photo:
        bot.send_message(m.chat.id, "Screenshot Photo bhejo bhai!", reply_markup=MAIN_MARKUP)
        bot.register_next_step_handler(m, get_screenshot)
        return
    data = user_data.get(m.from_user.id, {})
    caption = f"💸 NEW PAID ORDER\n\nUser: @{data.get('username')} ({m.from_user.id})\nUID: {data.get('uid')}\nRegion: {data.get('region')}\nPackage: {data.get('pkg')}\nPrice: {data.get('price')}\nUPI: {UPI_ID}"
    bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=caption)
    show_main_menu(m.chat.id, "✅ Order Received! Admin check karega. JAI SHREE RAM 🙏")

@bot.message_handler(func=lambda m: m.text in ["🛒 Order", "👥 Referral", "📞 Support"] or m.text in ["/referral", "/support"])
def handle_menu(m):
    if m.text == "👥 Referral" or m.text == "/referral":
        link = f"https://t.me/{BOT_USERNAME}?start={m.from_user.id}"
        data = load_json('referrals.json')
        count = len(data.get(str(m.from_user.id), []))
        show_main_menu(m.chat.id, f"👥 REFERRAL\n\nYour Link:\n{link}\n\nTotal: {count}\nEvery 5 referral you will get 100 like FREE!")
    elif m.text == "📞 Support" or m.text == "/support":
        bot.send_message(m.chat.id, "Apni problem bhejo:", reply_markup=MAIN_MARKUP)
        bot.register_next_step_handler(m, support_msg)
    elif m.text == "🛒 Order":
        bot.send_message(m.chat.id, "Order ke liye /start dabao", reply_markup=MAIN_MARKUP)

def support_msg(m):
    username = m.from_user.username or m.from_user.first_name
    cap = f"📞 SUPPORT\nUser: @{username} ({m.from_user.id})\nMsg: {m.text}"
    if m.photo:
        bot.send_photo(SUPPORT_ID, m.photo[-1].file_id, caption=cap)
    else:
        bot.send_message(SUPPORT_ID, cap)
    show_main_menu(m.chat.id, "Support ko bhej diya hai!")

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
