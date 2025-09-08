import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram.constants import ParseMode

# **ملاحظة هامة:**
# يجب استبدال "YOUR_BOT_TOKEN_HERE" و "YOUR_ADMIN_ID_HERE" بمعلوماتك.
# أفضل ممارسة هي استخدام متغيرات البيئة (Environment Variables) لحماية هذه البيانات.
#
# مثال:
# BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# ADMIN_ID = int(os.environ.get("ADMIN_ID"))
#
# لكن لتبسيط العملية، يمكنك إضافتها مباشرة هنا:

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # ضع توكن البوت الخاص بك هنا
ADMIN_ID = 123456789              # ضع الـ ID الخاص بك كمدير هنا (يجب أن يكون رقمًا)

async def start_command(update: Update, context):
    """يرسل رسالة الترحيب عند أمر /start."""
    welcome_text = "مرحباً بك في البوت! اضغط على زر `/admin` للتحكم الكامل."
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

async def admin_command(update: Update, context):
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

async def button_callback(update: Update, context):
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
    
    # تأكد أنك تقوم بتشغيل البوت بطريقة تتناسب مع بيئة الاستضافة
    # إذا كنت تستخدم Render، فإن Webhook هو الخيار الأفضل
    # أما إذا كنت تختبره محليًا، فإن Polling هو الأنسب

    # مثال على التشغيل المحلي (Polling)
    print("البوت يعمل...")
    application.run_polling()
    
    # مثال على التشغيل باستخدام Webhook لبيئات مثل Render.com
    # port = int(os.environ.get("PORT", "8443"))
    # application.run_webhook(
    #     listen="0.0.0.0",
    #     port=port,
    #     url_path=BOT_TOKEN,
    #     webhook_url=f"https://your-app-name.onrender.com/{BOT_TOKEN}"
    # )

if __name__ == "__main__":
    main()
