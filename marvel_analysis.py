import sqlite3

DB_NAME = "final_project.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def calculate_power_index():
    """
    For each hero, compute a power index as the average of
    the six powerstats: intelligence, strength, speed,
    durability, power, combat.

    Uses:
      - marvel_heroes
      - marvel_hero_names
      - marvel_powerstats (one row per hero)

    Returns:
      list of (hero_id, name, power_index), sorted descending.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT h.id,
               n.name,
               p.intelligence,
               p.strength,
               p.speed,
               p.durability,
               p.power,
               p.combat
        FROM marvel_heroes AS h
        JOIN marvel_hero_names AS n
            ON h.name_id = n.id
        JOIN marvel_powerstats AS p
            ON h.id = p.hero_id
    """)

    rows = cur.fetchall()
    conn.close()

    results = []
    for row in rows:
        hero_id = row[0]
        name = row[1]
        stats = row[2:]
        values = [v for v in stats if v is not None]
        if not values:
            continue
        avg_power = sum(values) / float(len(values))
        results.append((hero_id, name, avg_power))

    results.sort(key=lambda x: x[2], reverse=True)
    return results


def calculate_alignment_averages():
    """
    Compute average powerstats for each alignment (good, bad, neutral, etc.).

    Uses:
      - marvel_heroes (alignment_id)
      - marvel_alignments (alignment names)
      - marvel_powerstats (one row per hero)

    Returns:
        A list of (alignment, stats_dict), where stats_dict has keys:
            "intelligence", "strength", "speed",
            "durability", "power", "combat"
        and values are the average value for that stat and alignment.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT a.name AS alignment,
               p.intelligence,
               p.strength,
               p.speed,
               p.durability,
               p.power,
               p.combat
        FROM marvel_heroes AS h
        JOIN marvel_alignments AS a
            ON h.alignment_id = a.id
        JOIN marvel_powerstats AS p
            ON h.id = p.hero_id
    """)

    rows = cur.fetchall()
    conn.close()

    stat_order = ["intelligence", "strength", "speed", "durability", "power", "combat"]

    # alignment -> {stat_name: [values]}
    stats_by_align = {}
    for row in rows:
        alignment = row[0]
        values = row[1:]

        if alignment not in stats_by_align:
            stats_by_align[alignment] = {name: [] for name in stat_order}

        for name, v in zip(stat_order, values):
            if v is not None:
                stats_by_align[alignment][name].append(v)

    # alignment -> {stat_name: avg_value}
    results = []
    for alignment, stat_lists in stats_by_align.items():
        stats_dict = {}
        for name in stat_order:
            vals = stat_lists[name]
            if not vals:
                stats_dict[name] = None
            else:
                stats_dict[name] = sum(vals) / float(len(vals))
        results.append((alignment, stats_dict))

    return results


if __name__ == "__main__":
    power_list = calculate_power_index()
    print("Top 10 heroes by power index:")
    for hero_id, name, pi in power_list[:10]:
        print(hero_id, name, pi)

    print("\nAverage powerstats by alignment:")
    alignment_avgs = calculate_alignment_averages()
    for alignment, stats in alignment_avgs:
        print(f"\nAlignment: {alignment}")
        for stat_name in ["intelligence", "strength", "speed", "durability", "power", "combat"]:
            value = stats[stat_name]
            if value is None:
                print(f"  {stat_name}: None")
            else:
                print(f"  {stat_name}: {value:.2f}")
