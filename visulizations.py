import matplotlib.pyplot as plt
import sqlite3
from calculations import calculate_character_stats, DB_NAME

def visualize_total_appearances():
    stats = calculate_character_stats()
    top_10 = stats["top_10"]

    names = [x[0] for x in top_10]
    counts = [x[1] for x in top_10]

    plt.figure(figsize=(12,6))
    plt.bar(names, counts)
    plt.xticks(rotation=45, ha='right')
    plt.title("Top 10 Disney Characters by Total Media Appearances")
    plt.ylabel("Number of Appearances")
    plt.tight_layout()
    plt.show()


def get_media_spread_and_total(db_path=DB_NAME):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT c.name,
               (CASE WHEN EXISTS(SELECT 1 FROM mediaappearances m WHERE m.character_id = c.id AND m.media_type='films') THEN 1 ELSE 0 END +
                CASE WHEN EXISTS(SELECT 1 FROM mediaappearances m WHERE m.character_id = c.id AND m.media_type='shortFilms') THEN 1 ELSE 0 END +
                CASE WHEN EXISTS(SELECT 1 FROM mediaappearances m WHERE m.character_id = c.id AND m.media_type='tvShows') THEN 1 ELSE 0 END +
                CASE WHEN EXISTS(SELECT 1 FROM mediaappearances m WHERE m.character_id = c.id AND m.media_type='videoGames') THEN 1 ELSE 0 END +
                CASE WHEN EXISTS(SELECT 1 FROM mediaappearances m WHERE m.character_id = c.id AND m.media_type='parkAttractions') THEN 1 ELSE 0 END)
               AS spread,
               COUNT(m.media_id) AS total_appearances
        FROM characters c
        LEFT JOIN mediaappearances m ON c.id = m.character_id
        GROUP BY c.id
        ORDER BY total_appearances DESC
        LIMIT 30;
    """)

    results = cur.fetchall()
    conn.close()
    return results


def visualize_media_spread_vs_total():
    data = get_media_spread_and_total()
    spreads = [x[1] for x in data]
    totals = [x[2] for x in data]
    names = [x[0] for x in data]

    plt.figure(figsize=(10,6))
    plt.scatter(spreads, totals)

    for i, name in enumerate(names):
        plt.text(spreads[i], totals[i] + 1, name, fontsize=8, ha='center')

    plt.xlabel("Media Spread (0–5)")
    plt.ylabel("Total Appearances")
    plt.title("Media Spread vs Total Appearances")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    visualize_total_appearances()
    visualize_media_spread_vs_total()
