def test_qwe():
    assert 1 == 0


from bot import send_message

context = "<telegram.ext.callbackcontext.CallbackContext object at 0x000002116C747F40>"
update = {
    "update_id": 995793002,
    "message": {
        "entities": [{"length": 6, "offset": 0, "type": "bot_command"}],
        "message_id": 2788,
        "new_chat_photo": [],
        "caption_entities": [],
        "delete_chat_photo": False,
        "channel_chat_created": False,
        "date": 1643260526,
        "chat": {
            "last_name": "Denis",
            "type": "private",
            "id": 348696390,
            "first_name": "Denis",
            "username": "uxubisg",
        },
        "new_chat_members": [],
        "supergroup_chat_created": False,
        "photo": [],
        "group_chat_created": False,
        "text": "/start",
        "from": {
            "first_name": "Denis",
            "last_name": "Denis",
            "username": "uxubisg",
            "language_code": "ru",
            "id": 348696390,
            "is_bot": False,
        },
    },
}
