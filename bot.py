import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# قراءة المتغيرات من Environment
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
PORT = int(os.environ.get("PORT", "8443"))

if not BOT_TOKEN or ADMIN_ID == 0:
    raise ValueError("يجب تعيين TELEGRAM_TOKEN و ADMIN_ID في Environment Variables")

# دالة /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "مرحباً بك في البوت! اضغط على زر `/admin` للتحكم الكامل."
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

# دالة /admin
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("عذراً، هذا الأمر مخصص للمدير فقط.")
        return

    admin_keyboard = [
        [InlineKeyboardButton("إدارة الأزرار", callback_data="manage_buttons")],
        [InlineKeyboardButton("إرسال إذاعة", callback_data="broadcast_message")],
        [InlineKeyboardButton("تعديل رسالة الترحيب", callback_data="edit_welcome_msg")],
    ]
    reply_markup = InlineKeyboardMarkup(admin_keyboard)
    await update.message.reply_text("مرحباً بك يا مدير! هذه لوحة التحكم:", reply_markup=reply_markup)

# دالة التعامل مع الأزرار
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "manage_buttons":
        await query.edit_message_text("هنا يمكنك إضافة، تعديل، أو حذف الأزرار. (تحتاج برمجة إضافية)")
    elif data == "broadcast_message":
        await query.edit_message_text("هنا يمكنك إرسال إذاعة للجميع. (تحتاج برمجة إضافية)")
    elif data == "edit_welcome_msg":
        await query.edit_message_text("هنا يمكنك تعديل رسالة الترحيب. (تحتاج برمجة إضافية)")

# الدالة الرئيسية
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    # تشغيل Webhook على Render
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"https://اسم-مشروعك.onrender.com/{BOT_TOKEN}"
    )

if __name__ == "__main__":
    main()
