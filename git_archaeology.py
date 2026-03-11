#!/usr/bin/env python3
"""Git Archaeology - mining commit history for fun and metrics."""

import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import csv


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
    total_commits = len(commits)
    if total_commits == 0:
        return []

    counts = Counter(commit["author"] for commit in commits)
    top = counts.most_common(n)

    authors = []
    for name, count in top:
        percentage = (count / total_commits) * 100
        authors.append((name, count, percentage))

    return authors


def monthly_activity(commits: list[dict]) -> dict[str, int]:
    """Return commit count per month (YYYY-MM -> count)."""
    months = [commit["date"][:7] for commit in commits]
    activity = dict(Counter(months))

    return activity


def longest_gap(commits: list[dict]) -> tuple[int, str, str]:
    """Return longest gap between commits (days, start_date, end_date)."""
    dates = sorted([commit["date"] for commit in commits])
    longest_gap = 0
    start_date = end_date = ""

    for i in range(len(dates) - 1):
        d1 = datetime.strptime(dates[i], "%Y-%m-%d")
        d2 = datetime.strptime(dates[i+1], "%Y-%m-%d")
        diff = (d2 - d1).days

        if diff > longest_gap:
            longest_gap = diff
            start_date = dates[i]
            end_date = dates[i + 1]

    return (longest_gap, start_date, end_date)


def save_report_csv(filepath: str, authors, activity, gap):
    """Save report to CSV file."""
    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        writer.writerow(["section", "top authors"])
        writer.writerow(["name", "commit count", "percentage"])

        for name, count, percentage in authors:
            writer.writerow([name, count, f"{percentage:.1f}%"])
        writer.writerow([])

        writer.writerow(["section", "monthly activity"])
        writer.writerow(["month", "commit count"])

        for month in sorted(activity.keys()):
            writer.writerow([month, activity[month]])
        writer.writerow([])

        days, start_date, end_date = gap
        writer.writerow(["section", "longest gap"])
        writer.writerow(["metric", "value"])
        writer.writerow(["days", days])
        writer.writerow(["start date", start_date])
        writer.writerow(["end date", end_date])


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

    months_sorted = sorted(activity.keys())[-12:]
    for month in months_sorted:
        print(f"    {month}: {activity[month]}")

    # Najdłuższy gap
    gap_days, gap_start, gap_end = longest_gap(commits)
    print(f"\nNAJDŁUŻSZA PRZERWA: {gap_days} dni ({gap_start} → {gap_end})")

    # Zapis do CSV
    save_report_csv("report.csv", authors, activity, (gap_days, gap_start, gap_end))
    print(f"\nRaport zapisany do: report.csv")


if __name__ == "__main__":
    main()
