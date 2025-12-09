"""
visualizations.py
creates a bar chart for total appearances and a scatter plot for media spread vs total appearances
"""

import matplotlib.pyplot as plt
import sqlite3
from calculations import calculate_character_stats

def visualize_total_appearances():
    """
    bar chart for top 10 characters by total media appearances
    """
    stats = calculate_character_stats()
    top_10 = stats["top_10"]
    names = [x[0] for x in top_10]
    counts = [x[1] for x in top_10]

    plt.figure(figsize=(12,6))
    plt.bar(names, counts, color='skyblue')
    plt.xticks(rotation=45, ha='right')
    plt.title("Top 10 Disney Characters by Total Media Appearances")
    plt.ylabel("Number of Appearances")
    plt.tight_layout()
    plt.show()

def get_media_spread_and_total(db_path="disney.db"):
    """
    gets media spread (0-5) and total appearances for each character
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        select c.name,
               (case when exists(select 1 from mediaappearances m where m.character_id = c.id and m.media_type='films') then 1 else 0 end +
                case when exists(select 1 from mediaappearances m where m.character_id = c.id and m.media_type='shortFilms') then 1 else 0 end +
                case when exists(select 1 from mediaappearances m where m.character_id = c.id and m.media_type='tvShows') then 1 else 0 end +
                case when exists(select 1 from mediaappearances m where m.character_id = c.id and m.media_type='videoGames') then 1 else 0 end +
                case when exists(select 1 from mediaappearances m where m.character_id = c.id and m.media_type='parkAttractions') then 1 else 0 end
               ) as spread,
               count(m.media_id) as total_appearances
        from characters c
        left join mediaappearances m on c.id = m.character_id
        group by c.id
        order by total_appearances desc
        limit 30;
    """)

    results = cur.fetchall()
    conn.close()
    return results

def visualize_media_spread_vs_total():
    """
    scatter plot showing media spread vs total appearances
    """
    data = get_media_spread_and_total()
    spreads = [x[1] for x in data]
    totals = [x[2] for x in data]
    names = [x[0] for x in data]

    plt.figure(figsize=(10,6))
    plt.scatter(spreads, totals, color='orange')

    # label points above with small offset
    for i, name in enumerate(names):
        plt.text(spreads[i], totals[i]+1, name, fontsize=8, ha='center', rotation=0)

    plt.xlabel("Media Spread (0-5)")
    plt.ylabel("Total Appearances")
    plt.title("Media Spread vs Total Appearances for Top Disney Characters")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    visualize_total_appearances()
    visualize_media_spread_vs_total()
