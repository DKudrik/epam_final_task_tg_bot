import logging
import os
import time
from statistics import analysis, collect_statistics
from typing import Optional

import boto3
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.dispatcher import Update

from image_processing import get_final_image_url
from keyboards import (
    choose_GIF_type_keyboard,
    get_GIFS_keyboard,
    select_font_and_size_keyboard,
    select_font_keyboard,
    select_font_size_keyboard,
)

load_dotenv()

logger = logging.getLogger()

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
FONTS_SIZE = [32, 48, 64, 80]
SELECTED_FONT_SIZE = None
SELECTED_FONT = None


def wake_up(update: Update, context: CallbackContext) -> None:
    """
    Sends a greeting message with a list of the commands.

    :param update: represents an incoming update
    :param context: context of the processed message
    :return: None
    """
    chat = update.effective_chat
    username = chat.username
    message = (
        "{username}, добро пожаловать! Я бот по обработке изображений. "
        "Умею наносить текст на изображение, объединять несколько картинок "
        "в GIF и многое другое. Для начала работы отправьте изображение либо "
        "выберите одну из команд: "
    )
    keyboard = get_GIFS_keyboard
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        context.bot.send_message(
            chat_id=chat.id,
            text=message.format(username=username),
            reply_markup=reply_markup,
        )
        collect_statistics(chat.id, "вызов стартовой страницы")
    except Exception as e:
        logger.exception(e)


def count_user_images(user_id: int) -> int:
    """
    Returns number of previously sent images by the user (after every image
    processing the value is reset). In case it's a new user and there is no
    record about him, returns 0 instead of None so that the return value
    can be compared later with a condition value.

    :param user_id: id of the user
    :return: amount of user's sent messaged
    """
    if not USERS_INFO.get(user_id):
        return 0
    return USERS_INFO[user_id]["sent_images"]


