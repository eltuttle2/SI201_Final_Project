from marvel_analysis import calculate_power_index, calculate_alignment_averages


def write_marvel_results(output_path="marvel_results.txt"):
    """
    Write a human-readable summary of Marvel calculations to a text file.
    Includes:
      - Top 10 heroes by power index
      - Average powerstats by alignment
    """
    power_list = calculate_power_index()
    alignment_avgs = calculate_alignment_averages()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("Top 10 Heroes by Power Index\n")
        f.write("----------------------------------------\n")
        top10 = power_list[:10]
        for hero_id, name, pi in top10:
            f.write(f"{hero_id:4d}  {name:25s}  power_index = {pi:.2f}\n")

        f.write("\n\nAverage Powerstats by Alignment\n")
        f.write("----------------------------------------\n")

        stat_names = ["intelligence", "strength", "speed", "durability", "power", "combat"]
        for alignment, stats in alignment_avgs:
            f.write(f"\nAlignment: {alignment}\n")
            for s in stat_names:
                val = stats[s]
                if val is None:
                    f.write(f"  {s:12s}: None\n")
                else:
                    f.write(f"  {s:12s}: {val:.2f}\n")

    print(f"Wrote Marvel calculation results to {output_path}")


if __name__ == "__main__":
    write_marvel_results()
