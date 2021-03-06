import psycopg2 as pg
import os

postgres_db = os.getenv('POSTGRES_DB', 'postgres')
postgres_user = os.getenv('POSTGRES_USER', 'postgres')
postgres_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
conn = pg.connect("dbname={} user={} password={} host=0.0.0.0".format(postgres_db, postgres_user, postgres_password))

def link_group(group_name, desc, admin_id, longitude, latitude):
    print('Saving group={} admin_id={} longitude={} latitude={} -> DB'.format(group_name, admin_id, longitude, latitude))
    cur = conn.cursor()
    cur.execute("INSERT INTO grassroot.groups (group_name, description, creator_id, longitude, latitude, creation_date) VALUES (%s, %s, %s, %s, %s, current_timestamp)", (group_name, desc, admin_id, longitude, latitude))
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
    print('Deleting group={} by admin_id={}'.format(group_name, admin_id))
    cur = conn.cursor()
    cur.execute("SELECT group_id FROM grassroot.group_admins WHERE admin_id = %s AND group_name = %s", (admin_id, group_name))

    select_res = cur.fetchone()
    group_id = select_res[1]

    cur.execute("DELETE FROM grassroot.groups WHERE id = %s", (group_id,))
    cur.execute("DELETE FROM grassroot.group_admins WHERE group_id = %s", (group_id,))
    conn.commit()
    cur.close()
    return 1


def delete_admin(group_name, admin):
    print('Deleting admin={} from group={}'.format(group_name, admin))


def add_admin(group_name, admin):
    print('Adding admin={} to group={}'.format(admin, group_name))

def get_admins_ids_by(admin_id, group):
    print('admin_id={} Get admins ids by group name={}'.format(admin_id, group))
    cur = conn.cursor()
    cur.execute("SELECT admin_id FROM grassroot.group_admins WHERE group_name = %s", (group,))
    admins_ids = cur.fetchall()
    cur.close()
    return admins_ids


def get_description(admin_id, group_name):
    print('admin_id={} get_description for group_name={}'.format(admin_id, group_name))
    cur = conn.cursor()
    cur.execute("SELECT description FROM grassroot.groups WHERE group_name = %s", (group_name,))
    desc = cur.fetchone()
    cur.close
    return desc
