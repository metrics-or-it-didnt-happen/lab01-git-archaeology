"""Git Archaeology - mining commit history for fun and metrics."""

import subprocess
import sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Times New Roman"
import numpy as np

def run_git_log(repo_path: str) -> list[dict]:
    """Run git log and parse output into list of commit dicts."""
    separator = "|"
    fmt = f"%H{separator}%an{separator}%ae{separator}%ad{separator}%s"

    result = subprocess.run(
        ["git", "log", f"--format={fmt}", "--date=short"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )

    commits = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split(separator, maxsplit=4)
        if len(parts) == 5:
            commits.append({
                "hash": parts[0],
                "author": parts[1],
                "email": parts[2],
                "date": parts[3],
                "message": parts[4],
            })
    return commits

def top_authors(commits: list[dict], n: int = 10) -> list[tuple[str, int, float]]:
    """Return top N authors by commit count."""
    total = len(commits)
    authors_lst = [c["author"] for c in commits]
    authors_couter = Counter(authors_lst)
    
    result_lst = []
    for author, count in authors_couter.most_common(n):
        result_lst.append((author, count, count/total*100))  
    return result_lst

def monthly_activity(commits: list[dict]) -> dict[str, int]:
    """Return commit count per month (YYYY-MM -> count)."""
    activity = defaultdict(int)
    for c in commits:
        key = c["date"][:7]
        activity[key] += 1

    activity = dict(sorted(activity.items(), reverse=True))
    return activity

def longest_gap(commits: list[dict]) -> tuple[int, str, str]:
    """Return longest gap between commits (days, start_date, end_date)."""
    dates_str = sorted(c["date"] for c in commits)
    dates = [datetime.strptime(d, "%Y-%m-%d") for d in dates_str]

    max_gap = -1
    start_date = None
    end_date = None
    prev_date = dates[0]

    for date in dates:
        gap = (date - prev_date).days
        if gap > max_gap:
            max_gap = gap
            start_date = prev_date.strftime("%Y-%m-%d")
            end_date = date.strftime("%Y-%m-%d")
        prev_date = date

    return max_gap, start_date, end_date

def save_report_csv(filepath: str, authors, activity, gap):
    """Save report to CSV file."""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("Author,Commits,Percent\n")
        for name, count, pct in authors:
            f.write(f"{name},{count},{pct:.1f}\n")

        f.write("\nMonth,Commits\n")
        for month, count in activity.items():
            f.write(f"{month},{count}\n")

        f.write("\nDays,Start,End\n")
        gap_days, gap_start, gap_end = gap
        f.write(f"{gap_days},{gap_start},{gap_end}\n")

def monthly_plot(commits: list[dict], repo_name: str):
    activity = defaultdict(int)
    for c in commits:
        key = c["date"][:7]
        activity[key] += 1
    activity = dict(sorted(activity.items()))

    months = list(activity.keys())
    counts = list(activity.values())
    colors = ["red" if m.endswith('01') else 'green' for m in months]

    labels = []
    for m in months:
        year, month = m.split("-")
        if month == "01": labels.append(year)
        else: labels.append("")

    plt.figure(figsize=(14, 5))
    plt.bar(months, counts, color=colors)

    plt.xticks(months, labels)
    plt.xlabel("Miesiąc")
    plt.ylabel("Liczba commitów")
    plt.title(f"Aktywność projektu: {repo_name}")

    plt.tight_layout()
    plt.savefig("activity_chart.png", dpi=150)
    
def heatmap_plot(repo_path: str):
    result = subprocess.run(
        ["git", "log", "--date=iso", "--format=%ad"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )

    full_dates = result.stdout.strip().split("\n")
    heatmap = np.zeros((7, 24), dtype=int)
    
    for date in full_dates:
        dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z")
        weekday = dt.weekday()
        hour = dt.hour           
        heatmap[weekday, hour] += 1

    plt.figure(figsize=(10, 6))
    plt.imshow(heatmap, cmap="YlOrRd", aspect="auto")
    plt.colorbar(label="Liczba commitów")

    plt.yticks(range(7), ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Niedz"])
    plt.xticks(range(0, 24))
    plt.xlabel("Godzina dnia")
    plt.title(f"Heatmapa aktywności commitów dla projektu: {Path(repo_path).name}")

    plt.tight_layout()
    plt.savefig("heatmap.png", dpi=150) 

def main():
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    repo_path = str(Path(repo_path).resolve())

    print(f"Analizuję repozytorium: {repo_path}")
    print("=" * 60)

    commits = run_git_log(repo_path)
    print(f"Znaleziono {len(commits)} commitów\n")

    # Top autorzy
    authors = top_authors(commits)
    print("TOP 10 AUTORÓW:")
    print("-" * 40)
    for name, count, pct in authors:
        print(f"  {name:<30} {count:>5} ({pct:.1f}%)")

    # Aktywność miesięczna
    activity = monthly_activity(commits)
    print(f"\nAKTYWNOŚĆ MIESIĘCZNA (ostatnie 12 miesięcy):")
    print("-" * 40)
    for month, count in list(activity.items())[:12]:
        print(f"  {month}: {count}")

    # Najdłuższy gap
    gap_days, gap_start, gap_end = longest_gap(commits)
    print(f"\nNAJDŁUŻSZA PRZERWA: {gap_days} dni ({gap_start} → {gap_end})")

    # Zapis do CSV
    save_report_csv("report.csv", authors, activity, (gap_days, gap_start, gap_end))
    print(f"\nRaport zapisany do: report.csv\n")

    # Wykres słupkowy/liniowy: liczba commitów na miesiąc 
    repo_name = Path(repo_path).name
    monthly_plot(commits, repo_name)
    print(f"Wykres aktywności zapisany do: activity_chart.png")

    # Wykres heatmap (dzień tygodnia × godzina dnia)
    heatmap_plot(repo_path)
    print(f"\nHeatmapa zapisana do: heatmap.png")


if __name__ == "__main__":
    main()