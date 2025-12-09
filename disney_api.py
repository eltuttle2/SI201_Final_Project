import requests
import sqlite3

def setup_database():
    """
    sets up the database tables if they do not exist.
    kept very simple.
    """
    conn = sqlite3.connect("disney.db")
    cur = conn.cursor()

    # characters table
    cur.execute("""
        create table if not exists characters (
            id integer primary key,
            name text,
            image_url text
        );
    """)

    # media table
    cur.execute("""
        create table if not exists mediaappearances (
            media_id integer primary key autoincrement,
            character_id integer,
            media_type text,
            media_title text
        );
    """)

    conn.commit()
    conn.close()


def get_existing_character_ids():
    conn = sqlite3.connect("disney.db")
    cur = conn.cursor()

    cur.execute("select id from characters;")
    rows = cur.fetchall()

    conn.close()

    # convert to a set so we can check fast
    ids = set()
    for row in rows:
        ids.add(row[0])
    return ids


def store_characters():
    """
    gets up to 25 characters from the disney api
    and saves them into the database.
    """
    setup_database()
    existing = get_existing_character_ids()

    url = "https://api.disneyapi.dev/character"
    page = 1
    added = 0

    conn = sqlite3.connect("disney.db")
    cur = conn.cursor()

    while added < 25:
        response = requests.get(url + "?page=" + str(page))
        data = response.json()

        if "data" not in data:
            break

        for character in data["data"]:
            cid = character["_id"]

            # skip if we already saved it
            if cid in existing:
                continue

            # insert character
            cur.execute(
                "insert into characters (id, name, image_url) values (?, ?, ?);",
                (cid, character.get("name"), character.get("imageUrl"))
            )

            # simple loop for media lists
            media_types = {
                "films": character.get("films", []),
                "shortFilms": character.get("shortFilms", []),
                "tvShows": character.get("tvShows", []),
                "videoGames": character.get("videoGames", []),
                "parkAttractions": character.get("parkAttractions", [])
            }

            for m_type in media_types:
                titles = media_types[m_type]
                for title in titles:
                    cur.execute(
                        "insert into mediaappearances (character_id, media_type, media_title) values (?, ?, ?);",
                        (cid, m_type, title)
                    )

            added += 1
            existing.add(cid)

            if added >= 25:
                break

        page += 1

    conn.commit()
    conn.close()

    print("stored", added, "new disney characters in disney.db")


if __name__ == "__main__":
    store_characters()
