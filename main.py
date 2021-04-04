from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)
import os
import telegram
import logging
import logging.config
import redis_client as rds
import db_client as db
import threading


DEFAULT_SEARCH_RADIUS = 100

logging.config.fileConfig("logging.conf")
log = logging.getLogger("grassroot")


def start(update: telegram.Update, ctx: CallbackContext):
    update.message.reply_text("First, share your location, please")


def process_location(update: telegram.Update, ctx: CallbackContext):
    message: telegram.Message = update.message
    chat_id = message.chat_id
    longitude = message.location.latitude
    latitude = message.location.longitude
    msg = location(chat_id, longitude, latitude)
    return message.reply_text(msg)


def location(chat_id, longitude, latitude):
    log.info(
        "[id=%d] location(chat_id=%d longitude=%f latitude=%f)",
        chat_id,
        chat_id,
        longitude,
        latitude,
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
    resp = list_groups(admin_id=chat_id, radius=radius)
    return message.reply_text(resp)


def list_groups(admin_id, radius):
    """ radius - radius to search groups """
    loc = rds.get_location(admin_id)
    if loc == 0:
        return "Error: cannot find your current location. Could you, please, send it again.."
    longitude = loc[0]
    latitude = loc[1]
    groups_in_radius = rds.search_groups_within_radius(
        admin_id, longitude, latitude, radius
    )
    if groups_in_radius == 0:
        return "Error while searching groups! Sorry.."
    log.info(
        "[id=%d] list_groups(chat_id=%d radius=%s) => groups in radius: %s",
        admin_id,
        admin_id,
        radius,
        groups_in_radius,
    )
    list_groups_str = (
        "Groups within your location radius ({}m):\n\nname,distance,description".format(
            radius
        )
    )
    for g in groups_in_radius:
        radius = g[1]
        group_name = g[0]
        group_desc = db.get_description(admin_id, group_name)[0]
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
    if args_len > 1:
        for i in range(1, args_len):
            description = "{} {}".format(description, args[i])
    msg = link_group(admin_id, group, description)
    return message.reply_text(msg)


def link_group(chat_id, group, description):
    location = rds.get_location(chat_id)
    if len(location) < 2 or location is None:
        return "Error: group {} not found".format(group)
    longitude = location[0]
    latitude = location[1]
    log.info(
        "[id=%d] link_group(chat_id=%d group=%s description=%s) longitude=%s latitude=%s",
        chat_id,
        chat_id,
        group,
        description,
        longitude,
        latitude,
    )
    t = threading.Thread(
        target=db.link_group,
        args=(
            group,
            description,
            chat_id,
            longitude,
            latitude,
        ),
    )
    t.start()
    link_res = rds.link_group(group, description, chat_id, longitude, latitude)
    # TODO: async call db.link_group(group, description, chat_id, longitude, latitude)
    if link_res < 0:
        return "Error while creating group!"
    if link_res == 0:
        return "Group {} is already exists!".format(group)
    return "#link You have linked the group `{}` to the location: longitude={} latitude={}".format(
        group, longitude, latitude
    )


def process_join_group(update: telegram.Update, ctx: CallbackContext):
    args = ctx.args
    message: telegram.Message = update.message
    user: telegram.User = message.from_user
    chat_id = user.id
    username = user.username
    group = args[0]
    admins_ids = db.get_admins_ids_by(chat_id, group)
    for chat_id in admins_ids:
        log.info(
            "[id=%s] join_group: chat_id=%s group=%s sending join notification of %s",
            chat_id,
            chat_id,
            group,
            username,
        )
        message.bot.send_message(
            chat_id=int(chat_id),
            text="#join User @{} wants to join group `{}`".format(username, group),
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


def process_delete_group_link(update: telegram.Update, ctx: CallbackContext):
    args = ctx.args
    message: telegram.Message = update.message
    user: telegram.User = message.from_user
    admin_id = user.id

    if len(args) < 1:
        return message.reply_text("Please, define group")
    group_name = args[0]
    msg = delete_group_link(admin_id, group_name)
    message.reply_text(msg)


def delete_group_link(admin_id, group_name):
    t = threading.Thread(
        target=db.delete_group_link,
        args=(
            group_name,
            admin_id,
        ),
    )
    t.start()
    rds_del_res = rds.delete_group_link(group_name, admin_id)
    if rds_del_res < 1:
        return "Error: problems with deleting group={} from cache".format(group_name)
    return "#delete_link Group={} is deleted.".format(group_name)


def main():
    log.info("Grassroot-assistant is started")
    bot_token = os.getenv("BOT_TOKEN")
    updater = Updater(bot_token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.location, process_location))
    dp.add_handler(CommandHandler("list", process_list_groups, pass_args=True))
    dp.add_handler(CommandHandler("link", process_link_group, pass_args=True))
    dp.add_handler(CommandHandler("join", process_join_group, pass_args=True))
    dp.add_handler(
        CommandHandler("delete_link", process_delete_group_link, pass_args=True)
    )
    # TODO: event loop it to process a lot of requests
    updater.start_polling()
    updater.idle()


def cache_geos():
    log.info("Started updating geo indexes")
    if not rds.is_synced():
        groups_info = db.get_groups_info()
        t = threading.Thread(target=update_cache_geo, args=(groups_info,))
        t.start()


def update_cache_geo(groups_info):
    for group in groups_info:
        res = rds.link_group(
            group["group_name"],
            group["description"],
            group["admin_id"],
            group["longitude"],
            group["latitude"],
        )
    rds.set_synced()


if __name__ == "__main__":
    cache_geos()
    main()
