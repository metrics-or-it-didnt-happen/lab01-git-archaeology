#!/usr/bin/env python3
"""Git Archaeology - mining commit history for fun and metrics."""

import subprocess
import sys
import csv
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
    # TODO: Twój kod tutaj
    authorCounter = Counter()

    for commitDict in commits:
        authorCounter[commitDict['author']] += 1

    totalCommits = authorCounter.total()
    result = []
    for author in authorCounter.most_common(n):
        result.append((author[0], author[1], author[1] / totalCommits * 100))
    return result 
    
    


def monthly_activity(commits: list[dict]) -> dict[str, int]:
    """Return commit count per month (YYYY-MM -> count)."""
    # TODO: Twój kod tutaj
    monthDict = defaultdict(int)

    for commitDict in commits:
        monthDict[str(commitDict['date'][0:7])] += 1

    return monthDict


def longest_gap(commits: list[dict]) -> tuple[int, str, str]:
    """Return longest gap between commits (days, start_date, end_date)."""
    # TODO: Twój kod tutaj
    sortedCommits = sorted(commits, key=lambda x: x['date'])
    date_format = '%Y-%m-%d'
    top_time = 0
    top_t1 = ''
    top_t2 = ''

    for t1, t2 in zip(sortedCommits[:-1], sortedCommits[1:]):
        t1 = t1['date']
        t2 = t2['date']
        d1 = datetime.strptime(t1, date_format)
        d2 = datetime.strptime(t2, date_format)

        days_diff = (d2 - d1).days

        if (days_diff > top_time):
            top_time = days_diff
            top_t1 = t1
            top_t2 = t2


    return (top_time,top_t1,top_t2)


def save_report_csv(filepath: str, authors, activity, gap):
    """Save report to CSV file."""
    # TODO: Twój kod tutaj
    with open("authors_" + filepath, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['author', 'commits', 'commit_perc'])
        writer.writerows(authors)

    with open("activity_" + filepath, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['month', 'commits'])
        for key, value in activity.items():
            writer.writerow([key, value])

    with open("gap_" + filepath, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['days','start','stop'])
        writer.writerow(list(gap))

    


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
    # TODO: wydrukuj ostatnie 12 miesięcy
    sortedActivity = sorted(activity.items(), key= lambda x: x[0], reverse=True)
    for key,value in sortedActivity[:12]:
        print(key, ": ", value)

    # Najdłuższy gap
    gap_days, gap_start, gap_end = longest_gap(commits)
    print(f"\nNAJDŁUŻSZA PRZERWA: {gap_days} dni ({gap_start} → {gap_end})")

    # Zapis do CSV
    save_report_csv("report.csv", authors, activity, (gap_days, gap_start, gap_end))
    print(f"\nRaport zapisany do: report.csv")


if __name__ == "__main__":
    main()