import sqlite3

def calculate_character_stats(db_path="disney.db"):
    """
    calculates simple stats about disney characters.
    returns total appearances per character and top 10.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # total media appearances per character
    cur.execute("""
        select c.name, count(m.media_id) as count
        from characters c
        left join mediaappearances m
        on c.id = m.character_id
        group by c.id
        order by count desc;
    """)
    results = cur.fetchall()

    total_characters = len(results)
    total_appearances = sum([row[1] for row in results])
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


def calculate_media_spread(db_path="disney.db"):
    """
    calculates media spread score for each character (0-5)
    1 point for each media type the character appears in
    returns top 10 characters by media spread
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
        ) as spread
        from characters c
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
