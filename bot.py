import telebot
import json
import os
from telebot.types import *

# ================== CONFIG ==================

TOKEN = os.getenv("8516472351:AAEjte_yPW1fkHGujFvuw9Fwglgv6d_slyI")  # Railway variable
ADMIN_ID = 7702942505  # 👈 Apna Telegram ID daalo

REQUIRED_CHANNELS = [
    "@Shein_Reward",
    "@SheinStockss",
    "@SheinRewardsGc",
    "@sheinlinks202",
    "@sheinverse052"
]

FOLDER_LINK = "https://t.me/addlist/hVr_c6PLZ8k5YmQ1"

REWARD_COSTS = {
    "500": 4,
    "1000": 10,
    "2000": 20,
    "4000": 40
}

DATA_FILE = "data.json"

bot = telebot.TeleBot(TOKEN)

# ================== DATABASE ==================

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "users": {},
            "codes": {"500": [], "1000": [], "2000": [], "4000": []},
            "stats": {"users": 0, "redeemed": 0, "referrals": 0}
        }
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# ================== CHANNEL CHECK ==================

def check_channels(user_id):
    for ch in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

def send_force_join(msg):
    markup = InlineKeyboardMarkup()
    for ch in REQUIRED_CHANNELS:
        username = ch.replace("@", "")
        markup.add(
            InlineKeyboardButton(
                f"🔔 Join {username}",
                url=f"https://t.me/{username}"
            )
        )
    markup.add(
        InlineKeyboardButton("✅ I Joined", callback_data="verify")
    )
    bot.send_message(
        msg.chat.id,
        "🚫 You must join all required channels to use this bot.",
        reply_markup=markup
    )

# ================== MENU ==================

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("👤 Dashboard", "🎁 Rewards")
    kb.row("🔗 My Referral Link", "🏆 Leaderboard")
    kb.row("📊 Stats", "📂 Premium Folder")
    return kb

# ================== START ==================

@bot.message_handler(commands=['start'])
def start(msg):
    user_id = str(msg.from_user.id)
    args = msg.text.split()

    if not check_channels(msg.from_user.id):
        send_force_join(msg)
        return

    if user_id not in data["users"]:
        data["users"][user_id] = {
            "points": 0,
            "referrals": 0,
            "redeemed": 0,
            "referred_by": None
        }
        data["stats"]["users"] += 1

        # Referral system
        if len(args) > 1:
            ref = args[1]
            if ref != user_id and ref in data["users"]:
                if data["users"][user_id]["referred_by"] is None:
                    data["users"][ref]["points"] += 1
                    data["users"][ref]["referrals"] += 1
                    data["users"][user_id]["referred_by"] = ref
                    data["stats"]["referrals"] += 1
                    try:
                        bot.send_message(ref, "🎉 New referral joined! +1 Point")
                    except:
                        pass

        save_data(data)

    bot.send_message(
        msg.chat.id,
        "👑 Welcome to Shein Reward Empire 👑",
        reply_markup=main_menu()
    )

# ================== VERIFY ==================

@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify(call):
    if check_channels(call.from_user.id):
        bot.answer_callback_query(call.id, "Access Granted!")
        bot.send_message(call.message.chat.id, "Welcome 👑", reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "Join all channels first!", show_alert=True)

# ================== ROUTER ==================

@bot.message_handler(func=lambda m: True)
def router(msg):
    user_id = str(msg.from_user.id)

    if not check_channels(msg.from_user.id):
        send_force_join(msg)
        return

    if user_id not in data["users"]:
        return

    user = data["users"][user_id]
    text = msg.text

    if text == "👤 Dashboard":
        bot.send_message(
            msg.chat.id,
            f"""
👤 PROFILE

💰 Points: {user['points']}
👥 Referrals: {user['referrals']}
🎁 Redeemed: {user['redeemed']}
"""
        )

    elif text == "🔗 My Referral Link":
        bot.send_message(
            msg.chat.id,
            f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
        )

    elif text == "📊 Stats":
        s = data["stats"]
        bot.send_message(
            msg.chat.id,
            f"""
📊 GLOBAL STATS

👥 Users: {s['users']}
🔗 Referrals: {s['referrals']}
🎁 Redeemed: {s['redeemed']}
"""
        )

    elif text == "🏆 Leaderboard":
        sorted_users = sorted(
            data["users"].items(),
            key=lambda x: x[1]["referrals"],
            reverse=True
        )

        msg_text = "🏆 TOP REFERRERS\n\n"
        for i, (uid, u) in enumerate(sorted_users[:10], start=1):
            msg_text += f"{i}. {uid} → {u['referrals']} referrals\n"

        bot.send_message(msg.chat.id, msg_text)

    elif text == "📂 Premium Folder":
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(
                "📂 Open Shein Premium Folder",
                url=FOLDER_LINK
            )
        )

        bot.send_message(
            msg.chat.id,
            "📂 Click below to open the Premium Folder 👇",
            reply_markup=markup
        )

    elif text == "🎁 Rewards":
        markup = InlineKeyboardMarkup()
        for r, cost in REWARD_COSTS.items():
            markup.add(
                InlineKeyboardButton(
                    f"₹{r} Reward - {cost} Points",
                    callback_data=f"redeem_{r}"
                )
            )
        bot.send_message(msg.chat.id, "🎁 Select Reward:", reply_markup=markup)

# ================== REDEEM ==================

@bot.callback_query_handler(func=lambda call: call.data.startswith("redeem_"))
def redeem(call):
    user_id = str(call.from_user.id)
    reward = call.data.split("_")[1]

    cost = REWARD_COSTS[reward]
    user = data["users"][user_id]

    if user["points"] < cost:
        bot.answer_callback_query(call.id, "Not enough points!", show_alert=True)
        return

    if len(data["codes"][reward]) == 0:
        bot.answer_callback_query(call.id, "Out of stock!", show_alert=True)
        return

    code = data["codes"][reward].pop(0)

    user["points"] -= cost
    user["redeemed"] += 1
    data["stats"]["redeemed"] += 1

    save_data(data)

    bot.send_message(
        call.message.chat.id,
        f"🎉 Your Code: {code}"
    )

    bot.answer_callback_query(call.id, "Success!")

# ================== ADMIN ==================

@bot.message_handler(commands=['addcode'])
def add_code(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    try:
        _, reward, code = msg.text.split(maxsplit=2)
        data["codes"][reward].append(code)
        save_data(data)
        bot.reply_to(msg, "Code Added")
    except:
        bot.reply_to(msg, "Usage: /addcode 500 CODE123")

@bot.message_handler(commands=['broadcast'])
def broadcast(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    text = msg.text.replace("/broadcast ", "")
    for uid in data["users"]:
        try:
            bot.send_message(uid, text)
        except:
            pass
    bot.reply_to(msg, "Broadcast Sent")

print("Bot Running...")
bot.infinity_polling(skip_pending=True)
