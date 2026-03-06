#!/usr/bin/env python3
"""Git Archaeology - mining commit history for fun and metrics."""

import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


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
    res = []
    d = { c["author"]: 0 for c in commits }
    all_commits = len(commits)
    
    for c in commits:
        d[c["author"]] += 1

    for name, count in Counter(d).most_common(n):
        res.append((name, count, count / all_commits * 100))
    
    return res

def monthly_activity(commits: list[dict]) -> dict[str, int]:
    """Return commit count per month (YYYY-MM -> count)."""
    res = {}
    for c in commits:
        date = datetime.strptime(c["date"], "%Y-%m-%d")
        month_key = date.strftime("%Y-%m")
        res[month_key] = res.get(month_key, 0) + 1
    return res

def longest_gap(commits: list[dict]) -> tuple[int, str, str]:
    """Return longest gap between commits (days, start_date, end_date)."""

    if len(commits) < 2:
        return (0, "", "")
    dates = sorted(
        datetime.fromisoformat(c["date"]) for c in commits
    )
    max_gap = 0
    start_date = ""
    end_date = ""
    for i in range(1, len(dates)):
        gap = (dates[i] - dates[i - 1]).days
        if gap > max_gap:
            max_gap = gap
            start_date = dates[i - 1].strftime("%Y-%m-%d")
            end_date = dates[i].strftime("%Y-%m-%d")
    return (max_gap, start_date, end_date)


def save_report_csv(filepath: str, authors, activity, gap):
    """Save report to CSV file."""
    
    import csv
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow(["=== TOP 10 AUTORÓW ==="])
        writer.writerow(["Autor", "Liczba commitów", "% całości"])
        for name, count, pct in authors:
            writer.writerow([name, count, f"{pct:.1f}%"])
        writer.writerow([])

        writer.writerow(["=== AKTYWNOŚĆ MIESIĘCZNA ==="])
        writer.writerow(["Miesiąc", "Liczba commitów"])
        for month, count in sorted(activity.items(), key=lambda x: x[0], reverse=True):
            writer.writerow([month, count])
        writer.writerow([])

        gap_days, gap_start, gap_end = gap
        writer.writerow(["=== NAJDŁUŻSZA PRZERWA ==="])
        writer.writerow(["Dni", "Od", "Do"])
        writer.writerow([gap_days, gap_start, gap_end])


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

    activity = monthly_activity(commits)
    print(f"\nAKTYWNOŚĆ MIESIĘCZNA (ostatnie 12 miesięcy):")
    print("-" * 40)
    last_12 = sorted(activity.items(), key=lambda x: x[0], reverse=True)[:12]
    for month, count in last_12:
        print(f"  {month}: {count} commitów")

    # Najdłuższy gap
    gap_days, gap_start, gap_end = longest_gap(commits)
    print(f"\nNAJDŁUŻSZA PRZERWA: {gap_days} dni ({gap_start} → {gap_end})")

    # Zapis do CSV
    save_report_csv("report.csv", authors, activity, (gap_days, gap_start, gap_end))
    print(f"\nRaport zapisany do: report.csv")


if __name__ == "__main__":
    main()