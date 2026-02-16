import telebot
import json
import os
from telebot.types import *

# ================== CONFIG ==================

TOKEN = os.getenv("TOKEN")  # Railway variable
ADMIN_ID = 7702942505  # 👈 Apna Telegram ID daalo

# Main bot access channels
REQUIRED_CHANNELS = [
    "@Shein_Reward",
    "@SheinStockss",
    "@SheinRewardsGc",
    "@sheinlinks202",
    "@sheinverse052"
]

# Folder access channels
FOLDER_CHANNELS = [
 url, "@https://t.me/addlist/hVr_c6PLZ8k5YmQ1"
]

REWARD_COSTS = {
    "500": 5,
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

def check_channels(user_id, channels):
    for ch in channels:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

def send_force_join(msg, channels, callback_name, title):
    markup = InlineKeyboardMarkup()
    for ch in channels:
        username = ch.replace("@", "")
        markup.add(
            InlineKeyboardButton(
                f"🔔 Join {username}",
                url=f"https://t.me/{username}"
            )
        )
    markup.add(
        InlineKeyboardButton("✅ I Joined", callback_data=callback_name)
    )
    bot.send_message(msg.chat.id, title, reply_markup=markup)

# ================== MENU ==================

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("👤 Dashboard", "🎁 Rewards")
    kb.row("🔗 My Empire Link", "🏆 Rankings")
    kb.row("📊 Empire Stats")
    kb.row("📂 Premium Folder")
    return kb

# ================== START ==================

@bot.message_handler(commands=['start'])
def start(msg):
    user_id = str(msg.from_user.id)
    args = msg.text.split()

    if not check_channels(msg.from_user.id, REQUIRED_CHANNELS):
        send_force_join(
            msg,
            REQUIRED_CHANNELS,
            "verify_main",
            "🚫 Access Locked!\nJoin all required channels to enter the empire."
        )
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
                        bot.send_message(ref, "👑 New warrior joined your empire! +1 Point")
                    except:
                        pass

        save_data(data)

    bot.send_message(
        msg.chat.id,
        """
╔══════════════════════════╗
      👑 BLACK GOLD EMPIRE 👑
╚══════════════════════════╝

💰 Earn • Refer • Dominate  
🎁 Unlock Royal Rewards  
🏆 Rise In Rankings  

Welcome to the Empire.
""",
        reply_markup=main_menu()
    )

# ================== VERIFY CALLBACKS ==================

@bot.callback_query_handler(func=lambda call: call.data == "verify_main")
def verify_main(call):
    if check_channels(call.from_user.id, REQUIRED_CHANNELS):
        bot.answer_callback_query(call.id, "Access Granted 👑")
        bot.send_message(call.message.chat.id, "Empire Unlocked!", reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "Join all channels first!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "verify_folder")
def verify_folder(call):
    if check_channels(call.from_user.id, FOLDER_CHANNELS):
        bot.answer_callback_query(call.id, "Folder Unlocked 👑")
        bot.send_message(call.message.chat.id, "📂 Premium Folder Access Granted!")
    else:
        bot.answer_callback_query(call.id, "Join all folder channels first!", show_alert=True)

# ================== ROUTER ==================

@bot.message_handler(func=lambda m: True)
def router(msg):
    user_id = str(msg.from_user.id)

    if not check_channels(msg.from_user.id, REQUIRED_CHANNELS):
        send_force_join(
            msg,
            REQUIRED_CHANNELS,
            "verify_main",
            "🚫 Access Locked!\nJoin all required channels first."
        )
        return

    if user_id not in data["users"]:
        return

    user = data["users"][user_id]
    text = msg.text

    # DASHBOARD
    if text == "👤 Dashboard":
        bot.send_message(
            msg.chat.id,
            f"""
╔════ 👑 EMPIRE DASHBOARD ═══╗

💠 Points        : {user['points']}
👥 Warriors      : {user['referrals']}
🎁 Rewards Taken : {user['redeemed']}

Status: Rising King 👑
"""
        )

    # REFERRAL LINK
    elif text == "🔗 My Empire Link":
        bot.send_message(
            msg.chat.id,
            f"""
🔗 Your Royal Invite Link:

https://t.me/YOUR_BOT_USERNAME?start={user_id}

Invite. Earn. Conquer 👑
"""
        )

    # STATS
    elif text == "📊 Empire Stats":
        s = data["stats"]
        bot.send_message(
            msg.chat.id,
            f"""
📊 GLOBAL EMPIRE STATS

👥 Total Users   : {s['users']}
🎁 Total Redeemed: {s['redeemed']}
🔗 Total Referrals: {s['referrals']}

Empire Growing Daily 🚀
"""
        )

    # LEADERBOARD
    elif text == "🏆 Rankings":
        sorted_users = sorted(
            data["users"].items(),
            key=lambda x: x[1]["referrals"],
            reverse=True
        )

        msg_text = "🏆 ROYAL RANKINGS\n\n"
        for i, (uid, u) in enumerate(sorted_users[:10], start=1):
            msg_text += f"👑 {i}. {uid} → {u['referrals']} warriors\n"

        bot.send_message(msg.chat.id, msg_text)

    # REWARDS
    elif text == "🎁 Rewards":
        markup = InlineKeyboardMarkup()
        for r, cost in REWARD_COSTS.items():
            markup.add(
                InlineKeyboardButton(
                    f"₹{r} Reward - {cost} Points",
                    callback_data=f"redeem_{r}"
                )
            )

        bot.send_message(msg.chat.id, "🎁 Select Your Royal Reward:", reply_markup=markup)

    # FOLDER SYSTEM
    elif text == "📂 Premium Folder":

        if not check_channels(msg.from_user.id, FOLDER_CHANNELS):
            send_force_join(
                msg,
                FOLDER_CHANNELS,
                "verify_folder",
                "📂 Folder Locked!\nJoin required channels to unlock premium content."
            )
            return

        bot.send_message(
            msg.chat.id,
            """
📂 PREMIUM RESOURCE VAULT

🔓 Access Granted

• Secret Files
• VIP Content
• Private Links
• Paid Materials

Empire Exclusive 👑
"""
        )

# ================== REDEEM ==================

@bot.callback_query_handler(func=lambda call: call.data.startswith("redeem_"))
def redeem(call):
    user_id = str(call.from_user.id)
    reward = call.data.split("_")[1]

    if reward not in data["codes"]:
        return

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
        f"""
╔════ 🎉 REWARD UNLOCKED ═══╗

🔐 Your Code:
{code}

Use it wisely 👑
"""
    )

    bot.answer_callback_query(call.id, "Success 👑")

# ================== ADMIN ==================

@bot.message_handler(commands=['addcode'])
def add_code(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    try:
        _, reward, code = msg.text.split(maxsplit=2)
        data["codes"][reward].append(code)
        save_data(data)
        bot.reply_to(msg, "Code Added 👑")
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
    bot.reply_to(msg, "Broadcast Sent 👑")

print("👑 BLACK GOLD EMPIRE RUNNING...")
bot.infinity_polling()
