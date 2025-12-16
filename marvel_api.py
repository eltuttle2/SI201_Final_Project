import sqlite3
import requests

DB_NAME = "final_project.db"
ALL_URL = "https://akabab.github.io/superhero-api/api/all.json"


def get_connection():
    """
    Return a connection to the SQLite database.
    """
    return sqlite3.connect(DB_NAME)


def fetch_all_heroes():
    """
    Call the Akabab Superhero API /all.json endpoint and return the list of heroes.
    """
    print(f"Requesting all heroes from {ALL_URL} ...")
    resp = requests.get(ALL_URL)
    resp.raise_for_status()
    data = resp.json()
    print(f"Got {len(data)} heroes from API.")
    return data


def get_existing_hero_ids(conn):
    """
    Return a set of hero IDs already stored in marvel_heroes.
    """
    cur = conn.cursor()
    cur.execute("SELECT id FROM marvel_heroes")
    return {row[0] for row in cur.fetchall()}


def choose_new_heroes(all_heroes, existing_ids, max_new=25):
    """
    From all_heroes, select heroes that are NOT yet in the database,
    up to max_new heroes.
    """
    new_heroes = []

    for hero in all_heroes:
        hero_id = hero.get("id")
        if hero_id is None:
            continue

        if hero_id in existing_ids:
            continue

        new_heroes.append(hero)

        if len(new_heroes) >= max_new:
            break

    print(f"Selected {len(new_heroes)} new heroes to insert.")
    return new_heroes


def parse_int(value):
    """
    Safely parse an integer, returning None if parsing fails.
    """
    if value is None:
        return None
    if isinstance(value, int):
        return value
    try:
        text = str(value).strip()
        if text == "":
            return None
        return int(text)
    except ValueError:
        return None


def parse_float_from_cm_list(height_list):
    """
    The API gives height as something like ["5'9", "175 cm"].
    We try to parse the cm value as a float.
    """
    if not height_list:
        return None
    for item in height_list:
        if item is None:
            continue
        text = str(item).strip()
        if "cm" in text:
            text = text.replace("cm", "").strip()
        if text in ("", "-"):
            continue
        try:
            return float(text)
        except ValueError:
            continue
    return None


def parse_float_from_kg_list(weight_list):
    """
    The API gives weight as something like ["180 lb", "81 kg"].
    We try to parse the kg value as a float.
    """
    if not weight_list:
        return None
    for item in weight_list:
        if item is None:
            continue
        text = str(item).strip()
        if "kg" in text:
            text = text.replace("kg", "").strip()
        if text in ("", "-"):
            continue
        try:
            return float(text)
        except ValueError:
            continue
    return None


def get_or_create_lookup_id(cur, table_name, name):
    """
    Put a string into a lookup table and return its integer ID.
    If name is empty or "-", returns None and does not create a row.
    """
    if name is None:
        return None

    text = str(name).strip()
    if text == "" or text == "-":
        return None

    cur.execute(f"SELECT id FROM {table_name} WHERE name = ?", (text,))
    row = cur.fetchone()
    if row is not None:
        return row[0]

    cur.execute(f"INSERT INTO {table_name} (name) VALUES (?)", (text,))
    return cur.lastrowid


def split_hero_data(cur, hero):
    """
    Given one hero JSON object, build:

        hero_row:       for marvel_heroes
        powerstats_row: for marvel_powerstats (one row per hero)

    This function also fills the lookup tables for names, publishers,
    alignments, genders, and races.
    """
    hero_id = hero.get("id")
    if hero_id is None:
        return None, None

    name = hero.get("name")
    biography = hero.get("biography", {})
    appearance = hero.get("appearance", {})
    powerstats = hero.get("powerstats", {})

    publisher = biography.get("publisher")
    alignment = biography.get("alignment")
    gender = appearance.get("gender")
    race = appearance.get("race")

    height_list = appearance.get("height")
    weight_list = appearance.get("weight")

    height_cm = parse_float_from_cm_list(height_list)
    weight_kg = parse_float_from_kg_list(weight_list)

    # Map repeated strings into lookup tables
    name_id = get_or_create_lookup_id(cur, "marvel_hero_names", name)
    publisher_id = get_or_create_lookup_id(cur, "marvel_publishers", publisher)

    # For alignment, if missing we treat as "unknown" so we still have a category
    if alignment is None or str(alignment).strip() == "":
        alignment_value = "unknown"
    else:
        alignment_value = alignment
    alignment_id = get_or_create_lookup_id(cur, "marvel_alignments", alignment_value)

    gender_id = get_or_create_lookup_id(cur, "marvel_genders", gender)
    race_id = get_or_create_lookup_id(cur, "marvel_races", race)

    hero_row = (
        hero_id,
        name_id,
        publisher_id,
        alignment_id,
        gender_id,
        race_id,
        height_cm,
        weight_kg,
    )

    # One row per hero in marvel_powerstats (wide table)
    intelligence = parse_int(powerstats.get("intelligence"))
    strength = parse_int(powerstats.get("strength"))
    speed = parse_int(powerstats.get("speed"))
    durability = parse_int(powerstats.get("durability"))
    power = parse_int(powerstats.get("power"))
    combat = parse_int(powerstats.get("combat"))

    powerstats_row = (
        hero_id,
        intelligence,
        strength,
        speed,
        durability,
        power,
        combat,
    )

    return hero_row, powerstats_row


def store_marvel_data(heroes):
    """
    Insert heroes and their powerstats into the database.

    - marvel_heroes: one row per hero
    - marvel_powerstats: one row per hero (hero_id is PRIMARY KEY)

    Per run, we insert at most 25 hero rows and 25 powerstats rows.
    """
    if not heroes:
        print("No new heroes to store.")
        return

    conn = get_connection()
    cur = conn.cursor()

    hero_rows = []
    powerstats_rows = []

    for hero in heroes:
        hero_row, ps_row = split_hero_data(cur, hero)
        if hero_row is None:
            continue
        hero_rows.append(hero_row)
        powerstats_rows.append(ps_row)

    # Insert heroes
    cur.executemany(
        """
        INSERT OR IGNORE INTO marvel_heroes
        (id, name_id, publisher_id, alignment_id, gender_id, race_id, height_cm, weight_kg)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        hero_rows,
    )

    # Insert one-row-per-hero powerstats
    cur.executemany(
        """
        INSERT OR IGNORE INTO marvel_powerstats
        (hero_id, intelligence, strength, speed, durability, power, combat)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        powerstats_rows,
    )

    conn.commit()
    conn.close()

    print(f"Inserted up to {len(hero_rows)} heroes and {len(powerstats_rows)} powerstat rows.")


def main(max_new=25):
    """
    Main entry point: select up to max_new new heroes from the API
    and store them in the database.
    """
    conn = get_connection()
    existing_ids = get_existing_hero_ids(conn)
    conn.close()

    all_heroes = fetch_all_heroes()
    new_heroes = choose_new_heroes(all_heroes, existing_ids, max_new=max_new)
    store_marvel_data(new_heroes)


if __name__ == "__main__":
    # Per assignment requirement: at most 25 items per run (25 heroes -> 25 rows per table)
    main(max_new=25)
