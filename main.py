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
    msg = location(chat_id, user, longitude, latitude)
    return message.reply_text(msg)


def location(chat_id, user, longitude, latitude):
    print(
        "process_location: user={} chat_id={} latitude={} longitude={}".format(
            user, chat_id, latitude, longitude
        )
    )
    cmd_res = rds.set_location(chat_id, longitude, latitude)
    if cmd_res < 0:
        return "Error while saving location! Sorry.."
    return (
        "Good, now you can use next commands:\n\n"
        + "/list {radius} - show groups within your location radius (meters). 100m by default.\n"
        + "/link {group} {description} - link a group to your location.\n"
        + "/join {group} - request to join the group\n"
        + "/delete_link {group} - delete the link for Bot"
    )


def process_list_groups(update: telegram.Update, ctx: CallbackContext):
    args = ctx.args
    message: telegram.Message = update.message
    chat_id = message.chat_id
    if len(args) < 1:
        radius = DEFAULT_SEARCH_RADIUS
    else:
        radius = args[0]
    resp = list_groups(chat_id=chat_id, radius=radius)
    return message.reply_text(resp)


def list_groups(chat_id, radius):
    loc = rds.get_location(chat_id)
    if loc == 0:
        return "Error: cannot find your current location. Could you, please, send it again.."
    longitude = loc[0]
    latitude = loc[1]
    groups_in_radius = rds.search_groups_within_radius(longitude, latitude, radius)
    if groups_in_radius == 0:
        return "Error while searching groups! Sorry.."
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
    return list_groups_str


def process_link_group(update: telegram.Update, ctx: CallbackContext):
    args = ctx.args
    message: telegram.Message = update.message
    user: telegram.User = message.from_user
    admin_id = user.id
    if len(args) < 1:
        return message.reply_text(
            "Invalid arguments number={} but required={}".format(len(args), 1)
        )
    args_len = len(args)
    group = args[0]
    description = ""

    msg = link_group(group, description)
    return message.reply_text(msg)


def link_group(group, description):
    if args_len > 1:
        for i in range(1, args_len):
            description = "{} {}".format(description, args[i])
    description = description.replace(" ", "%")
    location = rds.get_location(admin_id)
    if len(location) < 2:
        return "Error: group {} not found".format(group)
    longitude = location[0]
    latitude = location[1]
    link_res = rds.link_group(group, description, admin_id, longitude, latitude)
    if link_res < 0:
        return "Error while creating group!"
    if link_res == 0:
        return "Group {} is already exists!".format(group)
    return "You have linked the group `{}` to the location: longitude={} latitude={}".format(
        group, longitude, latitude
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
    dp.add_handler(CommandHandler("list", process_list_groups, pass_args=True))
    dp.add_handler(CommandHandler("link", process_link_group, pass_args=True))
    dp.add_handler(CommandHandler("join", join_group, pass_args=True))
    dp.add_handler(CommandHandler("delete_link", delete_group_link, pass_args=True))
    # TODO: event loop it to process a lot of requests
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
