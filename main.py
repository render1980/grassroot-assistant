#! /usr/bin/python3

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import re
import redis_client as rds
import notification as notify
import pdb

def start(bot: telegram.Bot, update: telegram.Update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id,
                     text="First, share your location, please")

def process_location(bot: telegram.Bot, update: telegram.Update):
    message: telegram.Message = update.message
    chat_id = message.chat_id
    user: telegram.User = message.from_user
    longitude = message.location.latitude
    latitude = message.location.longitude
    text = 'process_location: user={} latitude={} longitude={}'.format(user,  latitude, longitude)
    cmd_res = rds.set_location(chat_id, longitude, latitude)
    if (cmd_res == 0):
        bot.send_message(chat_id=chat_id,
                         text='Saving location error! Sorry..')
    # TODO: more detailed description
    bot.send_message(chat_id=chat_id,
                     text='Good, now you can use next commands:\n\n' +
                     '/list {search_radius} - show groups within your location radius\n' +
                     '/create {group_name} - create new group\n' +
                     '/join {group_name} - request for joining to a group')

def list_groups(bot: telegram.Bot, update: telegram.Update, args):
    print('call list with args: {}'.format(args))
    chat_id = update.message.chat_id
    if (len(args) < 1):
        return bot.send_message(chat_id=chat_id,
                         text="Please, specify search radius as parameter")
    radius = args[0]
    location = rds.get_location(chat_id)
    if (location == 0):
        bot.send_message(chat_id=chat_id,
                         text='Cannot find your current location in cash. ' +
                         'Could you, please, send it again..')
    longitude = location[0]
    latitude = location[1]
    groups_in_radius = rds.search_location(longitude, latitude, radius)
    if (groups_in_radius == 0):
        bot.send_message(chat_id=chat_id,
                         text='Search groups error! Sorry..')
    print('groups in radius {} : {}'.format(radius, groups_in_radius))
    bot.send_message(chat_id=chat_id,
                     text=str(groups_in_radius))

def create_group(bot: telegram.Bot, update: telegram.Update, args):
    message: telegram.Message = update.message
    user: telegram.User = message.from_user
    admin_id = user.id
    chat_id = message.chat_id
    if (len(args) < 1):
        bot.send_message(chat_id=chat_id,
                         text='Invalid arguments number={} but required={}'.format(len(args), 1))
    group = args[0]
    if (rds.check_group_exists(group)):
        bot.send_message(chat_id=chat_id,
                         text='Group {} is already exists. Please, choose other name for your new group'.format(group))
    location = rds.get_location(chat_id)
    longitude = location[0]
    latitude = location[1]
    create_res = rds.create_group(group, admin_id, chat_id, longitude, latitude)
    if (create_res == 0):
        bot.send_message(chat_id=chat_id,
                         text='Create group error has occured! Sorry..')
    bot.send_message(chat_id=chat_id,
                     text='You have created group={} for location: longitude={} latitude={}'.format(group, longitude, latitude))

def delete_group(group):
    message: telegram.Message = update.message
    user: telegram.User = message.from_user
    user_id = user.id
    chat_id = message.chat_id
    group = args[0]
    if (rds.check_group_exists(group) == 0):
        bot.send_message(chat_id=chat_id,
                         text='Group {} is not exists. Please, choose other your group name'.format(group))
    delete_res = rds.delete_group(group)
    if (delete_res == 0):
        bot.send_message(chat_id=chat_id,
                         text='Delete group error has occured! Sorry.. Try later')
    bot.send_message(chat_id=chat_id,
                     text='Group={} is deleted'.format(group))

def join_group(bot: telegram.Bot, update: telegram.Update, args):
    message: telegram.Message = update.message
    user: telegram.User = message.from_user
    username = user.username
    chat_id = message.chat_id
    group = args[0]
    if (rds.check_group_exists(group) == 0):
        bot.send_message(chat_id=chat_id,
                         text='Group {} is not exists. ' +
                         'Please, choose other name for group to join'.format(group))
    chat_ids = rds.get_chats_ids_by(group)
    for chat in chat_ids:
       print('sending join notification of {} to {}'.format(username, chat)) 
       bot.send_message(chat_id=chat,
                        text='User {} wants to join group {}'.format(username, group))
    # notify.notify(admins_ids, group, user.id)
    bot.send_message(chat_id=chat_id,
                     text='We have notified admins of this group. They will add you soon ;)')

# required token
def add_admin(bot: telegram.Bot, update: telegram.Update, args):
    message: telegram.Message = update.message
    user: telegram.User = message.from_user
    user_id = user.id
    chat_id = message.chat_id
    group = args[0]
    new_admin = args[1]
    access_token = args[2]
    txt = 'add yet another admin={} to group={}'.format(new_admin, group)
    print(txt)
    rds.add_admin(group, new_admin)
    bot.send_message(chat_id=chat_id, text=txt)

# required token
def delete_admin(bot: telegram.Bot, update: telegram.Update, args):
    message: telegram.Message = update.message
    user: telegram.User = message.from_user
    user_id = user.id
    chat_id = message.chat_id
    group = args[0]
    admin = args[1]
    access_token = args[2]
    text='delete admin={} from group={}'.format(admin, group)

def main():
    # TODO: token -> to cmd line parameter
    updater = Updater('1237001342:AAE5sqITadSxeE06Xxcp8iPQz6AMCnRxN7Y')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('list', list_groups, pass_args=True))
    dp.add_handler(CommandHandler('create', create_group, pass_args=True))
    dp.add_handler(CommandHandler('join', join_group, pass_args=True))
    dp.add_handler(MessageHandler(Filters.location, process_location))
    # TODO: event loop it to process a lot of requests
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    pdb.set_trace()
    main()