def get_image_id(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat.id
    try:
        if update.message.document:
            if update.message.document.mime_type in ["image/png", "image/jpeg"]:
                image_id = update.message.document.file_id
            else:
                if count_user_images(user_id):
                    send_message(
                        update,
                        context,
                        "Отправьте следующее изображение или отправьте текст",
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
    except Exception as e:
        logger.exception(e)


def save_image(update: Update, context: CallbackContext) -> None:
    """
    Saves the received image and according to the amount of the previously
    sent images suggests the user next options.

    :param update: represents an incoming update
    :param context: context of the processed message
    :return: None
    """
    image_id = get_image_id(update, context)
    try:
        if image_id:
            image = context.bot.get_file(image_id)
            user_id = update.message.chat.id
            image_name = f"{user_id}-{image_id}.jpg"
            image.download(image_name)
            if count_user_images(user_id) >= 1:
                keyboard = choose_GIF_type_keyboard
                reply_markup = InlineKeyboardMarkup(keyboard)
                message = (
                    "Отправьте еще одно изображение или выберите, как сохранить GIF"
                )
                context.bot.send_message(
                    chat_id=user_id, text=message, reply_markup=reply_markup
                )
            elif count_user_images(user_id) == 0:
                USERS_INFO[user_id] = {"sent_images": 0}
                keyboard = select_font_and_size_keyboard
                reply_markup = InlineKeyboardMarkup(keyboard)
                message = (
                    "Отправьте следующее изображение или отправьте текст (при "
                    "необходимости возможно предварительно выбрать шрифт и "
                    "размер шрифта):"
                )
                context.bot.send_message(
                    chat_id=user_id, text=message, reply_markup=reply_markup
                )
            USERS_INFO[user_id]["sent_images"] += 1
    except Exception as e:
        logger.exception(e)


def process_text_from_message(update: Update, context: CallbackContext) -> None:
    """
    After receiving a text message, depending on th amount of the previously
    sent messages, add the text on the image or sends the notification.

    :param update: represents an incoming update
    :param context: context of the processed message
    :return: None
    """
    global SELECTED_FONT_SIZE
    global SELECTED_FONT
    global FONTS_SIZE
    user_id = update.message.chat.id
    text = update.message.text
    try:
        if count_user_images(user_id) == 1:
            url = get_final_image_url(user_id, text, SELECTED_FONT, SELECTED_FONT_SIZE)
            s3.upload_file(url, BUCKET, url)
            send_image(update, context, url)
            os.remove(url)
            USERS_INFO[user_id]["sent_images"] = 0
            SELECTED_FONT = None
            SELECTED_FONT_SIZE = None
            collect_statistics(user_id, "добавление текста на изображение")
        elif count_user_images(user_id) > 1:
            message = "Отправьте еще одно изображение или нажмите кнопку"
            keyboard = choose_GIF_type_keyboard
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(
                chat_id=user_id,
                text=message,
                reply_markup=reply_markup,
            )
        elif count_user_images(user_id) == 0:
            if text[:10].lower() == "статистика":
                message = analysis(text)
                send_message(update, context, message)
            else:
                send_message(update, context, "Сначала отправьте изображение")
    except Exception as e:
        logger.exception(e)


def create_private_gif(update: Update, context: CallbackContext) -> None:
    user_id = update.callback_query.message.chat.id
    try:
        create_gif(update, context, private=True)
        collect_statistics(user_id, "создание приватного GIF")
    except Exception as e:
        logger.exception(e)


def create_gif(
    update: Update, context: CallbackContext, private: Optional[bool] = None
) -> None:
    user_id = update.callback_query.message.chat.id
    try:
        if count_user_images(user_id) >= 2:
            url = get_final_image_url(user_id, private=private)
            s3.upload_file(url, BUCKET, url)
            send_gif(update, context, url)
            os.remove(url)
            USERS_INFO[user_id]["sent_images"] = 0
            collect_statistics(user_id, "создание GIF")
        else:
            send_message(update, context, "Сначала отправьте изображение")
    except Exception as e:
        logger.exception(e)


def send_message(update: Update, context: CallbackContext, text: str) -> None:
    """
    Aux func to send messages.

    :param update: represents an incoming update
    :param context: context of the processed message
    :param text: text to send
    :return: None
    """
    chat = update.effective_chat
    try:
        context.bot.send_message(chat_id=chat.id, text=text)
    except Exception as e:
        logger.exception(e)


def send_image(update: Update, context: CallbackContext, url: str) -> None:
    """
    Aux func to send images.

    :param update: represents an incoming update
    :param context: context of the processed message
    :param url: url of the image
    :return: None
    """
    chat = update.effective_chat
    try:
        context.bot.send_photo(chat_id=chat.id, photo=open(url, "rb"))
        message = "Отправьте новое изображение либо выберите одну из команд: "
        keyboard = get_GIFS_keyboard
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(
            chat_id=chat.id,
            text=message,
            reply_markup=reply_markup,
        )
    except Exception as e:
        logger.exception(e)


def send_gif(update: Update, context: CallbackContext, url: str) -> None:
    """
    Aux func to send GIFs.

    :param update: represents an incoming update
    :param context: context of the processed message
    :param url: url of the GIF
    :return: None
    """
    chat = update.effective_chat
    try:
        context.bot.send_animation(chat_id=chat.id, animation=open(url, "rb"))
        message = "Отправьте новое изображение либо выберите одну из команд: "
        keyboard = get_GIFS_keyboard
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(
            chat_id=chat.id,
            text=message,
            reply_markup=reply_markup,
        )
    except Exception as e:
        logger.exception(e)


def get_and_send_all_gifs(update: Update, context: CallbackContext) -> None:
    """
    Send all the GIFs made by all the users. In case GIF was created as private
    it would be sent only to its creator. To avoid Telegram flood limits
    sleep limit after each sent message was used.

    :param update: represents an incoming update
    :param context: context of the processed message
    :return: None
    """
    user_id = update.callback_query.message.chat.id
    try:
        gifs = s3.list_objects_v2(Bucket=BUCKET, Prefix="GIFS")["Contents"]
        counter = 0
        for gif in gifs:
            gif_name = gif["Key"]
            if gif["Size"] != 0:
                if "private" in gif_name and str(user_id) not in gif_name:
                    continue
                else:
                    counter += 1
                    s3.download_file(BUCKET, gif_name, gif_name)
                    context.bot.send_animation(
                        chat_id=user_id, animation=open(gif_name, "rb")
                    )
                    os.remove(gif_name)
                    time.sleep(0.1)
        if counter == 0:
            send_message(update, context, "Пока нет созданных GIF")
        collect_statistics(user_id, "получение всех GIF")
    except Exception as e:
        logger.exception(e)


def get_and_send_user_gifs(update: Update, context: CallbackContext) -> None:
    user_id = update.callback_query.message.chat.id
    try:
        gifs = s3.list_objects_v2(Bucket=BUCKET, Prefix="GIFS")["Contents"]
        counter = 0
        for gif in gifs:
            gif_name = gif["Key"]
            if gif["Size"] != 0 and str(user_id) in gif_name:
                s3.download_file(BUCKET, gif_name, gif_name)
                context.bot.send_animation(
                    chat_id=user_id, animation=open(gif_name, "rb")
                )
                os.remove(gif_name)
                counter += 1
                time.sleep(0.1)
        if counter == 0:
            send_message(update, context, "Вы пока не создали GIF")
        collect_statistics(user_id, "получение своих GIF")
    except Exception as e:
        logger.exception(e)


def show_fonts(update: Update, context: CallbackContext) -> None:
    """
    Show all the fonts added to the 'fonts' folder in the root.

    :param update: represents an incoming update
    :param context: context of the processed message
    :return: None
    """
    FONTS.clear()
    user_id = update.callback_query.message.chat.id
    keyboard = []
    try:
        if count_user_images(user_id) == 1:
            for font in os.listdir("fonts"):
                font = font.split(".")[0]
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            font, callback_data=f"get_selected_font_{font}"
                        )
                    ]
                )
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(
                chat_id=user_id, text="Выберите шрифт", reply_markup=reply_markup
            )
        elif count_user_images(user_id) > 1:
            send_message(update, context, "Отправьте следующее изображение")
        else:
            send_message(update, context, "Сначала отправьте изображение")
        update.callback_query.edit_message_reply_markup(None)
    except Exception as e:
        logger.exception(e)


