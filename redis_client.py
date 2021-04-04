import redis
import logging
import logging.config

redis_client: redis.Redis = redis.Redis(
    host='localhost', port=6379, db=0, decode_responses=True)

CHAT_LOCATION_KEY = "location"
GEOS_KEY = "geos"
DESCRIPTION_KEY = "desc"
SYNC_KEY = "sync"

logging.config.fileConfig('logging.conf')
log = logging.getLogger('grassroot')

# ***************** #
# Current location  #
# ***************** #


def set_location(chat_id, longitude, latitude):
    return execute_redis_cmd(chat_id, 'HSET {} {} {},{}'.format(CHAT_LOCATION_KEY, chat_id, longitude, latitude))


def get_location(chat_id):
    res = execute_redis_cmd(
        chat_id, 'HGET {} {}'.format(CHAT_LOCATION_KEY, chat_id))
    location = res.split(',')
    if (len(location) < 2):
        raise ValueError(
            'Invalid format of location={} for key={}'.format(location, chat_id))
    return location

# ***************** #


# `GEOADD geos 56.304558 38.135395 "group_name:description of the group_name"`
def link_group(group_name, desc, admin_id, longitude, latitude):
    desc = desc.replace(" ", "%")
    geoadd_res = execute_redis_cmd(admin_id, 'GEOADD {} {} {} {}'.format(
        GEOS_KEY, longitude, latitude, group_name))
    if geoadd_res < 1:
        return geoadd_res
    set_group_description(admin_id, group_name, desc)
    log.info(
        '[id=%d] successfully created group=%s admin_id=%d longitude=%s latitude=%s',
        admin_id, group_name, admin_id, longitude, latitude
    )
    return add_admin(admin_id, group_name)


def search_groups_within_radius(chat_id, longitude, latitude, radius=100):
    metric = 'm'
    resp = execute_redis_cmd(chat_id, 'GEORADIUS {} {} {} {} {} WITHDIST'.format(
        GEOS_KEY, longitude, latitude, radius, metric))
    return resp


def delete_group_link(group, admin_id):
    admins_ids = get_admins_ids_by(admin_id, group)
    log.info('[id=%d] delete_group_link(group=%s admin_id=%d) admins: %s',
             admin_id, group, admin_id, admins_ids)
    if (str(admin_id) not in admins_ids):
        log.warning('[id=%d] Cant delete group=%s by user=%d: He is not an admin of the group!',
                    admin_id, group, admin_id)
        return 0
    del_admins_res = execute_redis_cmd(admin_id, 'DEL {}:admins'.format(group))
    if del_admins_res == 0:
        return 0
    del_geos_res = execute_redis_cmd(
        admin_id, 'ZREM {} {}'.format(GEOS_KEY, group))
    return del_geos_res


def get_admins_ids_by(chat_id, group):
    return execute_redis_cmd(chat_id, 'SMEMBERS {}:admins'.format(group))


def add_admin(admin_id, group):
    return execute_redis_cmd(admin_id, 'SADD {}:admins {}'.format(group, admin_id))


def set_group_description(admin_id, group_name, desc):
    return execute_redis_cmd(admin_id, 'HSET {} {} {}'.format(DESCRIPTION_KEY, group_name, desc))


def get_description(admin_id, group_name):
    return execute_redis_cmd(admin_id, 'HGET {} {}'.format(DESCRIPTION_KEY, group_name))


def set_synced():
    """ Set fact that we have already synchronized data between DB and cache """
    return execute_redis_cmd(0, 'SET {} {}'.format(SYNC_KEY, '1'))


def is_synced():
    """ Check if data between DB and cache is synced """
    return execute_redis_cmd(0, 'GET {}'.format(SYNC_KEY)) == '1'


def execute_redis_cmd(admin_id, cmd):
    """ Redis responses: 1 - ok, 0 - already exists, -1 - error """
    try:
        res = redis_client.execute_command(cmd)
        log.info('[id=%d] redis cmd: `%s` res: `%s`', admin_id, cmd, res)
        return res
    except redis.exceptions.ResponseError as err:
        log.error('[id=%d] cmd: `%s` Exception: `%s`', admin_id, cmd, err)
        return -1
