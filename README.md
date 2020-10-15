# grassroot-assistant

Bot which helps to communicate with others nearby over Telegram

## Redis

### Location

*Location*

```
HSET location chat_id 56.346140,37.519993
OK

HGET location chat_id
"56.346140,37.519993"
```

### Create group

```
GEOADD geos 56.344222 37.520566 test_group  
(integer) 1

RPUSH test_group:admins admin_id1
RPUSH test_group:chats chat_id1
```

### Search groups within radius

```
GEORADIUS geos 56.346140 37.519993 500 m WITHDIST
1) 1) "test_group"
   2) "180.7012"
```

### Get chats ids for group

```
LRANGE test_group:chats 0 -1
```

### Get admins ids for group

```
LRANGE test_group:admins 0 -1
```
