import psycopg2 as pg

conn = pg.connect("dbname=postgres user=postgres password=postgres host=0.0.0.0")

def insert_group(group_name, desc, admin_id, longitude, latitude, token):
    print('Saving group={} admin_id={} longitude={} latitude={} token={} -> DB'.format(group_name, admin_id, longitude, latitude, token))
    cur = conn.cursor()
    cur.execute("INSERT INTO grassroot.groups (group_name, description, creator_id, longitude, latitude, creation_date) VALUES (%s, %s, %s, %s, %s, current_timestamp)", (group_name, desc, admin_id, longitude, latitude))
    conn.commit()
    cur.execute('SELECT LASTVAL()')
    group_id = cur.fetchone()
    res = 0
    if group_id:
        cur.execute("INSERT INTO grassroot.group_admins (admin_id, group_id, group_name, token) VALUES (%s, %s, %s, %s)",
                    (admin_id, group_id, group_name, token))
        conn.commit()
        cur.execute('SELECT LASTVAL()')
        group_admins_id = cur.fetchone()
        if group_admins_id:
            res = 1
    cur.close()
    return res


def delete_group(group_name, admin_id, token):
    print('Deleting group={} by admin_id={}'.format(group_name, admin_id))
    cur = conn.cursor()
    cur.execute("SELECT token, group_id FROM grassroot.group_admins WHERE admin_id = %s AND group_name = %s", (admin_id, group_name))

    select_res = cur.fetchone()
    token_in_db = select_res[0]
    group_id = select_res[1]

    if token_in_db != token:
        print('Token is incorrect for admin_id = '.format(admin_id))
        cur.close()
        return 0
    cur.execute("DELETE FROM grassroot.groups WHERE id = %s", (group_id,))
    cur.execute("DELETE FROM grassroot.group_admins WHERE group_id = %s", (group_id,))
    conn.commit()
    cur.close()
    return 1


def delete_admin(group_name, admin):
    print('Deleting admin={} from group={}'.format(group_name, admin))


def add_admin(group_name, admin):
    print('Adding admin={} to group={}'.format(admin, group_name))
