# import sqlite3
#
# bd = sqlite3.connect('database.sqlite')
#
# cur = bd.cursor()
# cur.execute("""
# create table if not exists RECORDS (
#     name text,
#     score integer
# )""")
#
# def get_best():
#     cur.execute("""
#     SELECT name gamer, max(score) score from RECORDS
#     GROUP BY name
#     ORDER BY score DESC
#     limit 5
#     """)
#     return cur.fetchall()
#
# print(get_best())
#
# def add_record(n, s):
#     cur.execute("""
#     INSERT INTO RECORDS (name, score)
#     VALUES (n, s)
#     """)
#     cur.execute()
#

import sqlite3 as sq

with sq.connect("database.sqlite") as con:
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS records (
        name TEXT,
        score INTEGER
        )""")

    def add_record(n, s):
        data = (n, s)
        cur.execute("""
            INSERT INTO records (name, score)
            VALUES (?, ?)
            """, data)
        con.commit()

    def get_best():
        cur.execute("""
            SELECT name gamer, max(score) score from records
            GROUP BY name
            ORDER BY score DESC
            LIMIT 5
            """)
        result = cur.fetchall()
        return result

    def get_one():
        cur.execute("""
            SELECT name, score from records
            WHERE id = 2;
            """)
        result = cur.fetchall()
        return result



