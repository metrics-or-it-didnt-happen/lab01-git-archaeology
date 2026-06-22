#!/usr/bin/env python3
"""Git Archaeology - mining commit history for fun and metrics."""

import subprocess
import sys
import csv
from collections import Counter
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


def run_git_log(repo_path: str) -> list[dict]:
    """Run git log and parse output into list of commit dicts."""
    separator = "|"
    fmt = f"%H{separator}%an{separator}%ae{separator}%ad{separator}%s"

    # Dodano encoding="utf-8" dla kompatybilności z Windows/FastAPI
    result = subprocess.run(
        ["git", "log", f"--format={fmt}", "--date=iso"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8"
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
    counts = Counter(c["author"] for c in commits)
    total = len(commits)
    return [(name, count, (count / total) * 100) for name, count in counts.most_common(n)]


def generate_charts(commits, activity, repo_name):
    """Generuje wykres słupkowy aktywności i heatmapę godzinową."""
    # 1. Wykres słupkowy aktywności (ostatnie 24 miesiące dla czytelności)
    months_data = list(reversed(list(activity.items())[:24]))
    months = [m[0] for m in months_data]
    counts = [m[1] for m in months_data]

    plt.figure(figsize=(14, 6))
    plt.bar(months, counts, color="steelblue", edgecolor="black", alpha=0.8)
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Miesiąc")
    plt.ylabel("Liczba commitów")
    plt.title(f"Aktywność projektu: {repo_name} (Ostatnie 24 m-ce)")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("activity_chart.png", dpi=150)
    print("Wygenerowano: activity_chart.png")

    heatmap_data = np.zeros((7, 24))

    for c in commits:
        try:
            dt = datetime.strptime(c["date"].split(' ')[0] + ' ' + c["date"].split(' ')[1], "%Y-%m-%d %H:%M:%S")
            heatmap_data[dt.weekday()][dt.hour] += 1
        except Exception:
            continue

    days = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Ndz"]

    plt.figure(figsize=(12, 5))
    plt.imshow(heatmap_data, cmap="YlOrRd", aspect="auto")

    plt.colorbar(label="Liczba commitów")
    plt.xticks(range(24), [f"{h:02d}" for h in range(24)])
    plt.yticks(range(7), days)
    plt.xlabel("Godzina dnia")
    plt.ylabel("Dzień tygodnia")
    plt.title(f"Kiedy pracują developerzy? (Heatmapa: {repo_name})")
    plt.tight_layout()
    plt.savefig("heatmap.png", dpi=150)
    print("Wygenerowano: heatmap.png")


def monthly_activity(commits: list[dict]) -> dict[str, int]:
    """Return commit count per month (YYYY-MM -> count)."""
    activity = Counter(c["date"][:7] for c in commits)
    return dict(sorted(activity.items(), reverse=True))


def longest_gap(commits: list[dict]) -> tuple[int, str, str]:
    """Return longest gap between commits (days, start_date, end_date)."""
    if not commits:
        return 0, "", ""

    # Wyciągamy tylko YYYY-MM-DD z pełnego ISO stringa
    dates = sorted({datetime.strptime(c["date"].split(' ')[0], "%Y-%m-%d") for c in commits})

    max_days = 0
    gap_range = ("", "")

    for i in range(len(dates) - 1):
        diff = (dates[i + 1] - dates[i]).days
        if diff > max_days:
            max_days = diff
            gap_range = (dates[i].strftime("%Y-%m-%d"), dates[i + 1].strftime("%Y-%m-%d"))

    return max_days, gap_range[0], gap_range[1]


def save_report_csv(filepath: str, authors, activity, gap):
    """Save report to CSV file."""
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Key", "Value", "Percentage"])

        for name, count, pct in authors:
            writer.writerow(["Top Author", name, count, f"{pct:.1f}%"])

        for month, count in activity.items():
            writer.writerow(["Monthly Activity", month, count, ""])

        writer.writerow(["Longest Gap", f"{gap[1]} to {gap[2]}", f"{gap[0]} days", ""])


def main():
    try:
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
        last_12_months = list(activity.items())[:12]
        for month, count in last_12_months:
            print(f"  {month}: {count}")

        # Najdłuższy gap
        gap = longest_gap(commits)
        print(f"\nNAJDŁUŻSZA PRZERWA: {gap[0]} dni ({gap[1]} → {gap[2]})")

        repo_name = Path(repo_path).name
        generate_charts(commits, activity, repo_name)

        # Zapis do CSV
        save_report_csv("report.csv", authors, activity, gap)
        print(f"\nRaport zapisany do: report.csv")

    except subprocess.CalledProcessError:
        print("Błąd: Ścieżka nie jest repozytorium Git.")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")


if __name__ == "__main__":
    main()