import requests
import sqlite3

DB_NAME = "final_project.db"

def setup_database():
    """
    sets up the database tables if they do not exist.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # characters table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY,
            name TEXT,
            image_url TEXT
        );
    """)

    # media table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mediaappearances (
            media_id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER,
            media_type TEXT,
            media_title TEXT
        );
    """)

    conn.commit()
    conn.close()


def get_existing_character_ids():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT id FROM characters;")
    rows = cur.fetchall()
    conn.close()

    return set(row[0] for row in rows)


def store_characters():
    """
    gets 25 NEW characters each run.
    """
    setup_database()
    existing = get_existing_character_ids()

    url = "https://api.disneyapi.dev/character"
    page = 1
    added = 0

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    while added < 25:
        response = requests.get(url + "?page=" + str(page))
        data = response.json()

        if "data" not in data or len(data["data"]) == 0:
            break

        for character in data["data"]:
            cid = character["_id"]

            # skip if already saved
            if cid in existing:
                continue

            # insert character
            cur.execute("""
                INSERT INTO characters (id, name, image_url)
                VALUES (?, ?, ?);
            """, (cid, character.get("name"), character.get("imageUrl")))

            media_types = {
                "films": character.get("films", []),
                "shortFilms": character.get("shortFilms", []),
                "tvShows": character.get("tvShows", []),
                "videoGames": character.get("videoGames", []),
                "parkAttractions": character.get("parkAttractions", [])
            }

            for m_type, titles in media_types.items():
                for title in titles:
                    cur.execute("""
                        INSERT INTO mediaappearances (character_id, media_type, media_title)
                        VALUES (?, ?, ?);
                    """, (cid, m_type, title))

            added += 1
            existing.add(cid)

            if added >= 25:
                break

        page += 1

    conn.commit()
    conn.close()

    print(f"Stored {added} new Disney characters in {DB_NAME}")


if __name__ == "__main__":
    store_characters()
