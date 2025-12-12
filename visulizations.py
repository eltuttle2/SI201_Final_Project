import matplotlib.pyplot as plt
import sqlite3
from calculations import calculate_character_stats, DB_NAME

def visualize_total_appearances():
    """bar chart for top 10 characters by total media appearances"""
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

def get_media_spread_and_total(db_path=DB_NAME, limit=30):
    """
    returns list of (name, spread, total_appearances) for characters
    spread = distinct media types, total_appearances = total join rows
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(f"""
        select c.name,
               count(distinct cm.type_id) as spread,
               count(cm.id) as total_appearances
        from characters c
        left join character_media cm on c.id = cm.character_id
        group by c.id
        order by total_appearances desc
        limit {limit};
    """)
    results = cur.fetchall()
    conn.close()
    return results

def visualize_media_spread_vs_total():
    """scatter plot showing media spread vs total appearances"""
    data = get_media_spread_and_total()
    spreads = [x[1] for x in data]
    totals = [x[2] for x in data]
    names = [x[0] for x in data]

    plt.figure(figsize=(10,6))
    plt.scatter(spreads, totals)

    # label points above with small offset, horizontal labels
    for i, name in enumerate(names):
        plt.text(spreads[i], totals[i] + 0.8, name, fontsize=8, ha='center', rotation=0)

    plt.xlabel("media spread (0-5)")
    plt.ylabel("total appearances")
    plt.title("media spread vs total appearances for top disney characters")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    visualize_total_appearances()
    visualize_media_spread_vs_total()
