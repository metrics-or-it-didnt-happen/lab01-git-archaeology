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
    # Policz commity każdego autora
    author_counts = Counter(commit["author"] for commit in commits)
    
    # Oblicz total commitów
    total_commits = len(commits)
    
    # Posortuj malejąco i weź top N
    top_n = author_counts.most_common(n)
    
    # Konwertuj na listę tuple'i (autor, liczba, procent)
    result = [
        (author, count, (count / total_commits) * 100)
        for author, count in top_n
    ]
    
    return result

def monthly_activity(commits: list[dict]) -> dict[str, int]:
    """Return commit count per month (YYYY-MM -> count)."""
    activity = defaultdict(int)
    
    # Dla każdego commitu, wyciągnij miesiąc (YYYY-MM) i dodaj do licznika
    for commit in commits:
        # Data jest w formacie YYYY-MM-DD, weź pierwsze 7 znaków (YYYY-MM)
        month = commit["date"][:7]
        activity[month] += 1
    
    # Konwertuj na zwykły dict, posortuj po dacie i weź ostatnie 12 miesięcy
    sorted_activity = dict(sorted(activity.items()))
    last_12 = dict(sorted(sorted_activity.items())[-12:])
    return last_12


def longest_gap(commits: list[dict]) -> tuple[int, str, str]:
    """Return longest gap between commits (days, start_date, end_date)."""
    if len(commits) < 2:
        return (0, "", "")
    
    # Posortuj commity po dacie (od najstarszych do najnowszych)
    sorted_commits = sorted(commits, key=lambda x: x["date"])
    
    max_gap = 0
    gap_start = ""
    gap_end = ""
    
    # Porównaj każdy commit z następnym
    for i in range(len(sorted_commits) - 1):
        current_date = datetime.strptime(sorted_commits[i]["date"], "%Y-%m-%d")
        next_date = datetime.strptime(sorted_commits[i + 1]["date"], "%Y-%m-%d")
        
        # Oblicz różnicę w dniach
        gap = (next_date - current_date).days
        
        # Jeśli to największa przerwa, zapisz ją
        if gap > max_gap:
            max_gap = gap
            gap_start = sorted_commits[i]["date"]
            gap_end = sorted_commits[i + 1]["date"]
    
    return (max_gap, gap_start, gap_end)


def save_report_csv(filepath: str, authors, activity, gap):
    """Save report to CSV file."""
    import csv
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Sekcja 1: Top autorzy
        writer.writerow(["TOP AUTORZY"])
        writer.writerow(["Autor", "Liczba commitów", "Procent"])
        for author, count, pct in authors:
            writer.writerow([author, count, f"{pct:.2f}%"])
        
        writer.writerow([])
        
        # Sekcja 2: Aktywność miesięczna
        writer.writerow(["AKTYWNOŚĆ MIESIĘCZNA"])
        writer.writerow(["Miesiąc", "Liczba commitów"])
        for month, count in sorted(activity.items()):
            writer.writerow([month, count])
        
        writer.writerow([])
        
        # Sekcja 3: Najdłuższa przerwa
        writer.writerow(["NAJDŁUŻSZA PRZERWA"])
        writer.writerow(["Dni", "Od", "Do"])
        gap_days, gap_start, gap_end = gap
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

    # Aktywność miesięczna
    activity = monthly_activity(commits)
    print(f"\nAKTYWNOŚĆ MIESIĘCZNA (ostatnie 12 miesięcy):")
    print("-" * 40)
    # Weź ostatnie 12 miesięcy
    last_12_months = dict(sorted(activity.items())[-12:])
    for month, count in last_12_months.items():
        print(f"  {month}: {count}")

    # Najdłuższy gap
    gap_days, gap_start, gap_end = longest_gap(commits)
    print(f"\nNAJDŁUŻSZA PRZERWA: {gap_days} dni ({gap_start} → {gap_end})")

    # Zapis do CSV
    save_report_csv("report.csv", authors, activity, (gap_days, gap_start, gap_end))
    print(f"\nRaport zapisany do: report.csv")


if __name__ == "__main__":
    main()