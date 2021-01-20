import datetime
import telegram
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)
from main import process_location


def test_process_location(mocker):
    mocker.patch('redis_client.set_location', return_value=1)
    mocker.patch('telegram.Message.reply_text', return_value='Hello World')

    message = telegram.Message(
        message_id=123,
        date=datetime.date(2021, 1, 1),
        chat=telegram.Chat(id=456, type="simple_chat"),
        location=telegram.Location(56.311527, 38.135115),
        from_user=telegram.User(666, 'test_user', False)
    )
    update = telegram.Update(update_id=1, message=message)

    resp = process_location(update, None)
    print('process_location result => {}'.format(resp))
    assert resp == 'Hello World'
    assert resp != '1'
