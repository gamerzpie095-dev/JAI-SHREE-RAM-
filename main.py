from flask import Flask
import threading
import os
import telebot
import qrcode
from telebot import types


BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
SUPPORT_ID = 6014936495
UPI_ID = "dubeyadarsh17@fam"

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN secret is missing")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

bot.delete_webhook(drop_pending_updates=True)

users = {}

PACKS = {
    "100 LIKES - 35 RS": "35",
    "1.5K LIKES - 150 RS": "150",
    "3K LIKES - 300 RS": "300",
    "5K LIKES - 475 RS": "475",
    "10K LIKES - 950 RS": "950",
    "20K LIKES - 1900 RS": "1900",
}


def make_qr(amount):
    path = f"qr_{amount}.png"

    payment_url = (
        f"upi://pay?"
        f"pa={UPI_ID}&"
        f"pn=DUBEY&"
        f"am={amount}&"
        f"cu=INR"
    )

    qrcode.make(payment_url).save(path)
    return path


@bot.message_handler(commands=["start"])
def start_cmd(message):
    users[message.chat.id] = {
        "step": "name"
    }

    bot.send_message(
        message.chat.id,
        "🔥 <b>DUBEY FF LIKE STORE</b> 🔥\n\n"
        "Apna naam bhejo:"
    )


@bot.callback_query_handler(func=lambda callback: True)
def callback_handler(callback):
    try:
        bot.answer_callback_query(callback.id)
    except Exception:
        pass

    chat_id = callback.message.chat.id
    data = users.get(chat_id, {})

    support_info = (
        "🆘 <b>SUPPORT REQUEST!</b>\n\n"
        f"👤 Name: {data.get('name', 'N/A')}\n"
        f"👤 Username: {data.get('username_input', 'N/A')}\n"
        f"📦 {data.get('pack', 'N/A')}\n"
        f"🆔 {chat_id}"
    )

    if callback.data == "paid":
        users.setdefault(chat_id, {})
        users[chat_id]["step"] = "wait_ss"

        bot.send_message(
            chat_id,
            "✅ <b>PAID Clicked!</b>\n"
            "Ab payment ka screenshot yahi bhejo 👇"
        )

        paid_info = (
            "💰 <b>PAID CLICKED!</b>\n\n"
            f"👤 Name: {data.get('name', 'N/A')}\n"
            f"🎮 UID: {data.get('uid', 'N/A')}\n"
            f"👤 Username: {data.get('username_input', 'N/A')}\n"
            f"🌍 Region: {data.get('region', 'N/A')}\n"
            f"📦 Likes: {data.get('pack', 'N/A')}\n"
            f"💰 Amount: ₹{data.get('amount', 'N/A')}\n"
            f"🆔 Chat ID: {chat_id}"
        )

        try:
            bot.send_message(SUPPORT_ID, paid_info)
        except Exception:
            pass

    elif callback.data == "cancel":
        users.setdefault(chat_id, {})
        users[chat_id]["step"] = "pack"

        keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            row_width=1
        )

        for pack_name in PACKS:
            keyboard.add(pack_name)

        bot.send_message(
            chat_id,
            "❌ Cancel! Pack dubara select karo:",
            reply_markup=keyboard
        )

    elif callback.data == "support":
        try:
            bot.send_message(
                SUPPORT_ID,
                f"🆘 <b>SUPPORT!</b>\n{support_info}"
            )
        except Exception:
            pass

        bot.send_message(
            chat_id,
            "💬 Support ko request bhej diya! Jaldi reply aayega."
        )


@bot.message_handler(content_types=["photo"])
def handle_payment_screenshot(message):
    data = users.get(message.chat.id, {})

    caption = (
        "📸 <b>PAYMENT PROOF</b>\n"
        f"👤 Name: {data.get('name', 'N/A')}\n"
        f"👤 Username: {data.get('username_input', 'N/A')}\n"
        f"📦 Likes: {data.get('pack', 'N/A')}\n"
        f"🎮 UID: {data.get('uid', 'N/A')}\n"
        f"🌍 Region: {data.get('region', 'N/A')}\n"
        f"💵 Amount: ₹{data.get('amount', 'N/A')}\n"
        f"🆔 Chat ID: {message.chat.id}"
    )

    try:
        bot.send_photo(
            SUPPORT_ID,
            message.photo[-1].file_id,
            caption=caption
        )
    except Exception:
        pass

    bot.send_message(
        message.chat.id,
        "✅ Screenshot mil gaya! Please wait for confirmation."
    )


