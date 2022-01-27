import pytest

import bot
from bot import count_user_images, get_image_id

# @pytest.fixture()
# def users_info():
#     users_info = {111: {"sent_images": 2}, 222: {"sent_images": 0}}
#     return users_info

# USERS_INFO = {111: {"sent_images": 2}, 222: {"sent_images": 0}}


@pytest.mark.parametrize("test_input,expected", [(222, 0), (333, 0)])
def test_count_user_images(test_input, expected):
    result = count_user_images(test_input)
    assert result == expected


@pytest.fixture
def users_info():
    bot.USERS_INFO = {111: {"sent_images": 2}, 222: {"sent_images": 0}}
    return bot.USERS_INFO


def test_get_image_id_from_voice_update():
    context = (
        "<telegram.ext.callbackcontext.CallbackContext object at 0x0000025F6C023C30>"
    )
    with open("tests/test_data/voice_update.txt") as update:
        result = get_image_id(update, context)
        assert result == 2893
