import os
import tempfile
import img2pdf
from PIL import Image
import fitz  # PyMuPDF
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters, ContextTypes
)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
MAX_IMAGES = 10
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

# نخزن الصور مؤقتًا لكل مستخدم
user_images = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً! أرسل صور لأحولها PDF (حد 10 صور).\n"
        "أو أرسل ملف PDF لأرجعه صور."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo = update.message.photo[-1]  # أكبر جودة
    file = await photo.get_file()

    if file.file_size > MAX_FILE_SIZE:
        await update.message.reply_text("⚠️ حجم الصورة أكبر من 20MB.")
        return

    # خزّن الصورة مؤقتًا
    if user_id not in user_images:
        user_images[user_id] = []

    if len(user_images[user_id]) >= MAX_IMAGES:
        await update.message.reply_text("⚠️ الحد الأقصى 10 صور فقط.")
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tf:
        await file.download_to_drive(tf.name)
        user_images[user_id].append(tf.name)

    await update.message.reply_text(
        f"📸 تمت إضافة صورة. المجموع: {len(user_images[user_id])}/{MAX_IMAGES}.\n"
        "أرسل /makepdf لإنشاء PDF."
    )

async def make_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_images or not user_images[user_id]:
        await update.message.reply_text("❌ ما عندك صور محفوظة.")
        return

    images = user_images[user_id]
    pdf_path = tempfile.mktemp(suffix=".pdf")

    with open(pdf_path, "wb") as f:
        f.write(img2pdf.convert(images))

    await update.message.reply_document(document=open(pdf_path, "rb"), filename="output.pdf")
    user_images[user_id] = []  # تفريغ القائمة

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document

    if doc.file_size > MAX_FILE_SIZE:
        await update.message.reply_text("⚠️ حجم الملف أكبر من 20MB.")
        return

    file = await doc.get_file()
    pdf_path = tempfile.mktemp(suffix=".pdf")
    await file.download_to_drive(pdf_path)

    # تحويل PDF → صور باستخدام PyMuPDF
    pdf_doc = fitz.open(pdf_path)
    if len(pdf_doc) > MAX_IMAGES:
        await update.message.reply_text("⚠️ PDF يحتوي أكثر من 10 صفحات.")
        return

    for i, page in enumerate(pdf_doc, start=1):
        pix = page.get_pixmap()
        img_path = tempfile.mktemp(suffix=".jpg")
        pix.save(img_path)
        await update.message.reply_photo(photo=open(img_path, "rb"), caption=f"صفحة {i}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("makepdf", make_pdf))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.MimeType("application/pdf"), handle_pdf))

    app.run_polling()

if __name__ == "__main__":
    main()
