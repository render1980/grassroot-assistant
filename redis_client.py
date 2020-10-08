#! /usr/bin/python3

import redis

redis_client: redis.Redis = redis.Redis(host='localhost', port=6379, db=0)

def set_location(key, longitude, latitude):
    return execute_redis_cmd('SET {} {},{}'.format(key, longitude, latitude))

def get_location(key):
    res = execute_redis_cmd('GET {}'.format(key))
    location = res.decode('utf-8').split(',')
    if (len(location) < 2):
        raise ValueError('Invalid format of location={} for key={}'.format(location, key))
    return location

def search_location(longitude, latitude, radius):
    metric = 'm'
    print('search in radius {} {}: latitude={} longitude={}'.format(radius, metric, latitude, longitude))
    resp = execute_redis_cmd('GEORADIUS geos {} {} {} {} WITHDIST'.format(longitude, latitude, radius, metric))
    # resp example: [[b'group3', b'306.7983'], [b'group4', b'354.9435']]
    return resp

def check_group_exists(group):
    return execute_redis_cmd(group)

def create_group(group, admin_id, longitude, latitude):
    print('create: group={} admin_id={} longitude={} latitude={}'.format(group, admin_id, longitude, latitude))
    # TODO: pipeline?
    geoadd_res = execute_redis_cmd('GEOADD geos {} {} {}'.format(longitude, latitude, group))
    if (geoadd_res == 0):
        return 0
    rpush_res = execute_redis_cmd('RPUSH {} {}'.format(group, admin_id))
    print('successfully created new group {}'.format(group))
    return rpush_res

def delete_group(group):
    del_res = execute_redis_cmd('DEL {}'.format(group))
    if (del_res == 0):
        return 0
    zrem_res = execute_redis_cmd('ZREM {} {}'.format('geos', group))
    return zrem_res

def get_admins_by(group):
    return execute_redis_cmd('LRANGE {} 0 -1'.format(group))

def add_admin(groupd, new_admin_id):
    return execute_redis_cmd('RPUSH {} {}'.format(group, new_admin_id))

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

