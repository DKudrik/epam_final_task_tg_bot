import os

from dotenv import load_dotenv
from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from image_processing import count_images

load_dotenv()

# bot = Bot(token=os.getenv('bot_token'))

updater = Updater(token=os.getenv("bot_token"))

user_sent_images = {}


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
    global user_sent_images
    user_id = update.message.chat.id
    if not update.message.photo:
        try:
            if update.message.document.mime_type not in ["image/png", "image/jpeg"]:
                if user_sent_images.get(user_id):
                    send_message(
                        update,
                        context,
                        "Отправьте следующее изображение " "или введите текст",
                    )
                else:
                    send_message(update, context, "Отправьте файл с изображением")
                image_id = None
            else:
                image_id = update.message.document.file_id
        except AttributeError:
            if user_sent_images.get(user_id):
                send_message(
                    update,
                    context,
                    "Отправьте следующее изображение" "или введите текст",
                )
            else:
                send_message(update, context, "Отправьте файл с изображением")
            image_id = None
    else:
        image_id = update.message.photo[-1].file_id
    return image_id


def save_image(update, context):
    image_id = get_image_id(update, context)
    if image_id:
        image = context.bot.get_file(image_id)
        # 1. получать filepath
        # https://api.telegram.org/bot5265067704:AAEMkbxQj0fnJKtg4uLct8U1N-dyHrEZ1yo/getFile?file_id=any
        # 2. чекать расширение

        user_id = update.message.chat.id
        image_name = f"{user_id}-{image_id}.jpg"
        image.download(image_name)
        global user_sent_images
        if user_sent_images.setdefault(user_id, 0) >= 1:
            send_message(
                update,
                context,
                "Отправьте еще одно изображение или нажмите /create_GIF",
            )
        elif user_sent_images.get(user_id) == 0:
            send_message(
                update, context, "Отправьте следующее изображение " "или введите текст"
            )
        user_sent_images[user_id] += 1


def get_text(update, context):
    global user_sent_images
    user_id = update.message.chat.id
    if user_sent_images.get(user_id) == 1:
        user_sent_images[user_id] = 0
        text = update.message.text
        user_id = update.message.chat.id
        url = count_images(user_id, text)
        send_image(update, context, url)
    elif user_sent_images.get(user_id, 0) > 1:
        send_message(
            update,
            context,
            "Отправьте еще одно изображение или нажмите /create_GIF",
        )
    elif user_sent_images.get(user_id, 0) == 0:
        send_message(update, context, "Сначала отправьте изображение")


def create_gif(update, context):
    global user_sent_images
    user_id = update.message.chat.id
    if user_sent_images.get(user_id, 0) < 2:
        send_message(update, context, "Отправьте изображение")
    else:
        url = count_images(user_id)
        send_gif(update, context, url)
    user_sent_images[user_id] = 0


def send_message(update, context, text):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text=text)


def send_image(update, context, url):
    chat = update.effective_chat
    context.bot.send_photo(chat_id=chat.id, photo=open(url, "rb"))


def send_gif(update, context, url):
    global user_sent_images
    if not user_sent_images:
        send_message(update, context, "Сначала отправьте изображение")
        pass
    chat = update.effective_chat
    context.bot.send_animation(chat_id=chat.id, animation=open(url, "rb"))


def get_and_send_all_gifs(update, context):
    chat = update.effective_chat
    for gif in os.listdir("GIFS"):
        url = "GIFS/" + gif
        context.bot.send_animation(chat_id=chat.id, animation=open(url, "rb"))


def get_user_gifs(update, context):
    chat = update.effective_chat
    user_id = update.message.chat.id
    for gif in os.listdir("GIFS"):
        if gif.startswith(str(user_id)):
            url = "GIFS/" + gif
            context.bot.send_animation(chat_id=chat.id, animation=open(url, "rb"))


updater.dispatcher.add_handler(CommandHandler("start", wake_up))
updater.dispatcher.add_handler(CommandHandler("create_gif", create_gif))
updater.dispatcher.add_handler(CommandHandler("get_all_gifs", get_and_send_all_gifs))
updater.dispatcher.add_handler(CommandHandler("get_user_gifs", get_user_gifs))
updater.dispatcher.add_handler(MessageHandler(Filters.text, get_text))
updater.dispatcher.add_handler(MessageHandler(Filters.attachment, save_image))
updater.dispatcher.add_handler(MessageHandler(Filters.photo, save_image))
updater.start_polling(poll_interval=3.0)
updater.idle()
