import psycopg2 as pg

conn = pg.connect("dbname=postgres user=postgres password=postgres host=0.0.0.0")

def insert_group(group, desc, admin_id, longitude, latitude, token):
    print('Saving group={} admin_id={} longitude={} latitude={} token={} -> DB'.format(group, admin_id, longitude, latitude, token))
    cur = conn.cursor()
    cur.execute("INSERT INTO grassroot.groups (group_name, description, creator_id, longitude, latitude, creation_date) VALUES (%s, %s, %s, %s, %s, current_timestamp)", (group, desc, admin_id, longitude, latitude))
    conn.commit()
    cur.execute('SELECT LASTVAL()')
    group_id = cur.fetchone()
    res = 0
    if group_id:
        cur.execute("INSERT INTO grassroot.group_admins (admin_id, group_id, token) VALUES (%s, %s, %s)",
                    (admin_id, group_id, token))
        conn.commit()
        cur.execute('SELECT LASTVAL()')
        group_admins_id = cur.fetchone()
        if group_admins_id:
            res = 1
    cur.close()
    return res
