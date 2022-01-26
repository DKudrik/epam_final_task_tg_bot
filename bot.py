import os

import boto3
from dotenv import load_dotenv
from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from image_processing import count_images

load_dotenv()

# bot = Bot(token=os.getenv('bot_token'))

updater = Updater(token=os.getenv("bot_token"))

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key"),
    region_name="ru-central1",
    endpoint_url="https://storage.yandexcloud.net",
)
BUCKET = "picture-process-bot-storage"

USERS_INFO = {}

FONTS = []

FONTS_SIZE = ["/32", "/48", "/64", "/80"]

SELECTED_FONT_SIZE = None

SELECTED_FONT = None


def wake_up(update, context):
    chat = update.effective_chat
    username = chat.username
    text = (
        "{username}, добро пожаловать! Я бот по обработке изображений. "
        "Умею наносить текст на изображение, объединять несколько картинок "
        "в GIF и многое другое. Список доступных команад: \n"
        "/start - стартовая страница \n"
        "/create_gif - создание GIF (требует мин. двух отправленных "
        "изображений) \n"
        "/get_all_gifs - получение всех GIF \n"
        "/get_user_gifs - получение всех GIF пользователя"
    )
    send_message(update, context, text.format(username=username))


def get_image_id(update, context):
    global USERS_INFO
    user_id = update.message.chat.id
    if update.message.document:
        if update.message.document.mime_type in ["image/png", "image/jpeg"]:
            image_id = update.message.document.file_id
        else:
            if USERS_INFO.get(user_id) and USERS_INFO[user_id]["sent_images"]:
                send_message(
                    update,
                    context,
                    "Отправьте следующее изображение или введите текст",
                )
            else:
                send_message(update, context, "Отправьте файл с изображением")
            image_id = None
    elif update.message.photo:
        image_id = update.message.photo[-1].file_id
    else:
        send_message(update, context, "Отправьте файл с изображением")
        image_id = None
    return image_id


def save_image(update, context):
    image_id = get_image_id(update, context)
    if image_id:
        image = context.bot.get_file(image_id)
        # 1. получать filepath
        # https://api.telegram.org/bot<token>/getFile?file_id=any
        # 2. чекать расширение

        user_id = update.message.chat.id
        image_name = f"{user_id}-{image_id}.jpg"
        image.download(image_name)
        global USERS_INFO
        if USERS_INFO.get(user_id) and USERS_INFO[user_id]["sent_images"] >= 1:
            text = (
                "Отправьте еще одно изображение или выберите, как "
                "сохранить GIF \n"
                "/create_private_GIF - создать приватный GIF \n"
                "/create_GIF - создать общий GIF"
            )
            send_message(update, context, text)
        elif (
            USERS_INFO.get(user_id) and USERS_INFO[user_id]["sent_images"] == 0
        ) or USERS_INFO.get(user_id, 0) == 0:
            USERS_INFO[user_id] = {"sent_images": 0}
            text = (
                "Отправьте следующее изображение или отправьте текст "
                "или выберите необходимое действие:"
                "/select_font - выбрать шрифт \n"
                "/select_font_size - выбрать размер шрифта"
            )
            send_message(update, context, text)
        USERS_INFO[user_id]["sent_images"] += 1


def get_text(update, context):
    global USERS_INFO
    global FONTS
    global SELECTED_FONT_SIZE
    global FONTS_SIZE
    global SELECTED_FONT
    user_id = update.message.chat.id
    text = update.message.text
    if USERS_INFO.get(user_id) and USERS_INFO[user_id]["sent_images"] == 1:
        if text.strip("/") in FONTS:
            SELECTED_FONT = text
            message = (
                "Отправьте текст или выберите размер шрифта: \n"
                "/select_font_size - выбрать размер шрифта"
            )
            send_message(update, context, message)
        elif text in FONTS_SIZE:
            SELECTED_FONT_SIZE = text.strip("/")
            message = (
                "Отправьте текст или выберите шрифт: \n" "/select_font - выбрать шрифт"
            )
            send_message(update, context, message)
        else:
            user_id = update.message.chat.id
            url = count_images(user_id, text, SELECTED_FONT, SELECTED_FONT_SIZE)
            s3.upload_file(url, BUCKET, url)
            send_image(update, context, url)
            os.remove(url)
            USERS_INFO[user_id]["sent_images"] = 0
            SELECTED_FONT = None
            SELECTED_FONT_SIZE = None
    elif USERS_INFO.get(user_id) and USERS_INFO[user_id]["sent_images"] > 1:
        text = "Отправьте еще одно изображение или нажмите /create_GIF"
        send_message(update, context, text)
    elif USERS_INFO.get(user_id) and USERS_INFO[user_id]["sent_images"] == 0:
        send_message(update, context, "Сначала отправьте изображение")
    elif USERS_INFO.get(user_id, 0) == 0:
        send_message(update, context, "Сначала отправьте изображение")


