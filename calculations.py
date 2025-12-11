import sqlite3

DB_NAME = "final_project.db"

def calculate_character_stats(db_path=DB_NAME):
    """
    calculates simple stats about disney characters.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT c.name, COUNT(m.media_id) AS count
        FROM characters c
        LEFT JOIN mediaappearances m
        ON c.id = m.character_id
        GROUP BY c.id
        ORDER BY count DESC;
    """)
    results = cur.fetchall()

    total_characters = len(results)
    total_appearances = sum(row[1] for row in results)
    avg_appearances = total_appearances / total_characters if total_characters else 0

    top_10 = results[:10]

    # write file
    with open("calculated_stats.txt", "w") as f:
        f.write("character media appearance statistics\n")
        f.write("--------------------------------------\n\n")
        f.write(f"total characters analyzed: {total_characters}\n")
        f.write(f"average number of media appearances: {avg_appearances:.2f}\n\n")
        f.write("top 10 characters by media appearances:\n")
        for name, count in top_10:
            f.write(f"- {name}: {count} appearances\n")

    conn.close()

    return {
        "total_characters": total_characters,
        "avg_appearances": avg_appearances,
        "top_10": top_10
    }


def calculate_media_spread(db_path=DB_NAME):
    """
    calculates media spread score for each character (0–5).
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT c.name,
            (CASE WHEN EXISTS(SELECT 1 FROM mediaappearances m WHERE m.character_id = c.id AND m.media_type='films') THEN 1 ELSE 0 END +
             CASE WHEN EXISTS(SELECT 1 FROM mediaappearances m WHERE m.character_id = c.id AND m.media_type='shortFilms') THEN 1 ELSE 0 END +
             CASE WHEN EXISTS(SELECT 1 FROM mediaappearances m WHERE m.character_id = c.id AND m.media_type='tvShows') THEN 1 ELSE 0 END +
             CASE WHEN EXISTS(SELECT 1 FROM mediaappearances m WHERE m.character_id = c.id AND m.media_type='videoGames') THEN 1 ELSE 0 END +
             CASE WHEN EXISTS(SELECT 1 FROM mediaappearances m WHERE m.character_id = c.id AND m.media_type='parkAttractions') THEN 1 ELSE 0 END)
            AS spread
        FROM characters c
        ORDER BY spread DESC
        LIMIT 10;
    """)

    results = cur.fetchall()
    conn.close()
    return results


if __name__ == "__main__":
    calculate_character_stats()
    calculate_media_spread()
    print("calculated stats written to calculated_stats.txt")
