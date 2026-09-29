import os, json, telebot, qrcode, io
from flask import Flask
import threading
from telebot import types

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = 5735299456
SUPPORT_ID = 6014936495
BOT_USERNAME = "Dubeyfflikesbot"
UPI_ID = "dubeyadarsh17@fam"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Live - Dubey FF"

def load_json(f):
    try:
        with open(f,'r') as x: return json.load(x)
    except: return {}
def save_json(f,d):
    with open(f,'w') as x: json.dump(x,d)

user_data = {}

# --- TERE NAYE RATES ---
PACKAGES = {
    "100 Likes - Rs 35 (TRUST)": 35,
    "1.5K Likes - Rs 150": 150,
    "3K Likes - Rs 300": 300,
    "5K Likes - Rs 475": 475,
    "10K Likes - Rs 950": 950,
    "20K Likes - Rs 1900": 1900
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
                        bot.send_message(ADMIN_ID, f"🔥 5 REFERRAL COMPLETE\nWinner ID: {referrer}\nTotal Referrals: {count}\nReward: {likes} Likes Dena Hai")
                    except: pass

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛒 Order Likes", "👥 Referral")
    markup.add
