#!/usr/bin/env python3
"""Git Archaeology - mining commit history for fun and metrics."""

import csv
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

def git(cmd, repo_path: str = None) -> str:
    return subprocess.check_output(["git", *cmd], cwd=repo_path).decode().strip()

def run_git_log(repo_path: str) -> list[dict]:
    """Run git log and parse output into list of commit dicts."""
    separator = "|"
    fmt = f"%H{separator}%an{separator}%ae{separator}%ad{separator}%s"


    result = git(["log", f"--format={fmt}", "--date=short"], repo_path)

    commits = []
    for line in result.strip().split("\n"):
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
    authors = Counter(commit["author"] for commit in commits)
    total_commits = sum(authors.values())
    top = authors.most_common(n)
    return [(name, count, (count / total_commits * 100)) for name, count in top]


def monthly_activity(commits: list[dict]) -> dict[str, int]:
    """Return commit count per month (YYYY-MM -> count)."""
    activity = defaultdict(int)
    for commit in commits:
        month = commit["date"][:7]  # YYYY-MM
        activity[month] += 1
    return dict(activity)


def longest_gap(commits: list[dict]) -> tuple[int, str, str]:
    """Return longest gap between commits (days, start_date, end_date)."""
    if not commits:
        return 0, "", ""

    dates = sorted(datetime.strptime(c["date"], "%Y-%m-%d") for c in commits)
    max_gap = 0
    gap_start = gap_end = dates[0]

    for i in range(1, len(dates)):
        gap = (dates[i] - dates[i - 1]).days
        if gap > max_gap:
            max_gap = gap
            gap_start = dates[i - 1]
            gap_end = dates[i]

    return max_gap, gap_start.strftime("%Y-%m-%d"), gap_end.strftime("%Y-%m-%d")


def save_report_csv(filepath: str, authors, activity, gap):
    """Save report to three proper CSV files: authors, activity, gap."""
    base = Path(filepath).stem

    with open(f"{base}_authors.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Author", "Commits", "Percentage"])
        for name, count, pct in authors:
            writer.writerow([name, count, f"{pct:.1f}"])

    with open(f"{base}_activity.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Month", "Commits"])
        for month in sorted(activity.keys()):
            writer.writerow([month, activity[month]])

    with open(f"{base}_gap.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Days", "Start Date", "End Date"])
        gap_days, gap_start, gap_end = gap
        writer.writerow([gap_days, gap_start, gap_end])


def visualize(commits: list[dict], activity: dict[str, int], repo_name: str):
    """Generate activity bar chart and day-of-week × hour heatmap."""
    import matplotlib.pyplot as plt
    import numpy as np

    # --- Bar chart: commits per month ---
    months = sorted(activity.keys())
    counts = [activity[m] for m in months]

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(range(len(months)), counts, color="steelblue")
    step = max(1, len(months) // 20)
    ax.set_xticks(range(0, len(months), step))
    ax.set_xticklabels([months[i] for i in range(0, len(months), step)], rotation=45, ha="right")
    ax.set_xlabel("Miesiąc")
    ax.set_ylabel("Liczba commitów")
    ax.set_title(f"Aktywność projektu: {repo_name}")
    fig.tight_layout()
    fig.savefig("activity_chart.png", dpi=150)
    plt.close(fig)
    print("Zapisano: activity_chart.png")

    # --- Heatmap: day of week × hour ---
    # Need hour data — re-run git log with hour info
    try:
        raw = subprocess.check_output(
            ["git", "log", "--format=%ad", "--date=format:%w %H"],
            cwd=repo_name
        ).decode().strip()
    except Exception:
        print("Nie udało się wygenerować heatmapy (brak danych godzinowych).")
        return

    heatmap = np.zeros((7, 24), dtype=int)
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) == 2:
            dow, hour = int(parts[0]), int(parts[1])
            heatmap[dow][hour] += 1

    # Reorder: %w gives 0=Sun,1=Mon,...,6=Sat → shift to Mon-Sun
    reorder = [1, 2, 3, 4, 5, 6, 0]
    heatmap = heatmap[reorder]
    days_labels = ["Pon.", "Wt.", "Śr.", "Czw.", "Pt.", "Sob.", "Niedz."]

    fig2, ax2 = plt.subplots(figsize=(12, 4))
    im = ax2.imshow(heatmap, aspect="auto", cmap="YlOrRd", interpolation="nearest")
    ax2.set_yticks(range(7))
    ax2.set_yticklabels(days_labels)
    ax2.set_xticks(range(24))
    ax2.set_xticklabels([f"{h:02d}" for h in range(24)])
    ax2.set_xlabel("Godzina")
    ax2.set_ylabel("Dzień tygodnia")
    ax2.set_title(f"Heatmapa commitów: {repo_name}")
    fig2.colorbar(im, ax=ax2, label="Liczba commitów")
    fig2.tight_layout()
    fig2.savefig("heatmap_chart.png", dpi=150)
    plt.close(fig2)
    print("Zapisano: heatmap_chart.png")


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
    for month in sorted(activity.keys())[-12:]:
        print(f"  {month}: {activity[month]} commitów")

    # Najdłuższy gap
    gap_days, gap_start, gap_end = longest_gap(commits)
    print(f"\nNAJDŁUŻSZA PRZERWA: {gap_days} dni ({gap_start} → {gap_end})")

    # Zapis do CSV
    save_report_csv("report.csv", authors, activity, (gap_days, gap_start, gap_end))
    print(f"\nRaporty CSV zapisane: report_authors.csv, report_activity.csv, report_gap.csv")

    # Wizualizacja
    visualize(commits, activity, repo_path)


if __name__ == "__main__":
    main()