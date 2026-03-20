#!/usr/bin/env python3
"""Git Archaeology - mining commit history with visual charts."""

import subprocess
import sys
import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

# Próba importu matplotlib
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def run_git_log(repo_path: str) -> list[dict]:
    """Uruchamia git log i parsuje wynik do listy słowników."""
    separator = "|"
    fmt = f"%H{separator}%an{separator}%ae{separator}%ad{separator}%s"

    try:
        result = subprocess.run(
            ["git", "log", f"--format={fmt}", "--date=short"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        print(f"Błąd: Ścieżka '{repo_path}' nie jest repozytorium Git.")
        sys.exit(1)

    commits = []
    for line in result.stdout.strip().split("\n"):
        if not line: continue
        parts = line.split(separator, maxsplit=4)
        if len(parts) == 5:
            commits.append({
                "hash": parts[0], "author": parts[1],
                "email": parts[2], "date": parts[3], "message": parts[4],
            })
    return commits


def top_authors(commits: list[dict], n: int = 10):
    """Zwraca listę TOP N autorów."""
    counts = Counter(c['author'] for c in commits)
    total = len(commits)
    top = counts.most_common(n)
    return [(name, count, (count / total) * 100) for name, count in top]


def monthly_activity(commits: list[dict]) -> dict[str, int]:
    """Zlicza commity na miesiąc."""
    return Counter(c['date'][:7] for c in commits)


def generate_activity_chart(activity: dict[str, int], repo_name: str):
    """Generuje i zapisuje wykres słupkowy aktywności."""
    if not HAS_MATPLOTLIB:
        print("\n[!] Pomiń generowanie wykresu: brak biblioteki matplotlib.")
        return

    sorted_months = sorted(activity.keys())
    counts = [activity[m] for m in sorted_months]

    plt.figure(figsize=(14, 6))
    plt.bar(sorted_months, counts, color="steelblue", edgecolor="black", alpha=0.8)
    
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Miesiąc", fontweight='bold')
    plt.ylabel("Liczba commitów", fontweight='bold')
    plt.title(f"Aktywność projektu: {repo_name}", fontsize=14, fontweight='bold')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig("activity_chart.png", dpi=150)
    print(f"\n[+] Wykres zapisany do: activity_chart.png")


def main():
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    repo_path = str(Path(repo_path).resolve())
    repo_name = Path(repo_path).name

    print(f"\nAnalizuję repozytorium: {repo_name}")
    print("=" * 60)

    commits = run_git_log(repo_path)
    if not commits:
        print("Brak danych do analizy.")
        return

    # Pobieramy TOP 10
    authors = top_authors(commits, n=10)
    activity = monthly_activity(commits)

    print(f"Znaleziono {len(commits)} commitów.")
    
    # Wyświetlanie TOP 10 w terminalu
    print("\nTOP 10 AUTORÓW:")
    print("-" * 50)
    for i, (name, count, pct) in enumerate(authors, 1):
        print(f"{i:>2}. {name:<30} {count:>5} ({pct:.1f}%)")
    print("-" * 50)

    # Generowanie wykresu
    generate_activity_chart(activity, repo_name)

    # Zapis raportu CSV
    with open("report.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Month", "Commits"])
        for m in sorted(activity.keys()):
            writer.writerow([m, activity[m]])
    
    print(f"Raport CSV zapisany do: report.csv\n")


if __name__ == "__main__":
    main()
