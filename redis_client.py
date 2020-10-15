#! /usr/bin/python3

import redis

redis_client: redis.Redis = redis.Redis(host='localhost', port=6379, db=0)

CHAT_LOCATION_KEY = "location"
GEOS_KEY = "geos"

def set_location(chat_id, longitude, latitude):
    return execute_redis_cmd('HSET {} {} {},{}'.format(CHAT_LOCATION_KEY, chat_id, longitude, latitude))

def get_location(chat_id):
    res = execute_redis_cmd('HGET {} {}'.format(CHAT_LOCATION_KEY, chat_id))
    location = res.decode('utf-8').split(',')
    if (len(location) < 2):
        raise ValueError('Invalid format of location={} for key={}'.format(location, chat_id))
    return location

def search_location(longitude, latitude, radius):
    metric = 'm'
    print('search in radius {} {}: latitude={} longitude={}'.format(radius, metric, latitude, longitude))
    resp = execute_redis_cmd('GEORADIUS {} {} {} {} {} WITHDIST'.format(GEOS_KEY, longitude, latitude, radius, metric))
    # resp example: [[b'group3', b'306.7983'], [b'group4', b'354.9435']]
    return resp

def check_group_exists(group):
    return execute_redis_cmd(group)

def create_group(group, admin_id, chat_id, longitude, latitude):
    print('create: group={} admin_id={} chat_id={} longitude={} latitude={}'.format(group, admin_id, chat_id, longitude, latitude))
    geoadd_res = execute_redis_cmd('GEOADD {} {} {} {}'.format(GEOS_KEY, longitude, latitude, group))
    if (geoadd_res == 0):
        return 0
    add_admin_res = execute_redis_cmd('RPUSH {}:admins {}'.format(group, admin_id))
    add_chat_res = execute_redis_cmd('RPUSH {}:chats {}'.format(group, chat_id))
    print('successfully created group={} admin_id={} chat_id={}'.format(group, admin_id, chat_id))
    return add_chat_res

def delete_group(group):
    del_admins_res = execute_redis_cmd('DEL {}:admins'.format(group))
    del_chats_res = execute_redis_cmd('DEL {}:chats'.format(group))
    if (del_location_res == 0 or del_chats_res == 0):
        return 0
    del_geos_res = execute_redis_cmd('HDEL {} {}'.format(GEOS_KEY, group))
    return del_geos_res

def get_chats_ids_by(group):
    return execute_redis_cmd('LRANGE {}:chats 0 -1'.format(group))

def get_admins_ids_by(group):
    return execute_redis_cmd('LRANGE {}:admins 0 -1'.format(group))

def add_admin(group, new_admin_id):
    return execute_redis_cmd('RPUSH {}:admins {}'.format(group, new_admin_id))

def add_chat(group, new_chat_id):
    return execute_redis_cmd('RPUSH {}:chats {}'.format(group, new_chat_id))

def execute_redis_cmd(cmd):
    try:
        print('execute redis cmd: ', cmd)
        res = redis_client.execute_command(cmd)
        print('cmd: `{}` res: `{}`'.format(cmd, res))
        return res
    except redis.exceptions.ResponseError as err:
        print('Cmd: `{}` Exception: `{}`'.format(cmd, err))
        return 0

if __name__ == '__main__':
    search(58.524634, 31.286504, b'800')
    # get('user1')
#     create('group1', 11, 58.520158, 31.285259)
    # create('group2', 12, 58.519665, 31.284938)
    # create('group3', 13, 58.521433, 31.286161)
    # create('group4', 14, 58.521191, 31.287738)

