from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import telegram
import re
import redis_client as rds
import notification as notify
import pdb


def start(update: telegram.Update, ctx: CallbackContext):
    chat_id = update.message.chat_id
    update.message.reply_text('First, share your location, please')


def process_location(update: telegram.Update, ctx: CallbackContext):
    message: telegram.Message = update.message
    chat_id = message.chat_id
    user: telegram.User = message.from_user
    longitude = message.location.latitude
    latitude = message.location.longitude
    text = 'process_location: user={} latitude={} longitude={}'.format(user,  latitude, longitude)
    cmd_res = rds.set_location(chat_id, longitude, latitude)
    if (cmd_res < 0):
        return message.reply_text('Saving location error! Sorry..')
    # TODO: more detailed description
    message.reply_text('Good, now you can use next commands:\n\n' +
                     '/list {search_radius} - show groups within your location radius\n' +
                     '/link {group_name} - link a group to your location\n' +
                     '/join {group_name} - request for joining to the group')


def list_groups(update: telegram.Update, ctx: CallbackContext):
    args = ctx.args
    message: telegram.Message = update.message
    print('call list with args: {}'.format(args))
    chat_id = update.message.chat_id
    if (len(args) < 1):
        return message.reply_text('Please, specify the search radius as a parameter')
    radius = args[0]
    location = rds.get_location(chat_id)
    if (location == 0):
        return message.reply_text('Cannot find your current location. Could you, please, send it again..')
    longitude = location[0]
    latitude = location[1]
    groups_in_radius = rds.search_groups_within_radius(longitude, latitude, radius)
    if (groups_in_radius == 0):
        return message.reply_text('Search groups error! Sorry..')
    print('groups in radius {} : {}'.format(radius, groups_in_radius))
    message.reply_text(str(groups_in_radius))


def link_group(update: telegram.Update, ctx: CallbackContext):
    args = ctx.args
    message: telegram.Message = update.message
    user: telegram.User = message.from_user
    admin_id = user.id
    if (len(args) < 1):
        return message.reply_text('Invalid arguments number={} but required={}'.format(len(args), 1))
    group = args[0]
    location = rds.get_location(admin_id)
    longitude = location[0]
    latitude = location[1]
    link_res = rds.link_group(group, admin_id, longitude, latitude)
    if (link_res < 0):
        return message.reply_text('Create group error has occured! Sorry..')
    if (link_res == 0):
        return message.reply_text('Group {} is already exists!'.format(group))
    message.reply_text('You have linked the group={} for the location: longitude={} latitude={}'.format(group, longitude, latitude))


def join_group(update: telegram.Update, ctx: CallbackContext):
    args = ctx.args
    message: telegram.Message = update.message
    user: telegram.User = message.from_user
    username = user.username
    chat_id = message.chat_id
    group = args[0]
    admins_ids = rds.get_admins_ids_by(group)
    for admin_id in admins_ids:
       print('Sending join notification of {} to {}'.format(username, admin_id))
       message.bot.send_message(chat_id=int(admin_id), text='User @{} wants to join group `{}`'.format(username, group))
    return message.reply_text('We have notified admins of group `{}`. They will add you soon ;)'.format(group))

# required token
# def add_admin(update: telegram.Update, ctx: CallbackContext):
    # message: telegram.Message = update.message
    # user: telegram.User = message.from_user
    # user_id = user.id
    # chat_id = message.chat_id
    # group = args[0]
    # new_admin = args[1]
    # access_token = args[2]
    # check_token
    # txt = 'add yet another admin={} to group={}'.format(new_admin, group)
    # print(txt)
    # rds.add_admin(group, new_admin)

# required token
# def delete_admin(update: telegram.Update, ctx: CallbackContext):
    # message: telegram.Message = update.message
    # user: telegram.User = message.from_user
    # user_id = user.id
    # chat_id = message.chat_id
    # group = args[0]
    # admin = args[1]
    # access_token = args[2]
    # check_token

# required token
# def delete_group_link(update: telegram.Update, ctx: CallbackContext):
    # message: telegram.Message = update.message
    # user: telegram.User = message.from_user
    # user_id = user.id
    # chat_id = message.chat_id
    # group = args[0]
    # access_token = args[2]
    # check_token


def main():
    # TODO: token -> to cmd line parameter
    updater = Updater('1237001342:AAE5sqITadSxeE06Xxcp8iPQz6AMCnRxN7Y')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.location, process_location))
    dp.add_handler(CommandHandler('list', list_groups, pass_args=True))
    dp.add_handler(CommandHandler('link', link_group, pass_args=True))
    dp.add_handler(CommandHandler('join', join_group, pass_args=True))
    # TODO: event loop it to process a lot of requests
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    # pdb.set_trace()
    main()
