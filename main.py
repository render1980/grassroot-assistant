from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)
import os
import telegram
import redis_client as rds

DEFAULT_SEARCH_RADIUS = 100


def start(update: telegram.Update, ctx: CallbackContext):
    update.message.reply_text("First, share your location, please")


def process_location(update: telegram.Update, ctx: CallbackContext):
    message: telegram.Message = update.message
    chat_id = message.chat_id
    user: telegram.User = message.from_user
    longitude = message.location.latitude
    latitude = message.location.longitude
    print(
        "process_location: user={} latitude={} longitude={}".format(
            user, latitude, longitude
        )
    )
    cmd_res = rds.set_location(chat_id, longitude, latitude)
    if cmd_res < 0:
        return message.reply_text("Saving location error! Sorry..")
    return message.reply_text(
        'Good, now you can use next commands:\n\n'
        + '/list {radius} - show groups within your location radius (meters). 100m by default.\n'
        + '/link {group} {description} - link a group to your location.\n'
        + '/join {group} - request to join the group\n'
        + '/delete_link {group} - delete the link for Bot'
    )


def list_groups(update: telegram.Update, ctx: CallbackContext):
    args = ctx.args
    message: telegram.Message = update.message
    print("call list with args: {}".format(args))
    chat_id = update.message.chat_id
    if len(args) < 1:
        radius = DEFAULT_SEARCH_RADIUS
    else:
        radius = args[0]
    location = rds.get_location(chat_id)
    if location == 0:
        return message.reply_text(
            "Cannot find your current location. Could you, please, send it again.."
        )
    longitude = location[0]
    latitude = location[1]
    groups_in_radius = rds.search_groups_within_radius(longitude, latitude, radius)
    if groups_in_radius == 0:
        return message.reply_text("Search groups error! Sorry..")
    print("groups in radius {} : {}".format(radius, groups_in_radius))
    list_groups_str = (
        "Groups within your location radius ({}m):\n\nname,distance,description".format(
            radius
        )
    )
    for g in groups_in_radius:
        radius = g[1]
        group_name = g[0]
        group_desc = rds.get_description(group_name)
        list_groups_str = "{}\n{},{},{}".format(
            list_groups_str, group_name, radius, group_desc
        )
    return message.reply_text(list_groups_str)


def link_group(update: telegram.Update, ctx: CallbackContext):
    args = ctx.args
    message: telegram.Message = update.message
    user: telegram.User = message.from_user
    admin_id = user.id
    if len(args) < 1:
        return message.reply_text(
            "Invalid arguments number={} but required={}".format(len(args), 1)
        )
    group = args[0]
    args_len = len(args)
    description = ""
    if args_len > 1:
        for i in range(1, args_len):
            description = "{} {}".format(description, args[i])
    description = description.replace(" ", "%")
    location = rds.get_location(admin_id)
    longitude = location[0]
    latitude = location[1]
    link_res = rds.link_group(group, description, admin_id, longitude, latitude)
    if link_res < 0:
        return message.reply_text("Creating group error has occured! Sorry..")
    if link_res == 0:
        return message.reply_text("Group {} is already exists!".format(group))
    return message.reply_text(
        "You have linked the group `{}` to the location: longitude={} latitude={}".format(
            group, longitude, latitude
        )
    )


def join_group(update: telegram.Update, ctx: CallbackContext):
    args = ctx.args
    message: telegram.Message = update.message
    user: telegram.User = message.from_user
    username = user.username
    group = args[0]
    admins_ids = rds.get_admins_ids_by(group)
    for admin_id in admins_ids:
        print("Sending join notification of {} to {}".format(username, admin_id))
        message.bot.send_message(
            chat_id=int(admin_id),
            text="User @{} wants to join group `{}`".format(username, group),
        )
    return message.reply_text(
        "We have notified admins of group `{}`. They will add you soon.".format(group)
    )


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


def delete_group_link(update: telegram.Update, ctx: CallbackContext):
    args = ctx.args
    message: telegram.Message = update.message
    user: telegram.User = message.from_user
    admin_id = user.id
    if len(args) < 1:
        return message.reply_text("Please, define group")
    group_name = args[0]
    rds_del_res = rds.delete_group_link(group_name, admin_id)
    if rds_del_res < 1:
        return message.reply_text(
            "Problems with deleting group={} from cache".format(group_name)
        )
    return message.reply_text("Group={} is deleted.".format(group_name))


def main():
    bot_token = os.getenv("BOT_TOKEN")
    updater = Updater(bot_token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.location, process_location))
    dp.add_handler(CommandHandler("list", list_groups, pass_args=True))
    dp.add_handler(CommandHandler("link", link_group, pass_args=True))
    dp.add_handler(CommandHandler("join", join_group, pass_args=True))
    dp.add_handler(CommandHandler("delete_link", delete_group_link, pass_args=True))
    # TODO: event loop it to process a lot of requests
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
