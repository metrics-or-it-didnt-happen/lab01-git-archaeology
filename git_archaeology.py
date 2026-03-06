#!/usr/bin/env python3
"""Git Archaeology - mining commit history for fun and metrics."""

import csv
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


def run_git_log(repo_path: str) -> list[dict]:
    """Run git log and parse output into list of commit dicts."""
    separator = "|"
    fmt = f"%H{separator}%an{separator}%ae{separator}%ad{separator}%s"

    try:
        result = subprocess.run(
            ["git", "log", f"--format={fmt}", "--date=iso-strict"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
    except subprocess.CalledProcessError:
        sys.exit(1)

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
    if not commits:
        return []

    total_commits = len(commits)
    author_counts = Counter(commit["author"] for commit in commits)

    top_n = []
    for author, count in author_counts.most_common(n):
        percentage = (count / total_commits) * 100
        top_n.append((author, count, percentage))

    return top_n


def monthly_activity(commits: list[dict]) -> dict[str, int]:
    """Return commit count per month (YYYY-MM -> count)."""
    months = [commit["date"][:7] for commit in commits]
    month_counts = Counter(months)

    return dict(sorted(month_counts.items()))


def get_heatmap_data(commits: list[dict]) -> list[list[int]]:
    """Tworzy macierz 7 dni x 24 godziny."""
    matrix = [[0 for _ in range(24)] for _ in range(7)]
    for c in commits:
        try:
            dt = datetime.fromisoformat(c["date"])
            matrix[dt.weekday()][dt.hour] += 1
        except (ValueError, KeyError):
            continue
    return matrix


def longest_gap(commits: list[dict]) -> tuple[int, str, str]:
    """Return longest gap between commits (days, start_date, end_date)."""
    if len(commits) < 2:
        return 0, "", ""

    parsed_dates = [datetime.fromisoformat(c["date"]).date() for c in commits]
    parsed_dates.sort()

    max_gap = 0
    start_date = ""
    end_date = ""

    for i in range(1, len(parsed_dates)):
        gap = (parsed_dates[i] - parsed_dates[i - 1]).days
        if gap > max_gap:
            max_gap = gap
            start_date = parsed_dates[i - 1].strftime("%Y-%m-%d")
            end_date = parsed_dates[i].strftime("%Y-%m-%d")

    return max_gap, start_date, end_date


def save_report_csv(filepath: str, authors: list, activity: dict, gap: tuple, heatmap: list):
    """Save report to CSV file."""
    with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Sekcja 1: Autorzy
        writer.writerow(["--- TOP AUTHORS ---"])
        writer.writerow(["Author", "Commits", "Percentage"])
        for author, count, pct in authors:
            writer.writerow([author, count, f"{pct:.1f}%"])
        writer.writerow([])

        # Sekcja 2: Aktywność miesięczna
        writer.writerow(["--- MONTHLY ACTIVITY ---"])
        writer.writerow(["Month", "Commits"])
        for month, count in activity.items():
            writer.writerow([month, count])
        writer.writerow([])

        # Sekcja 3: Najdłuższa przerwa
        writer.writerow(["--- LONGEST GAP ---"])
        writer.writerow(["Gap (Days)", "Start Date", "End Date"])
        writer.writerow([gap[0], gap[1], gap[2]])

        # Sekcja 4: Heatmapa
        writer.writerow([])
        writer.writerow(["--- HEATMAP DATA ---"])
        writer.writerow(["Day"] + [str(i) for i in range(24)])
        for day_idx in range(7):
            writer.writerow([day_idx] + heatmap[day_idx])


def main():
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    repo_path = str(Path(repo_path).resolve())

    print(f"Analizuję repozytorium: {repo_path}")
    print("=" * 60)

    commits = run_git_log(repo_path)
    if not commits:
        print("Nie znaleziono żadnych commitów w tym repozytorium.")
        return

    print(f"Znaleziono {len(commits)} commitów\n")

    authors = top_authors(commits)
    print("TOP 10 AUTORÓW:")
    print("-" * 40)
    for name, count, pct in authors:
        print(f"  {name:<30} {count:>5} ({pct:.1f}%)")

    activity = monthly_activity(commits)
    print(f"\nAKTYWNOŚĆ MIESIĘCZNA (ostatnie 12 aktywnych miesięcy):")
    print("-" * 40)

    last_12_months = list(activity.items())[-12:]
    for month, count in reversed(last_12_months):
        print(f"  {month:<15} {count:>5} commitów")

    gap_days, gap_start, gap_end = longest_gap(commits)
    if gap_days > 0:
        print(f"\nNAJDŁUŻSZA PRZERWA: {gap_days} dni ({gap_start} → {gap_end})")
    else:
        print("\nNAJDŁUŻSZA PRZERWA: Brak (mniej niż 2 commity lub wszystkie tego samego dnia)")

    heatmap = get_heatmap_data(commits)

    save_report_csv("report.csv", authors, activity, (gap_days, gap_start, gap_end), heatmap)
    print(f"\nRaport zapisany do: report.csv")


if __name__ == "__main__":
    main()