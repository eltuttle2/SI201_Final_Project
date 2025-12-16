import sqlite3

DB_NAME = "final_project.db"

def calculate_character_stats(db_path=DB_NAME):
    """
    calculates simple stats using normalized tables:
    - total appearances per character (count of rows in character_media)
    - average appearances
    - top 10 characters by appearances
    writes results to calculated_stats.txt
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # total media appearances per character (count of join rows)
    cur.execute("""
        select c.name, count(cm.id) as total
        from characters c
        left join character_media cm on c.id = cm.character_id
        group by c.id
        order by total desc;
    """)
    results = cur.fetchall()

    total_characters = len(results)
    total_appearances = sum(row[1] for row in results)
    avg_appearances = total_appearances / total_characters if total_characters else 0

    top_10 = results[:10]

    # write to text file
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
    calculates media spread score (0-5) for each character:
    count distinct media types per character (via character_media -> media_types)
    returns top 10 characters by spread
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        select c.name,
               count(distinct cm.type_id) as spread
        from characters c
        left join character_media cm on c.id = cm.character_id
        group by c.id
        order by spread desc
        limit 10;
    """)
    results = cur.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    calculate_character_stats()
    calculate_media_spread()
    print("calculated stats written to calculated_stats.txt")
