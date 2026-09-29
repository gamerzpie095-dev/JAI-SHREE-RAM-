import os, json, threading, io
import telebot
from telebot import types
from flask import Flask
import qrcode

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5735299456
SUPPORT_ID = 6014936495
UPI_ID = "dubeyadarsh17@fam"
BOT_USERNAME = "Dubeyfflikebot" # Without @

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Live"

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

# Main Menu Buttons
MAIN_MARKUP = types.ReplyKeyboardMarkup(resize_keyboard=True)
MAIN_MARKUP.add("Order", "Referral")
MAIN_MARKUP.add("Support", "Cancel")

def get_user_display(m):
    return f"@{m.from_user.username}" if m.from_user.username else m.from_user.first_name

# --- START ---
@bot.message_handler(commands=['start'])
def start(m):
    user_id = str(m.from_user.id)
    username = get_user_display(m)

    # Referral Tracking
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
                        bot.send_message(ADMIN_ID, f"REFERRAL COMPLETE\nUser: {username} (ID: {referrer}) has completed 5 referrals.\nTotal referrals: {count}\nReward: 100 Likes Free")
                        bot.send_message(int(referrer), f"Congratulations! You completed 5 referrals. You will get 100 Likes Free. Admin has been notified.")
                    except:
                        pass

    bot.send_message(m.chat.id, f"Welcome {username}!\n\nWelcome to DUBEY FF SERVICES\nPlease send your Free Fire UID:", reply_markup=MAIN_MARKUP)
    bot.register_next_step_handler(m, get_uid)

def get_uid(m):
    if m.text == "Cancel":
        return cancel_order(m)
    if m.text in ["Order", "Referral", "Support"]:
        return handle_menu(m)
    user_data[m.from_user.id] = {"username": get_user_display(m), "user_id": m.from_user.id, "uid": m.text.strip()}
    bot.send_message(m.chat.id, "Please send your Region (Example: India):", reply_markup=MAIN_MARKUP)
    bot.register_next_step_handler(m, get_region)

def get_region(m):
    if m.text == "Cancel":
        return cancel_order(m)
    if m.text in ["Order", "Referral", "Support"]:
        return handle_menu(m)
    if m.from_user.id not in user_data:
        user_data[m.from_user.id] = {}
    user_data[m.from_user.id]['region'] = m.text.strip()

    markup = types.InlineKeyboardMarkup(row_width=1)
    for pkg, price in PACKAGES.items():
        markup.add(types.InlineKeyboardButton(f"{pkg} - Rs {price}", callback_data=f"pkg_{price}_{pkg}"))

    bot.send_message(m.chat.id, f"UID: {user_data[m.from_user.id]['uid']}\nRegion: {m.text}\n\nPlease select a package:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("pkg_"))
def select_pkg(c):
    parts = c.data.split("_", 2)
    price = parts[1]
    pkg_name = parts[2]

    if c.from_user.id not in user_data:
        bot.answer_callback_query(c.id, "Please send /start again")
        return

    user_data[c.from_user.id].update({"pkg": pkg_name, "price": price})
    uid = user_data[c.from_user.id].get('uid', 'N/A')
    region = user_data[c.from_user.id].get('region', 'N/A')

    # QR Code
    upi_link = f"upi://pay?pa={UPI_ID}&pn=DUBEY FF&am={price}&cu=INR&tn=FF_{uid}"
    qr = qrcode.make(upi_link)
    bio = io.BytesIO()
    qr.save(bio, 'PNG')
    bio.seek(0)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Paid", callback_data="paid"), types.InlineKeyboardButton("Cancel", callback_data="cancel"))

    caption = f"Package: {pkg_name}\nPrice: Rs {price}\nUID: {uid}\nRegion: {region}\nUPI ID: {UPI_ID}\n\nScan the QR code and pay. After payment, click Paid and send screenshot. If you want to cancel, click Cancel."
    bot.send_photo(c.message.chat.id, bio, caption=caption, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data in ["paid", "cancel"])
def paid_cancel_inline(c):
    if c.data == "cancel":
        user_data.pop(c.from_user.id, None)
        bot.send_message(c.message.chat.id, "Order cancelled. Send /start to create a new order.", reply_markup=MAIN_MARKUP)
        return
    bot.send_message(c.message.chat.id, "Please send your payment screenshot:", reply_markup=MAIN_MARKUP)
    bot.register_next_step_handler(c.message, get_screenshot)

def cancel_order(m):
    user_data.pop(m.from_user.id, None)
    bot.send_message(m.chat.id, "Order cancelled. Send /start to start again.", reply_markup=MAIN_MARKUP)

@bot.message_handler(commands=['cancel'])
def cancel_cmd(m):
    cancel_order(m)

def get_screenshot(m):
    if m.text == "Cancel":
        return cancel_order(m)
    if not m.photo:
        bot.send_message(m.chat.id, "Please send a screenshot as a photo. Or send Cancel to cancel.", reply_markup=MAIN_MARKUP)
        bot.register_next_step_handler(m, get_screenshot)
        return

    data = user_data.get(m.from_user.id, {})
    caption = f"NEW PAID ORDER\n\nUser: {data.get('username')} ({data.get('user_id')})\nUID: {data.get('uid')}\nRegion: {data.get('region')}\nPackage: {data.get('pkg')}\nPrice: Rs {data.get('price')}\nUPI: {UPI_ID}"

    bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=caption)
    bot.send_message(m.chat.id, "Order received! Admin will verify and deliver likes within 1-2 hours. If you have any issue, contact Support.", reply_markup=MAIN_MARKUP)
    user_data.pop(m.from_user.id, None)

# --- MENU HANDLERS ---
@bot.message_handler(func=lambda m: m.text in ["Order", "Referral", "Support", "Cancel"])
def handle_menu(m):
    if m.text == "Cancel":
        return cancel_order(m)
    elif m.text == "Referral" or m.text == "/referral":
        link = f"https://t.me/{BOT_USERNAME}?start={m.from_user.id}"
        data = load_json('referrals.json')
        count = len(data.get(str(m.from_user.id), []))
        bot.send_message(m.chat.id, f"REFERRAL MENU\n\nYour referral link:\n{link}\n\nTotal referrals: {count}\n\nEvery 5 referrals you will get 100 likes free.", reply_markup=MAIN_MARKUP)
    elif m.text == "Support" or m.text == "/support":
        bot.send_message(m.chat.id, "Please write your problem and send. If you have a screenshot, send it.", reply_markup=MAIN_MARKUP)
        bot.register_next_step_handler(m, support_msg)
    elif m.text == "Order":
        bot.send_message(m.chat.id, "To place a new order, please send /start", reply_markup=MAIN_MARKUP)

@bot.message_handler(commands=['referral', 'support'])
def cmd_handler(m):
    m.text = f"/{m.text}"
    if m.text == "/referral": m.text = "Referral"
    if m.text == "/support": m.text = "Support"
    handle_menu(m)

def support_msg(m):
    if m.text == "Cancel":
        return cancel_order(m)
    cap = f"SUPPORT MESSAGE\n\nUser: {get_user_display(m)} ({m.from_user.id})\nMessage: {m.text if m.text else 'Photo'}"
    if m.photo:
        bot.send_photo(SUPPORT_ID, m.photo[-1].file_id, caption=cap)
    else:
        bot.send_message(SUPPORT_ID, cap)
    bot.send_message(m.chat.id, "Your message has been sent to support team.", reply_markup=MAIN_MARKUP)

# --- RUN ---
def run_bot():
    print("Bot Starting...")
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