@bot.message_handler(
    func=lambda message: True,
    content_types=["text"]
)
def handle_text(message):
    if message.text.startswith("/"):
        return

    chat_id = message.chat.id

    if chat_id not in users:
        users[chat_id] = {
            "step": "name"
        }

        bot.send_message(
            chat_id,
            "Naam bhejo:"
        )
        return

    step = users[chat_id].get("step")

    if step == "name":
        users[chat_id]["name"] = message.text
        users[chat_id]["step"] = "username"

        bot.send_message(
            chat_id,
            "👤 Ab apna Username / Insta ID bhejo:"
        )

    elif step == "username":
        users[chat_id]["username_input"] = message.text
        users[chat_id]["step"] = "pack"

        keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            row_width=1
        )

        for pack_name in PACKS:
            keyboard.add(pack_name)

        bot.send_message(
            chat_id,
            f"Ok {message.text}! Pack select karo:",
            reply_markup=keyboard
        )

    elif step == "pack" and message.text in PACKS:
        users[chat_id]["pack"] = message.text
        users[chat_id]["amount"] = PACKS[message.text]
        users[chat_id]["step"] = "uid"

        bot.send_message(
            chat_id,
            "🎮 FF UID bhejo:",
            reply_markup=types.ReplyKeyboardRemove()
        )

    elif step == "uid":
        users[chat_id]["uid"] = message.text
        users[chat_id]["step"] = "region"

        keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            row_width=2
        )
        keyboard.add("IND", "SG", "ME", "BR")

        bot.send_message(
            chat_id,
            "🌍 Region select karo:",
            reply_markup=keyboard
        )

    elif step == "region":
        users[chat_id]["region"] = message.text

        amount = users[chat_id]["amount"]
        pack = users[chat_id]["pack"]
        uid = users[chat_id]["uid"]

        bot.send_message(
            chat_id,
            f"📦 {pack}\n"
            f"🎮 UID: {uid}\n"
            f"🌍 Region: {message.text}\n"
            f"💰 Amount: ₹{amount}",
            reply_markup=types.ReplyKeyboardRemove()
        )

        qr_path = make_qr(amount)

        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(
            types.InlineKeyboardButton(
                "✅ PAID",
                callback_data="paid"
            ),
            types.InlineKeyboardButton(
                "❌ CANCEL",
                callback_data="cancel"
            ),
            types.InlineKeyboardButton(
                "💬 SUPPORT",
                callback_data="support"
            )
        )

        with open(qr_path, "rb") as qr_file:
            bot.send_photo(
                chat_id,
                qr_file,
                caption=f"Pay ₹{amount} on {UPI_ID}",
                reply_markup=keyboard
            )


print("Bot Started...")
app = Flask('')
@app.route('/')
def home(): return "Bot is running!"

def run(): app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run).start()
bot.infinity_polling(skip_pending=True)
import os
import json
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5735299456
BOT_USERNAME = "Dubeyfflikesbot"

bot = telebot.TeleBot(BOT_TOKEN)

# Load referrals
def load_refs():
    try:
        with open('referrals.json','r') as f:
            return json.load(f)
    except:
        return {}

def save_refs(data):
    with open('referrals.json','w') as f:
        json.dump(data, f)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    user_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    refs = load_refs()

    # Referral check
    args = message.text.split()
    if len(args) > 1:
        referrer = args[1]
        if referrer!= user_id:
            if referrer not in refs:
                refs[referrer] = []
            if user_id not in refs[referrer]:
                refs[referrer].append(user_id)
                save_refs(refs)
                count = len(refs[referrer])

                # User ko batana
                try:
                    bot.send_message(referrer, f"✅ 1 New User Joined! Total: {count}")
                except: pass

                # Har 5 pe admin ko notify
                if count % 5 == 0:
                    likes = (count // 5) * 100
                    # Admin ko
                    bot.send_message(ADMIN_ID, f"🔥 NEW REWARD UNLOCKED!\n\nWinner ID: {referrer}\nUsername: {user_name}\nTotal Invites: {count}\nReward: {likes} Likes\n\nCheck karke likes de do!")
                    # Winner ko
                    try:
                        bot.send_message(referrer, f"🎉 MUBARAK HO! {count} Invite Complete!\n\nTumne {likes} Likes jeet liye!\nApna Instagram Username bhejo!")
                    except: pass

    if user_id not in refs:
        refs[user_id] = []
        save_refs(refs)

    count = len(refs[user_id])
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

    bot.send_message(message.chat.id, f"👋 Welcome {message.from_user.first_name}!\n\n🔗 Tera Referral Link:\n{link}\n\n📊 Score: {count} Invites\n🎁 Har 5 Invite = 100 Likes\n\nDosto ko share kar aur likes kama!")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    # Agar koi Insta ID bhejta hai to admin ko forward
    bot.send_message(ADMIN_ID, f"📩 Insta ID Aaya:\nFrom: @{message.from_user.username} ({message.from_user.id})\nID: {message.text}")
    bot.send_message(message.chat.id, "✅ Insta ID mil gaya! 5-10 min me likes aa jayenge!")

print("Bot Running...")
bot.infinity_polling()
