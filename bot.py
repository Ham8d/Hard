import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# قراءة التوكن وID المشرف من Environment Variables
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))  # القيمة الافتراضية 0 إذا لم توجد

if not BOT_TOKEN or ADMIN_ID == 0:
    raise ValueError("يجب تعيين TELEGRAM_TOKEN و ADMIN_ID في Environment Variables")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يرسل رسالة الترحيب عند أمر /start."""
    welcome_text = "مرحباً بك في البوت! اضغط على زر `/admin` للتحكم الكامل."
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يفتح لوحة تحكم المدير."""
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

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يستجيب للضغط على الأزرار."""
    query = update.callback_query
    await query.answer()

    data = query.data
    if data == "manage_buttons":
        await query.edit_message_text("هنا يمكنك إضافة، تعديل، أو حذف الأزرار. (هذه الميزة تحتاج إلى برمجة إضافية)")
    elif data == "broadcast_message":
        await query.edit_message_text("هنا يمكنك إرسال رسالة إذاعة للجميع. (هذه الميزة تحتاج إلى برمجة إضافية)")
    elif data == "edit_welcome_msg":
        await query.edit_message_text("هنا يمكنك تعديل رسالة الترحيب. (هذه الميزة تحتاج إلى برمجة إضافية)")

def main():
    """الدالة الرئيسية لتشغيل البوت."""
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    print("البوت يعمل...")
    application.run_polling()  # للتشغيل المحلي
    # إذا كنت تريد Render، يمكنك استخدام run_webhook مع تعيين PORT وwebhook_url

if __name__ == "__main__":
    main()
