import datetime
import telegram
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
)
from main import process_location, location, process_list_groups, list_groups

# Location

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
    assert msg is not None


def test_process_0(mocker):
    mocker.patch("redis_client.set_location", return_value=0)

    chat_id = 123
    user = telegram.User(666, "test_user", False)
    longitude = "56.311527"
    latitude = "38.135115"

    msg = location(chat_id, user, longitude, latitude)
    print("location message => \n{}\n".format(msg))
    assert not msg.__contains__("Error")


def test_process_negative(mocker):
    mocker.patch("redis_client.set_location", return_value=-1)

    chat_id = 123
    user = telegram.User(666, "test_user", False)
    longitude = "56.311527"
    latitude = "38.135115"

    msg = location(chat_id, user, longitude, latitude)
    print("location message => \n{}\n".format(msg))
    assert msg.__contains__("Error")


# List Groups


def test_list_groups(mocker):
    mocker.patch("redis_client.get_location", return_value=[56.311527, 38.135115])
    mocker.patch(
        "redis_client.search_groups_within_radius",
        return_value=[[100, "group1"], [200, "group2"]],
    )
    mocker.patch("redis_client.get_description", return_value="cool group")

    chat_id = 456
    radius = 100
    resp = list_groups(chat_id=chat_id, radius=radius)

    print("\ntest_list_groups response => {}\n".format(resp))
    assert resp.__contains__("group1")
    assert resp.__contains__("group2")
    assert not resp.__contains__("group3")


def test_list_when_groups_get_location_0(mocker):
    mocker.patch("redis_client.get_location", return_value=0)
    mocker.patch(
        "redis_client.search_groups_within_radius",
        return_value=[[100, "group1"], [200, "group2"]],
    )
    mocker.patch("redis_client.get_description", return_value="cool group")

    chat_id = 456
    radius = 100
    resp = list_groups(chat_id=chat_id, radius=radius)

    print("\ntest_list_groups response => {}\n".format(resp))
    assert resp.__contains__("Error")
    assert not resp.__contains__("group1")
    assert not resp.__contains__("group2")


def test_list_when_groups_search_groups_within_radius_0(mocker):
    mocker.patch(
        "redis_client.get_location", return_value=[56.311527, 38.135115]
    )
    mocker.patch(
        "redis_client.search_groups_within_radius",
        return_value=0,
    )
    mocker.patch("redis_client.get_description", return_value="cool group")

    chat_id = 456
    radius = 100
    resp = list_groups(chat_id=chat_id, radius=radius)

    print("\ntest_list_groups response => {}\n".format(resp))
    assert resp.__contains__("Error")
    assert not resp.__contains__("group1")
    assert not resp.__contains__("group2")


# Link group

def test_link_group(mocker):
    mocker.patch("redis_client.get_location", return_value=[56.311527, 38.135115])
    mocker.patch("redis_client.link_group", return_value=1)


def test_link_group_when_no_location_found(mocker):
    mocker.patch("redis_client.get_location", return_value=None)
    mocker.patch("redis_client.link_group", return_value=1)


def test_link_group_when_error_has_occured(mocker):
    mocker.patch("redis_client.get_location", return_value=[56.311527, 38.135115])
    mocker.patch("redis_client.link_group", return_value=-1)

def test_link_group_when_group_already_exists(mocker):
    mocker.patch("redis_client.get_location", return_value=[56.311527, 38.135115])
    mocker.patch("redis_client.link_group", return_value=0)
