#!/usr/bin/env python3
"""Git Archaeology - mining commit history for fun and metrics."""

import csv
import io
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# Dostawalem blad UTF-8, wiec dodalem
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def run_git_log(repo_path: str) -> list[dict]:
    """Run git log and parse output into list of commit dicts."""
    separator = "|"
    fmt = f"%H{separator}%an{separator}%ae{separator}%ad{separator}%s"

    result = subprocess.run(
        ["git", "log", f"--format={fmt}", "--date=short"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
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
    counter = Counter(c["author"] for c in commits)
    total = len(commits)
    return [
        (name, count, count / total * 100)
        for name, count in counter.most_common(n)
    ]


def monthly_activity(commits: list[dict]) -> dict[str, int]:
    """Return commit count per month (YYYY-MM -> count), sorted chronologically."""
    counter = Counter()
    for c in commits:
        month_key = c["date"][:7]  # YYYY-MM
        counter[month_key] += 1
    return dict(sorted(counter.items()))


def longest_gap(commits: list[dict]) -> tuple[int, str, str]:
    """Return longest gap between commits (days, start_date, end_date)."""
    dates = sorted({c["date"] for c in commits})
    parsed = [datetime.strptime(d, "%Y-%m-%d") for d in dates]

    max_gap = 0
    gap_start = ""
    gap_end = ""

    for i in range(1, len(parsed)):
        diff = (parsed[i] - parsed[i - 1]).days
        if diff > max_gap:
            max_gap = diff
            gap_start = dates[i - 1]
            gap_end = dates[i]

    return max_gap, gap_start, gap_end


def save_report_csv(filepath: str, authors, activity, gap):
    """Save report to CSV file."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Top autorzy
        writer.writerow(["Sekcja", "Top autorzy"])
        writer.writerow(["Autor", "Liczba commitow", "Procent"])
        for name, count, pct in authors:
            writer.writerow([name, count, f"{pct:.1f}%"])
        writer.writerow([])

        # Aktywność miesięczna
        writer.writerow(["Sekcja", "Aktywnosc miesieczna"])
        writer.writerow(["Miesiąc", "Liczba commitow"])
        for month, count in activity.items():
            writer.writerow([month, count])
        writer.writerow([])

        # Najdłuższa przerwa
        writer.writerow(["Sekcja", "Najdluzsza przerwa"])
        writer.writerow(["Dni", "Od", "Do"])
        gap_days, gap_start, gap_end = gap
        writer.writerow([gap_days, gap_start, gap_end])

    return filepath


def main():
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    repo_path = str(Path(repo_path).resolve())

    print(f"Analizuje repozytorium: {repo_path}")
    print("=" * 60)

    commits = run_git_log(repo_path)
    print(f"Znaleziono {len(commits)} commitow\n")

    # Top autorzy
    authors = top_authors(commits)
    print("TOP 10 AUTOROW:")
    print("-" * 40)
    for name, count, pct in authors:
        print(f"  {name:<30} {count:>5} ({pct:.1f}%)")

    # Aktywność miesięczna
    activity = monthly_activity(commits)
    print(f"\nAKTYWNOSC MIESIECZNA (ostatnie 12 miesiecy):")
    print("-" * 40)
    last_12 = list(activity.items())[-12:]
    for month, count in last_12:
        print(f"  {month}: {count}")

    # Najdłuższy gap
    gap_days, gap_start, gap_end = longest_gap(commits)
    print(f"\nNAJDLUZSZA PRZERWA: {gap_days} dni ({gap_start} → {gap_end})")

    # Zapis do CSV
    try:
        csv_path = save_report_csv("report.csv", authors, activity, (gap_days, gap_start, gap_end))
        print(f"\nRaport zapisany do: {csv_path}")
    except PermissionError:
        print(f"\nBlad: Brak dostepu do report.csv (zamknij plik i sprobuj ponownie).")
        sys.exit(1)


if __name__ == "__main__":
    main()
