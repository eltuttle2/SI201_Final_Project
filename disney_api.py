import requests
import sqlite3

# shared db name
DB_NAME = "final_project.db"

def get_connection():
    """return a sqlite connection to the shared db."""
    return sqlite3.connect(DB_NAME)

def setup_database():
    """
    sets up normalized database tables:
    - characters
    - media_types
    - media_titles
    - character_media (join table)
    keeps everything simple and lowercase.
    """
    conn = get_connection()
    cur = conn.cursor()

    # characters table
    cur.execute("""
        create table if not exists characters (
            id integer primary key,
            name text,
            image_url text
        );
    """)

    # media types table (one row per media type)
    cur.execute("""
        create table if not exists media_types (
            type_id integer primary key autoincrement,
            type_name text unique
        );
    """)

    # media titles table (one row per title)
    cur.execute("""
        create table if not exists media_titles (
            title_id integer primary key autoincrement,
            title text unique
        );
    """)

    # join table: which character appears in which title and which type
    cur.execute("""
        create table if not exists character_media (
            id integer primary key autoincrement,
            character_id integer,
            type_id integer,
            title_id integer,
            unique(character_id, type_id, title_id)
        );
    """)

    conn.commit()
    conn.close()

def seed_media_types():
    """ensure the five common media types exist in media_types table."""
    types = ["films", "shortFilms", "tvShows", "videoGames", "parkAttractions"]
    conn = get_connection()
    cur = conn.cursor()
    for t in types:
        cur.execute("insert or ignore into media_types (type_name) values (?);", (t,))
    conn.commit()
    conn.close()

def get_existing_character_ids():
    """return set of character ids already in database."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("select id from characters;")
    rows = cur.fetchall()
    conn.close()
    return {r[0] for r in rows}

def get_type_id(type_name, cur):
    """return the type_id for a media type, inserting if missing."""
    cur.execute("select type_id from media_types where type_name = ?;", (type_name,))
    r = cur.fetchone()
    if r:
        return r[0]
    cur.execute("insert into media_types (type_name) values (?);", (type_name,))
    return cur.lastrowid

def get_title_id(title, cur):
    """return the title_id for a media title, inserting if missing."""
    cur.execute("select title_id from media_titles where title = ?;", (title,))
    r = cur.fetchone()
    if r:
        return r[0]
    cur.execute("insert into media_titles (title) values (?);", (title,))
    return cur.lastrowid

def store_characters():
    """
    fetch up to 25 new characters from the disney api and store them normalized.
    - characters go to characters
    - media types go to media_types (seeded)
    - titles go to media_titles
    - character appearances go to character_media (join table)
    duplicates are avoided by checking existing ids and unique constraints.
    """
    setup_database()
    seed_media_types()
    existing = get_existing_character_ids()

    url = "https://api.disneyapi.dev/character"
    page = 1
    added = 0

    conn = get_connection()
    cur = conn.cursor()

    while added < 25:
        response = requests.get(url + "?page=" + str(page))
        if response.status_code != 200:
            break
        data = response.json()
        if "data" not in data or not data["data"]:
            break

        for character in data["data"]:
            cid = character.get("_id")
            if cid in existing:
                continue

            # insert character
            cur.execute(
                "insert or ignore into characters (id, name, image_url) values (?, ?, ?);",
                (cid, character.get("name"), character.get("imageUrl"))
            )

            # for each media type and title, insert into media_titles and character_media
            media_lists = {
                "films": character.get("films", []),
                "shortFilms": character.get("shortFilms", []),
                "tvShows": character.get("tvShows", []),
                "videoGames": character.get("videoGames", []),
                "parkAttractions": character.get("parkAttractions", [])
            }

            for m_type, titles in media_lists.items():
                if not titles:
                    continue
                # get type_id (should exist from seed or insert)
                type_id = get_type_id(m_type, cur)
                for title in titles:
                    # get or insert title
                    title_id = get_title_id(title, cur)
                    # insert into join table, unique constraint prevents duplicates
                    cur.execute("""
                        insert or ignore into character_media (character_id, type_id, title_id)
                        values (?, ?, ?);
                    """, (cid, type_id, title_id))

            added += 1
            existing.add(cid)

            if added >= 25:
                break

        page += 1

    conn.commit()
    conn.close()
    print(f"stored {added} new disney characters in {DB_NAME}")

if __name__ == "__main__":
    store_characters()
