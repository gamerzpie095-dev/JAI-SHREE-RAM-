import os
import json
import qrcode
import io
import threading
import telebot
from flask import Flask
from telebot import types

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = 5725948456
SUPPORT_ID = 6014934645
BOT_USERNAME = "Dubeyfflikebot"
UPI_ID = "dubeyadarsh17@fam"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Live - Dubey FF"

def load_json(f):
    try:
        with open(f, 'r') as x: return json.load(x)
    except: return {}

def save_json(f, d):
    with open(f, 'w') as x: json.dump(x, d)

user_data = {}

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
                        bot.send_message(ADMIN_ID, f"REFERRAL COMPLETE")
                    except: pass

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Order Likes", "Referral")
    bot.send_message(message.chat.id, "JAI SHREE RAM - Welcome!", reply_markup=markup)

# --- Yaha se tera baaki ka code same rahega jo neeche hai ---

def run_bot():
    print("Bot Starting...")
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