def get_selected_font(update: Update, context: CallbackContext) -> None:
    """
    Captures the selected font from the pressed button.

    :param update: represents an incoming update
    :param context: context of the processed message
    :return: None
    """
    global SELECTED_FONT
    SELECTED_FONT = update.callback_query.data.split("_")[-1]
    user_id = update.callback_query.message.chat.id
    try:
        if count_user_images(user_id) == 1:
            if SELECTED_FONT_SIZE:
                send_message(update, context, "Отправьте текст")
            else:
                keyboard = select_font_size_keyboard
                reply_markup = InlineKeyboardMarkup(keyboard)

                message = "Отправьте текст или выберите размер шрифта:"
                context.bot.send_message(
                    chat_id=user_id, text=message, reply_markup=reply_markup
                )
        elif count_user_images(user_id) > 1:
            send_message(update, context, "Отправьте следующее изображение")
        else:
            send_message(update, context, "Сначала отправьте изображение")
        update.callback_query.edit_message_reply_markup(None)
        update.callback_query.message.delete()
    except Exception as e:
        logger.exception(e)


def show_font_sizes(update: Update, context: CallbackContext) -> None:
    user_id = update.callback_query.message.chat.id
    try:
        if count_user_images(user_id) == 1:
            keyboard = []
            for size in FONTS_SIZE:
                size = str(size)
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            size, callback_data=f"get_selected_font_size_{size}"
                        )
                    ]
                )
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(
                chat_id=user_id,
                text="Выберите размер шрифта",
                reply_markup=reply_markup,
            )
        elif count_user_images(user_id) > 1:
            send_message(update, context, "Отправьте следующее изображение")
        else:
            send_message(update, context, "Сначала отправьте изображение")
        update.callback_query.edit_message_reply_markup(None)
    except Exception as e:
        logger.exception(e)


def get_selected_font_size(update: Update, context: CallbackContext) -> None:
    """
    Captures the selected font size from the pressed button.

    :param update: represents an incoming update
    :param context: context of the processed message
    :return: None
    """
    global SELECTED_FONT_SIZE
    SELECTED_FONT_SIZE = int(update.callback_query.data.split("_")[-1])
    user_id = update.callback_query.message.chat.id
    try:
        if count_user_images(user_id) == 1:
            if SELECTED_FONT:
                send_message(update, context, "Отправьте текст")
            else:
                keyboard = select_font_keyboard
                reply_markup = InlineKeyboardMarkup(keyboard)

                message = "Отправьте текст или выберите шрифт:"
                context.bot.send_message(
                    chat_id=user_id, text=message, reply_markup=reply_markup
                )
        elif count_user_images(user_id) > 1:
            send_message(update, context, "Отправьте следующее изображение")
        else:
            send_message(update, context, "Сначала отправьте изображение")
        update.callback_query.edit_message_reply_markup(None)
        update.callback_query.message.delete()
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    logging.basicConfig(
        filename=__file__ + ".log",
        format="%(asctime)s - %(name)s - %(levelname)s - %(" "message)s",
        level=logging.WARNING,
    )

    updater.dispatcher.add_handler(CommandHandler("start", wake_up))
    updater.dispatcher.add_handler(
        CallbackQueryHandler(get_and_send_all_gifs, pattern="all_gifs")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(get_and_send_user_gifs, pattern="user_gifs")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(create_private_gif, pattern="create_private_gif")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(create_gif, pattern="create_gif")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(show_font_sizes, pattern="show_font_sizes")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(get_selected_font_size, pattern="get_selected_font_size*")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(show_fonts, pattern="show_fonts")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(get_selected_font, pattern="get_selected_font*")
    )
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text, process_text_from_message)
    )
    updater.dispatcher.add_handler(MessageHandler(Filters.attachment, save_image))
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, save_image))
    updater.start_polling(poll_interval=5.0)
    updater.idle()
