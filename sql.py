import sqlite3


def sql_create_table(connection):
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS  homepage (
                    mask_id INTEGER PRIMARY KEY IS NOT NULL,
                    title TEXT,
                    create_time INTEGER,
                    cover_img_url TEXT,
                    )""")
    connection.commit()
    connection.close()
    return

def sql_insert_data(connection, data):
    cursor = connection.cursor()
    cursor.execute("""INSERT INTO homepage (mask_id, title, create_time, cover_img_url) VALUES (?, ?, ?, ?)""", data)
    connection.commit()
    connection.close()
    return

def sql_select_data(connection):
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM homepage""")
    data = cursor.fetchall()
    connection.close()
    return data


if __name__ == '__main__':
    connection = sqlite3.connect('meipian.db')
    sql_create_table(connection)
    data = (1, 'title', 123456789, '')
    sql_insert_data(connection, data)
    data = sql_select_data(connection)
    print(data)
