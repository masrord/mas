import os
import telebot
import sqlite3
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)



# حالت مرحله‌ای کاربران
user_states = {}

# ساخت دیتابیس
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            phone TEXT,
            interest TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ذخیره اطلاعات
def save_user(uid, name, age, phone, interest):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (user_id, name, age, phone, interest, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
              (uid, name, age, phone, interest, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# شروع گفت‌وگو
@bot.message_handler(commands=['start'])
def start(msg):
    user_states[msg.chat.id] = {'step': 'name'}
    bot.send_message(msg.chat.id, "سلام! لطفاً نام خود را وارد کنید:")

# مدیریت مراحل
@bot.message_handler(func=lambda msg: True)
def handle(msg):
    uid = msg.chat.id
    if uid not in user_states:
        bot.send_message(uid, "لطفاً /start را وارد کنید.")
        return

    state = user_states[uid]

    if state['step'] == 'name':
        state['name'] = msg.text
        state['step'] = 'age'
        bot.send_message(uid, "سن شما؟")
    elif state['step'] == 'age':
        if not msg.text.isdigit():
            bot.send_message(uid, "سن باید عدد باشد.")
            return
        state['age'] = int(msg.text)
        state['step'] = 'phone'
        bot.send_message(uid, "شماره تماس شما؟")
    elif state['step'] == 'phone':
        state['phone'] = msg.text
        state['step'] = 'interest'
        bot.send_message(uid, "شغل یا علاقه‌مندی شما؟")
    elif state['step'] == 'interest':
        state['interest'] = msg.text
        save_user(uid, state['name'], state['age'], state['phone'], state['interest'])
        bot.send_message(uid, "✅ اطلاعات شما با موفقیت ثبت شد.")
        del user_states[uid]

# اجرای اولیه
init_db()
print("🤖 ربات در حال اجراست...")
bot.infinity_polling()
