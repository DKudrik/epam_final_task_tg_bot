import datetime
import os

from bson.son import SON
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

USER = os.getenv("MONGO_USER")
PASSWORD = os.getenv("MONGO_PASS")
PORT = 27017

client = MongoClient(host="mongo_db", port=PORT, username=USER, password=PASSWORD)
db = client["statistics"]
collection = db["users"]


def collect_statistics(user_id: int, command: str) -> None:
    """
    Writing the received data to the MongoDB.

    :param user_id: user id
    :param command: received command
    :return:
    """
    date = datetime.datetime.today().strftime("%Y-%m-%d")
    collection.insert_one({"date": date, "user_id": user_id, "command": command})


def analysis(keywords: str) -> str:
    """
    Returns statistics of usage according to the received keyword.

    :param keywords: keywords for statistics
    :return:
    """
    keywords = keywords.lower()
    no_stats_message = "Бот ранее не использовался, статистика не набрана"
    if "активность" in keywords and "фичи" in keywords:
        actions = collection.aggregate(
            [
                {"$group": {"_id": "$command", "count": {"$sum": 1}}},
                {"$sort": SON([("count", -1)])},
            ]
        )
        actions_stats = ""
        counter = 0
        for action in actions:
            counter += 1
            actions_stats += (
                u"\u2022 " + action["_id"] + " - " + str(action["count"]) + "\n"
            )
        activities = collection.aggregate(
            [
                {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
                {"$sort": SON([("count", -1)])},
            ]
        )
        activities_stats = ""
        for act in activities:
            counter += 1
            activities_stats += (
                u"\u2022 "
                + str(act["_id"])
                + " - "
                + "действий"
                + " - "
                + str(act["count"])
                + "\n"
            )
        if counter:
            general_stats = "Общая статистика: \n" + actions_stats + activities_stats
            return general_stats
        return no_stats_message
    elif "фичи" in keywords:
        actions = collection.aggregate(
            [
                {"$group": {"_id": "$command", "count": {"$sum": 1}}},
                {"$sort": SON([("count", -1)])},
            ]
        )
        actions_stats = "Статистика использования фичей: \n"
        counter = 0
        for action in actions:
            counter += 1
            actions_stats += (
                u"\u2022 " + action["_id"] + " - " + str(action["count"]) + "\n"
            )
        if counter:
            return actions_stats
        return no_stats_message
    elif "активность" in keywords:
        activities = collection.aggregate(
            [
                {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
                {"$sort": SON([("count", -1)])},
            ]
        )
        activities_stats = "Статистика активности пользователей: \n"
        counter = 0
        for act in activities:
            counter += 1
            activities_stats += (
                u"\u2022 "
                + str(act["_id"])
                + " - "
                + "действий"
                + " - "
                + str(act["count"])
                + "\n"
            )
        if counter:
            return activities_stats
        return no_stats_message
    return "Неверные ключи"
