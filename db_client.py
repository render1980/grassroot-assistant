import psycopg2 as pg
import psycopg2.extras
import os
import logging
import logging.config


logging.config.fileConfig("logging.conf")
log = logging.getLogger("grassroot")


postgres_db = os.getenv('POSTGRES_DB', 'postgres')
postgres_user = os.getenv('POSTGRES_USER', 'postgres')
postgres_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
conn = pg.connect("dbname={} user={} password={} host=0.0.0.0".format(postgres_db, postgres_user, postgres_password))


def link_group(group_name, desc, admin_id, longitude, latitude):
    log.info(
        "[id=%d] saving group=%s longitude=%f latitude=%f -> DB",
        admin_id, group_name, longitude, latitude
    )
    cur = conn.cursor()
    cur.execute("INSERT INTO grassroot.groups (group_name, description, admin_id, longitude, latitude, creation_date) VALUES (%s, %s, %s, %s, %s, current_timestamp)", (group_name, desc, admin_id, longitude, latitude))
    conn.commit()
    cur.execute('SELECT LASTVAL()')
    group_id = cur.fetchone()
    res = 0
    if group_id:
        cur.execute("INSERT INTO grassroot.group_admins (admin_id, group_id, group_name) VALUES (%s, %s, %s)",
                    (admin_id, group_id, group_name))
        conn.commit()
        cur.execute('SELECT LASTVAL()')
        group_admins_id = cur.fetchone()
        if group_admins_id:
            res = 1
    cur.close()
    return res


def delete_group_link(group_name, admin_id):
    log.info('[id=%d] deleting group=%s', admin_id, group_name)
    cur = conn.cursor()
    cur.execute("SELECT group_id FROM grassroot.group_admins WHERE admin_id = %s AND group_name = %s", (admin_id, group_name))

    select_res = cur.fetchone()
    group_id = select_res[0]

    cur.execute("DELETE FROM grassroot.groups WHERE id = %s", (group_id,))
    cur.execute("DELETE FROM grassroot.group_admins WHERE group_id = %s", (group_id,))
    conn.commit()
    cur.close()
    return 1


def delete_admin(group_name, admin_id):
    log.info('[id=%d] deleting from group=%s', admin_id, group_name)


def add_admin(group_name, admin_id):
    log.info('[id=%d] adding to group=%s', admin_id, group_name)


def get_admins_ids_by(admin_id, group_name):
    log.info('[id=%d] get admins ids by group name=%s', admin_id, group_name)
    cur = conn.cursor()
    cur.execute("SELECT admin_id FROM grassroot.group_admins WHERE group_name = %s", (group_name,))
    admins_ids = cur.fetchall()
    cur.close()
    return admins_ids


def get_description(admin_id, group_name):
    log.info(
        '[id=%d] get description for group_name=%s',
         admin_id, group_name
    )
    cur = conn.cursor()
    cur.execute("SELECT description FROM grassroot.groups WHERE group_name = %s", (group_name,))
    desc = cur.fetchone()
    cur.close()
    return desc


def get_groups_info():
    log.info('Get groups info from DB')
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT group_name,description,admin_id,longitude,latitude FROM grassroot.groups")
    groups_data = cur.fetchall()
    cur.close()
    return groups_data
