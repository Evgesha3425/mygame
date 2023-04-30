import sqlite3

bd = sqlite3.connect('database.sqlite')

cur = bd.cursor()
cur.execute("""
create table if not exists RECORDS (
    name text,
    score integer
)""")
def get_best():
    cur.execute("""
    SELECT name gamer, max(score) score from RECORDS 
    GROUP BY name
    ORDER BY score DESC
    limit 5
    """)
    return cur.fetchall()

print(get_best())