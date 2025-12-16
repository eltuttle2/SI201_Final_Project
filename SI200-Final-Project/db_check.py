"""
db_check.py
prints counts for characters and mediaappearances in disney.db
"""

import sqlite3

db_name = "disney.db"

def print_counts():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("create table if not exists characters (id integer primary key, name text)")
    c.execute("create table if not exists mediaappearances (character_id integer primary key, films text, tvshows text, videogames text, parkattractions text)")
    c.execute("select count(*) from characters")
    char_count = c.fetchone()[0]
    c.execute("select count(*) from mediaappearances")
    media_count = c.fetchone()[0]
    conn.close()
    print(f"characters table rows: {char_count}")
    print(f"mediaappearances table rows: {media_count}")

if __name__ == '__main__':
    print_counts()
