import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

FONT_DIR = 'fonts/'  # Directory where fonts are stored
FONT_PATH = os.path.join(FONT_DIR, 'font1.ttf')  # You can change this to the font of your choice
IMAGE_SIZE = (800, 400)  # Default size for the generated image

def create_quote_image(quote_text, author=None):
    img = Image.new('RGB', IMAGE_SIZE, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_PATH, size=40)
    except IOError:
        font = ImageFont.load_default()
    text_position = (50, 150)
    draw.text(text_position, quote_text, font=font, fill=(0, 0, 0))  # Black text
    if author:
        draw.text((50, 350), f"- {author}", font=font, fill=(0, 0, 0))  # Black text
    image_io = BytesIO()
    img.save(image_io, format='PNG')
    image_io.seek(0)
    return image_io

def download_sticker_as_image(sticker):
    file = sticker.get_file()
    response = requests.get(file.file_path)
    image = Image.open(BytesIO(response.content))
    image = image.convert('RGBA')
    return image

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a text message or a sticker, and I'll create a quote image for you!")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    author = update.message.from_user.first_name
    image_io = create_quote_image(text, author=author)
    await update.message.reply_photo(photo=image_io)

async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker = update.message.sticker
    sticker_image = download_sticker_as_image(sticker)
    image_io = BytesIO()
    sticker_image.save(image_io, format='PNG')
    image_io.seek(0)
    await update.message.reply_photo(photo=image_io)

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_content = requests.get(file.file_path).content
    image = Image.open(BytesIO(image_content))
    image = image.convert('RGB')
    image_io = BytesIO()
    image.save(image_io, format='PNG')
    image_io.seek(0)
    await update.message.reply_photo(photo=image_io)

if __name__ == '__main__':
    application = ApplicationBuilder().token('6752171458:AAEsP8Z_1NFxLLo1D7AV34Na0LbQMD5fb3c').build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT, handle_text))
    application.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.run_polling()
  
