import os
import matplotlib.pyplot as plt
from marvel_analysis import calculate_power_index, calculate_alignment_averages


def get_output_path(filename):
    """
    Save figures into the same folder as this file.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, filename)


def plot_top_power_index():
    """
    Bar chart of top 10 heroes by power index.
    Also save the figure as 'marvel_top_power_index.png'.
    """
    results = calculate_power_index()
    top10 = results[:10]

    if not top10:
        print("No heroes found for top power index plot.")
        return

    names = [row[1] for row in top10]
    scores = [row[2] for row in top10]

    plt.figure()
    plt.bar(range(len(names)), scores)
    plt.xticks(range(len(names)), names, rotation=45, ha="right")
    plt.ylabel("Power index (average of 6 stats)")
    plt.title("Top 10 heroes by power index")
    plt.tight_layout()

    out_path = get_output_path("marvel_top_power_index.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print("Saved bar chart to:", out_path)

    plt.show()
    plt.close()


def plot_alignment_line():
    """
    Line chart of average powerstats by alignment.

    x-axis: powerstats
    y-axis: average value
    One line per alignment (good, bad, neutral, etc.).
    Also save the figure as 'marvel_alignment_powerstats.png'.
    """
    alignment_avgs = calculate_alignment_averages()
    if not alignment_avgs:
        print("No data for alignment line plot.")
        return

    stat_names = ["intelligence", "strength", "speed",
                  "durability", "power", "combat"]
    x_positions = list(range(len(stat_names)))

    plt.figure()

    for alignment, stats in alignment_avgs:
        y_values = []
        for s in stat_names:
            v = stats[s]
            if v is None:
                y_values.append(0.0)
            else:
                y_values.append(float(v))

        plt.plot(x_positions, y_values, marker="o", label=alignment)

    plt.xticks(x_positions, [s.capitalize() for s in stat_names])
    plt.xlabel("Powerstat")
    plt.ylabel("Average value")
    plt.title("Average powerstats by alignment")
    plt.legend(title="Alignment")
    plt.tight_layout()

    out_path = get_output_path("marvel_alignment_powerstats.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print("Saved line chart to:", out_path)

    plt.show()
    plt.close()


if __name__ == "__main__":
    plot_top_power_index()
    plot_alignment_line()
