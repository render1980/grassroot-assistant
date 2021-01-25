import datetime
import telegram
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
)
from main import (
    process_location,
    location,
    process_list_groups,
    list_groups,
    link_group,
    delete_group_link,
)

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
    longitude = 56.311527
    latitude = 38.135115

    msg = location(chat_id, longitude, latitude)
    print("location message => \n{}\n".format(msg))
    assert msg is not None


def test_process_0(mocker):
    mocker.patch("redis_client.set_location", return_value=0)

    chat_id = 123
    longitude = 56.311527
    latitude = 38.135115

    msg = location(chat_id, longitude, latitude)
    print("location message => \n{}\n".format(msg))
    assert not msg.__contains__("Error")


def test_process_negative(mocker):
    mocker.patch("redis_client.set_location", return_value=-1)

    chat_id = 123
    longitude = 56.311527
    latitude = 38.135115

    msg = location(chat_id, longitude, latitude)
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
    mocker.patch("redis_client.get_location", return_value=[56.311527, 38.135115])
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

    chat_id = 123
    group = "test_group"
    description = "desc"

    resp = link_group(chat_id, group, description)
    print("test_link_group => {}".format(resp))
    assert not resp.__contains__("Error")
    assert resp.__contains__("linked")


def test_link_group_when_no_location_found(mocker):
    mocker.patch("redis_client.get_location", return_value=[])
    mocker.patch("redis_client.link_group", return_value=1)

    chat_id = 123
    group = "test_group"
    description = "desc"

    resp = link_group(chat_id, group, description)
    print("\ntest_link_group_when_no_location_found => {}".format(resp))
    assert resp.__contains__("Error")


def test_link_group_when_error_has_occured(mocker):
    mocker.patch("redis_client.get_location", return_value=[56.311527, 38.135115])
    mocker.patch("redis_client.link_group", return_value=-1)

    chat_id = 123
    group = "test_group"
    description = "desc"

    resp = link_group(chat_id, group, description)
    print("\ntest_link_group_when_error_has_occured => {}".format(resp))
    assert resp.__contains__("Error while creating")


def test_link_group_when_group_already_exists(mocker):
    mocker.patch("redis_client.get_location", return_value=[56.311527, 38.135115])
    mocker.patch("redis_client.link_group", return_value=0)

    chat_id = 123
    group = "test_group"
    description = "desc"

    resp = link_group(chat_id, group, description)
    print("\ntest_link_group_when_group_already_exists => {}".format(resp))
    assert resp.__contains__("already exists")


# Delete group link


def test_delete_group_link_when_group_exists(mocker):
    mocker.patch("redis_client.delete_group_link", return_value=1)

    admin_id = 123
    group_name = "test_group"

    resp = delete_group_link(admin_id, group_name)
    print("\ntest_delete_group_link_when_group_exists => {}".format(resp))
    assert not resp.__contains__("Error")
    assert resp.__contains__("deleted")


def test_delete_group_link_when_group_is_not_exists(mocker):
    mocker.patch("redis_client.delete_group_link", return_value=0)

    admin_id = 123
    group_name = "test_group"

    resp = delete_group_link(admin_id, group_name)
    print("\ntest_delete_group_link_when_group_is_not_exists => {}".format(resp))
    assert resp.__contains__("Error")


def test_delete_group_link_when_error(mocker):
    mocker.patch("redis_client.delete_group_link", return_value=-1)

    admin_id = 123
    group_name = "test_group"

    resp = delete_group_link(admin_id, group_name)
    print("\ntest_delete_group_link_when_error => {}".format(resp))
    assert resp.__contains__("Error")
