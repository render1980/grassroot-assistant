# grassroot-assistant

Bot which helps to communicate with others nearby over Telegram

## Redis

### Location

*Location (by chat_id)*

```
SET 1 56.346140,37.519993
OK

GET 1
"56.346140,37.519993"
```

### Create group (123 - chat_id)

```
GEOADD geos 56.344222 37.520566 test_group  
(integer) 1

RPUSH test_group 123 
```

### Search groups within radius

```
GEORADIUS geos 56.346140 37.519993 500 m WITHDIST
1) 1) "test_group"
   2) "180.7012"
```

### Get chat_ids for group

```
LRANGE test_group 0 -1
```
