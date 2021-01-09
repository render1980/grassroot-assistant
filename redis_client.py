import redis

redis_client: redis.Redis = redis.Redis(host='localhost', port=6379, db=0)

CHAT_LOCATION_KEY = "location"
GEOS_KEY = "geos"


# ***************** #
# Current location  #
# ***************** #
def set_location(chat_id, longitude, latitude):
    return execute_redis_cmd('HSET {} {} {},{}'.format(CHAT_LOCATION_KEY, chat_id, longitude, latitude))


def get_location(chat_id):
    res = execute_redis_cmd('HGET {} {}'.format(CHAT_LOCATION_KEY, chat_id))
    location = res.decode('utf-8').split(',')
    if (len(location) < 2):
        raise ValueError('Invalid format of location={} for key={}'.format(location, chat_id))
    return location

# ***************** #


# `GEOADD geos 56.304558 38.135395 "group_name:description of the group_name"`
def link_group(group, desc, admin_id, longitude, latitude):
    print('create: group={} admin_id={} longitude={} latitude={}'.format(group, admin_id, longitude, latitude))
    geoadd_res = execute_redis_cmd('GEOADD {} {} {} "{}:{}"'.format(GEOS_KEY, longitude, latitude, group, desc))
    if (geoadd_res < 1):
        return geoadd_res
    print('successfully created group={} admin_id={} longitude={} latitude={}'.format(group, admin_id, longitude, latitude))
    # TODO: add async writing -> pg
    return add_admin(group, admin_id)


def search_groups_within_radius(longitude, latitude, radius=100):
    metric = 'm'
    print('search in radius {} {}: latitude={} longitude={}'.format(radius, metric, latitude, longitude))
    resp = execute_redis_cmd('GEORADIUS {} {} {} {} {} WITHDIST'.format(GEOS_KEY, longitude, latitude, radius, metric))
    # resp example: [[b'group3,desc', b'306.7983'], [b'group4,desc', b'354.9435']]
    return resp


# def delete_group_link(group):
    # del_admins_res = execute_redis_cmd('DEL {}:admins'.format(group))
    # if (del_location_res == 0 or del_chats_res == 0):
        # return 0
    # del_geos_res = execute_redis_cmd('HDEL {} {}'.format(GEOS_KEY, group))
    # del from pg
    # return del_geos_res


def get_admins_ids_by(group):
    return execute_redis_cmd('LRANGE {}:admins 0 -1'.format(group))

def add_admin(group, admin_id):
    return execute_redis_cmd('RPUSH {}:admins {}'.format(group, admin_id))


def execute_redis_cmd(cmd):
    """ Responses: 1 - ok, 0 - already exists, -1 - error """
    try:
        print('execute redis cmd: ', cmd)
        res = redis_client.execute_command(cmd)
        print('cmd: `{}` res: `{}`'.format(cmd, res))
        return res
    except redis.exceptions.ResponseError as err:
        print('Cmd: `{}` Exception: `{}`'.format(cmd, err))
        return -1


if __name__ == '__main__':
    search(58.524634, 31.286504, b'800')
    # get('user1')
#     create('group1', 11, 58.520158, 31.285259)
    # create('group2', 12, 58.519665, 31.284938)
    # create('group3', 13, 58.521433, 31.286161)
    # create('group4', 14, 58.521191, 31.287738)
