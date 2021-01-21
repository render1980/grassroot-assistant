import datetime
import telegram
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)
from main import process_location, location

## Location

def test_process_location(mocker):
    mocker.patch("redis_client.set_location", return_value=1)
    mocker.patch("telegram.Message.reply_text", return_value="Hello World")

    message = telegram.Message(
        message_id=123,
        date=datetime.date(2021, 1, 1),
        chat=telegram.Chat(id=456, type="simple_chat"),
        location=telegram.Location(56.311527, 38.135115),
        from_user=telegram.User(666, "test_user", False),
    )
    update = telegram.Update(update_id=1, message=message)

    resp = process_location(update, None)
    print("process_location result => \n{}\n".format(resp))
    assert resp == "Hello World"
    assert resp != "0"


def test_process_1(mocker):
    mocker.patch("redis_client.set_location", return_value=1)

    chat_id = 123
    user = telegram.User(666, "test_user", False)
    longitude = "56.311527"
    latitude = "38.135115"

    msg = location(chat_id, user, longitude, latitude)
    print("location message => \n{}\n".format(msg))


def test_process_0(mocker):
    mocker.patch("redis_client.set_location", return_value=0)

    chat_id = 123
    user = telegram.User(666, "test_user", False)
    longitude = "56.311527"
    latitude = "38.135115"

    msg = location(chat_id, user, longitude, latitude)
    print("location message => \n{}\n".format(msg))
    assert not msg.__contains__("error")


def test_process_negative(mocker):
    mocker.patch("redis_client.set_location", return_value=-1)

    chat_id = 123
    user = telegram.User(666, "test_user", False)
    longitude = "56.311527"
    latitude = "38.135115"

    msg = location(chat_id, user, longitude, latitude)
    print("location message => \n{}\n".format(msg))
    assert msg.__contains__("error")


## List Groups

def test_list_groups(mocker):
    mocker.patch("redis_client.get_location", return_value=[56.311527, 38.135115])
    mocker.patch(
        "redis_client.search_groups_within_radius",
        return_value=[[100, "group1"], [200, "group2"]],
    )
    mocker.patch("redis_client.get_description", return_value="cool group")


