import os
import sqlite3
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789"))  # غيرها لرقمك
DB_PATH = "referrals.db"

# ---------- قاعدة البيانات ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    points INTEGER DEFAULT 0,
                    referrer_id INTEGER
                )''')
    conn.commit()
    conn.close()

def add_user(user_id, referrer_id=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, points, referrer_id) VALUES (?, 0, ?)", (user_id, referrer_id))
    conn.commit()
    conn.close()

def add_point(user_id, pts=1):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (pts, user_id))
    conn.commit()
    conn.close()

def remove_point(user_id, pts=1):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET points = MAX(points - ?, 0) WHERE user_id = ?", (pts, user_id))
    conn.commit()
    conn.close()

def reset_points(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET points = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_points(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def get_referrals(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE referrer_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_total_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    row = c.fetchone()
    conn.close()
    return row[0]

# ---------- أوامر المستخدم ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args

    referrer_id = int(args[0]) if args else None
    add_user(user_id, referrer_id)

    if referrer_id and referrer_id != user_id:
        add_point(referrer_id)
        await context.bot.send_message(
            chat_id=referrer_id,
            text=f"🎉 شخص جديد دخل برابطك! نقاطك: {get_points(referrer_id)}"
        )

    await update.message.reply_text(
        "👋 أهلاً بك!\n"
        "استعمل /invite للحصول على رابط إحالتك.\n"
        "استعمل /points لمعرفة رصيد نقاطك.\n"
        "استعمل /referrals لرؤية من دخل برابطك."
    )

async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    link = f"https://t.me/{context.bot.username}?start={user_id}"
    await update.message.reply_text(f"🔗 رابط إحالتك:\n{link}")

async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    p = get_points(user_id)
    await update.message.reply_text(f"📊 نقاطك الحالية: {p}")

async def referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    refs = get_referrals(user_id)
    if not refs:
        await update.message.reply_text("❌ ما عندك أي إحالات لحد الآن.")
    else:
        text = "👥 الأشخاص اللي دخلوا برابطك:\n"
        text += "\n".join([f"- {rid}" for rid in refs])
        text += f"\n\n📊 المجموع: {len(refs)}"
        await update.message.reply_text(text)

# ---------- أوامر الأدمن ----------
def is_admin(user_id):
    return user_id == ADMIN_ID

async def addpoints(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    try:
        target = int(context.args[0])
        pts = int(context.args[1])
        add_point(target, pts)
        await update.message.reply_text(f"✅ تمت إضافة {pts} نقطة للمستخدم {target}.")
    except:
        await update.message.reply_text("❌ الاستعمال: /addpoints <user_id> <عدد النقاط>")

async def removepoints(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    try:
        target = int(context.args[0])
        pts = int(context.args[1])
        remove_point(target, pts)
        await update.message.reply_text(f"✅ تم خصم {pts} نقطة من المستخدم {target}.")
    except:
        await update.message.reply_text("❌ الاستعمال: /removepoints <user_id> <عدد النقاط>")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    try:
        target = int(context.args[0])
        reset_points(target)
        await update.message.reply_text(f"🔄 تم تصفير نقاط المستخدم {target}.")
    except:
        await update.message.reply_text("❌ الاستعمال: /reset <user_id>")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    msg = " ".join(context.args)
    users = get_all_users()
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=msg)
        except:
            pass
    await update.message.reply_text(f"📢 تم إرسال الرسالة إلى {len(users)} مستخدم.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    total = get_total_users()
    await update.message.reply_text(f"📊 عدد المستخدمين المسجلين: {total}")

async def listusers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    users = get_all_users()
    await update.message.reply_text("👥 المستخدمين:\n" + "\n".join(map(str, users)))

# ---------- Flask + Webhook ----------
flask_app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# أوامر المستخدم
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("invite", invite))
application.add_handler(CommandHandler("points", points))
application.add_handler(CommandHandler("referrals", referrals))

# أوامر الأدمن
application.add_handler(CommandHandler("addpoints", addpoints))
application.add_handler(CommandHandler("removepoints", removepoints))
application.add_handler(CommandHandler("reset", reset))
application.add_handler(CommandHandler("broadcast", broadcast))
application.add_handler(CommandHandler("stats", stats))
application.add_handler(CommandHandler("listusers", listusers))

@flask_app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

if __name__ == "__main__":
    init_db()
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
