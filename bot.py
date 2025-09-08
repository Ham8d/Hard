import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# **تنبيه: هذا الأسلوب غير آمن!**
# يرجى استبدال "YOUR_BOT_TOKEN_HERE" و "YOUR_ADMIN_ID_HERE" بمعلوماتك.
# استخدام متغيرات البيئة (environment variables) هو الأسلوب الموصى به.
BOT_TOKEN = "8349322402:AAFWPI4snUxdCET_XumYSVoh3wa7Cgx4ojA"  # ضع توكن البوت هنا
ADMIN_ID = 1651487511              # ضع الـ ID الخاص بك هنا (تأكد من أنه رقم صحيح)

async def start_command(update: Update, context):
    """يرسل رسالة الترحيب عند أمر /start."""
    welcome_text = "مرحباً بك في البوت! اضغط على زر `/admin` للتحكم الكامل."
    await update.message.reply_text(welcome_text)

async def admin_command(update: Update, context):
    """يفتح لوحة تحكم المدير."""
    # التأكد من أن المستخدم هو المدير
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("عذراً، هذا الأمر مخصص للمدير فقط.")
        return

    # إنشاء أزرار لوحة التحكم
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
    
    # إضافة الأوامر والمستجيبات
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    print("البوت يعمل...")
    application.run_polling()

if __name__ == "__main__":
    main()
