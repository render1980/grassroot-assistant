# grassroot-assistant

Bot which helps to communicate with others nearby over Telegram

## Telegram Bot Commands

```
/start - start communicating with Bot
/list {radius} - list groups within your location radius (meters). 100m by default.
/link {group} {description} - link a group to your location
/join {group} - request to join the group
/delete_link {group} {token} - delete the link for Bot
```

## Redis commands

### Current Location

*Location*

```
HSET location {chat_id} 56.346140,37.519993
OK

HGET location {chat_id}
"56.346140,37.519993"
```

### Link group

```
GEOADD geos 56.344222 37.520566 test_group  
(integer) 1

RPUSH test_group:admins admin_id1
```

### Search groups within radius

```
GEORADIUS geos 56.346140 37.519993 500 m WITHDIST
1) 1) "test_group"
   2) "180.7012"
```

### Get admins ids for group

```
LRANGE test_group:admins 0 -1
```

### Set group description

```
SET test_group description
```

### Get group description

```
GET test_group
```

## Pg scheme

`cat postgres/init.sql`
