import sqlite3

DB_NAME = "final_project.db"


def create_marvel_tables():
    """
    Create all Marvel-related tables in final_project.db.

    We fully normalize all repeating string categories into separate
    lookup tables so that the main tables only store integer IDs
    and numeric values.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # ---------- Lookup tables (each string stored once, UNIQUE) ----------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS marvel_hero_names (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS marvel_publishers (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS marvel_alignments (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS marvel_genders (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS marvel_races (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    """)

    # ---------- Main heroes table ----------
    # One row per hero; only IDs + numeric columns here.

    cur.execute("""
        CREATE TABLE IF NOT EXISTS marvel_heroes (
            id INTEGER PRIMARY KEY,       -- hero id from API
            name_id INTEGER,
            publisher_id INTEGER,
            alignment_id INTEGER,
            gender_id INTEGER,
            race_id INTEGER,
            height_cm REAL,
            weight_kg REAL,
            FOREIGN KEY (name_id) REFERENCES marvel_hero_names(id),
            FOREIGN KEY (publisher_id) REFERENCES marvel_publishers(id),
            FOREIGN KEY (alignment_id) REFERENCES marvel_alignments(id),
            FOREIGN KEY (gender_id) REFERENCES marvel_genders(id),
            FOREIGN KEY (race_id) REFERENCES marvel_races(id)
        )
    """)

    # ---------- One-row-per-hero powerstats ----------
    # hero_id is PRIMARY KEY: each hero appears at most once
    # in this table (no hero_id duplicated 6 times).

    cur.execute("""
        CREATE TABLE IF NOT EXISTS marvel_powerstats (
            hero_id INTEGER PRIMARY KEY,
            intelligence INTEGER,
            strength INTEGER,
            speed INTEGER,
            durability INTEGER,
            power INTEGER,
            combat INTEGER,
            FOREIGN KEY (hero_id) REFERENCES marvel_heroes(id)
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_marvel_tables()
    print("Marvel tables created (or already exist) in final_project.db")
