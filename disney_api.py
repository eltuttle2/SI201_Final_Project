import requests
import sqlite3

DB_NAME = "final_project.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def setup_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY,
            name TEXT,
            image_url TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS media_types (
            type_id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_name TEXT UNIQUE
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS media_titles (
            title_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS character_media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER,
            type_id INTEGER,
            title_id INTEGER,
            UNIQUE(character_id, type_id, title_id)
        );
    """)

    conn.commit()
    conn.close()

def seed_media_types(cur):
    types = ["films", "shortFilms", "tvShows", "videoGames", "parkAttractions"]
    for t in types:
        cur.execute(
            "INSERT OR IGNORE INTO media_types (type_name) VALUES (?);",
            (t,)
        )

def get_existing_character_ids(cur):
    cur.execute("SELECT id FROM characters;")
    return {r[0] for r in cur.fetchall()}

def get_type_id(type_name, cur):
    cur.execute(
        "SELECT type_id FROM media_types WHERE type_name = ?;",
        (type_name,)
    )
    return cur.fetchone()[0]

def get_title_id(title, cur):
    cur.execute(
        "SELECT title_id FROM media_titles WHERE title = ?;",
        (title,)
    )
    row = cur.fetchone()
    if row:
        return row[0]

    cur.execute(
        "INSERT INTO media_titles (title) VALUES (?);",
        (title,)
    )
    return cur.lastrowid

def store_characters():
    setup_database()
    conn = get_connection()
    cur = conn.cursor()

    seed_media_types(cur)
    existing = get_existing_character_ids(cur)

    url = "https://api.disneyapi.dev/character"
    page = 1

    character_added = 0
    media_added = 0
    titles_added = 0

    MAX_PER_RUN = 25

    while character_added < MAX_PER_RUN and media_added < MAX_PER_RUN:
        response = requests.get(f"{url}?page={page}")
        if response.status_code != 200:
            break

        data = response.json()
        if "data" not in data or not data["data"]:
            break

        for character in data["data"]:
            if character_added >= MAX_PER_RUN:
                break

            cid = character["_id"]
            if cid in existing:
                continue

            cur.execute("""
                INSERT OR IGNORE INTO characters (id, name, image_url)
                VALUES (?, ?, ?);
            """, (cid, character.get("name"), character.get("imageUrl")))

            character_added += 1
            existing.add(cid)

            media_lists = {
                "films": character.get("films", []),
                "shortFilms": character.get("shortFilms", []),
                "tvShows": character.get("tvShows", []),
                "videoGames": character.get("videoGames", []),
                "parkAttractions": character.get("parkAttractions", [])
            }

            for m_type, titles in media_lists.items():
                if media_added >= MAX_PER_RUN:
                    break

                type_id = get_type_id(m_type, cur)

                for title in titles:
                    if media_added >= MAX_PER_RUN:
                        break

                    # insert title if needed
                    before = titles_added
                    title_id = get_title_id(title, cur)
                    if cur.rowcount > 0:
                        titles_added += 1
                        if titles_added > MAX_PER_RUN:
                            break

                    cur.execute("""
                        INSERT OR IGNORE INTO character_media
                        (character_id, type_id, title_id)
                        VALUES (?, ?, ?);
                    """, (cid, type_id, title_id))

                    if cur.rowcount > 0:
                        media_added += 1

        page += 1

    conn.commit()
    conn.close()

    print("Run summary:")
    print("characters added:", character_added)
    print("media rows added:", media_added)
    print("titles added:", titles_added)

if __name__ == "__main__":
    store_characters()