def create_private_gif(update, context):
    create_gif(update, context, private=True)


def create_gif(update, context, private=None):
    global USERS_INFO
    user_id = update.message.chat.id
    if USERS_INFO.get(user_id) and USERS_INFO[user_id]["sent_images"] >= 2:
        url = count_images(user_id, private=private)
        s3.upload_file(url, BUCKET, url)
        send_gif(update, context, url)
        os.remove(url)
        USERS_INFO[user_id]["sent_images"] = 0
    else:
        send_message(update, context, "Сначала отправьте изображение")


def send_message(update, context, text):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text=text)


def send_image(update, context, url):
    chat = update.effective_chat
    context.bot.send_photo(chat_id=chat.id, photo=open(url, "rb"))


def send_gif(update, context, url):
    chat = update.effective_chat
    context.bot.send_animation(chat_id=chat.id, animation=open(url, "rb"))


def get_and_send_all_gifs(update, context):
    chat = update.effective_chat
    user_id = update.message.chat.id
    gifs = s3.list_objects_v2(Bucket=BUCKET, Prefix="GIFS")["Contents"]
    for gif in gifs:
        gif_name = gif["Key"]
        if gif["Size"] != 0:
            if "private" in gif_name and str(user_id) not in gif_name:
                pass
            else:
                s3.download_file(BUCKET, gif_name, gif_name)
                context.bot.send_animation(
                    chat_id=chat.id, animation=open(gif_name, "rb")
                )
                os.remove(gif_name)


def get_and_send_user_gifs(update, context):
    chat = update.effective_chat
    user_id = update.message.chat.id
    gifs = s3.list_objects_v2(Bucket=BUCKET, Prefix="GIFS")["Contents"]
    for gif in gifs:
        gif_name = gif["Key"]
        if gif["Size"] != 0 and str(user_id) in gif_name:
            s3.download_file(BUCKET, gif_name, gif_name)
            context.bot.send_animation(chat_id=chat.id, animation=open(gif_name, "rb"))
            os.remove(gif_name)


def select_font(update, context):
    global USERS_INFO
    global FONTS
    FONTS = []
    user_id = update.message.chat.id
    if USERS_INFO.get(user_id) and USERS_INFO[user_id]["sent_images"] == 1:
        for font in os.listdir("fonts"):
            font = font.split(".")[0]
            FONTS.append(font)
            text = "/" + font
            send_message(update, context, text)
    elif USERS_INFO.get(user_id) and USERS_INFO[user_id]["sent_images"] > 1:
        text = "Отправьте еще одно изображение или нажмите /create_GIF"
        send_message(update, context, text)
    else:
        send_message(update, context, "Сначала отправьте изображение")


def select_font_size(update, context):
    global USERS_INFO
    global FONTS
    global SELECTED_FONT_SIZE
    SELECTED_FONT_SIZE = None
    for size in FONTS_SIZE:
        send_message(update, context, size)


updater.dispatcher.add_handler(CommandHandler("start", wake_up))
updater.dispatcher.add_handler(CommandHandler("create_private_GIF", create_private_gif))
updater.dispatcher.add_handler(CommandHandler("create_gif", create_gif))
updater.dispatcher.add_handler(CommandHandler("get_all_gifs", get_and_send_all_gifs))
updater.dispatcher.add_handler(CommandHandler("get_user_gifs", get_and_send_user_gifs))
updater.dispatcher.add_handler(CommandHandler("select_font", select_font))
updater.dispatcher.add_handler(CommandHandler("select_font_size", select_font_size))
updater.dispatcher.add_handler(MessageHandler(Filters.text, get_text))
updater.dispatcher.add_handler(MessageHandler(Filters.attachment, save_image))
updater.dispatcher.add_handler(MessageHandler(Filters.photo, save_image))
updater.start_polling(poll_interval=5.0)
updater.idle()
