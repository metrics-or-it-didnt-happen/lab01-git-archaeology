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
            commits.append(
                {
                    "hash": parts[0],
                    "author": parts[1],
                    "email": parts[2],
                    "date": parts[3],
                    "message": parts[4],
                }
            )
    return commits


def top_authors(commits: list[dict], n: int = 10) -> list[tuple[str, int, float]]:
    """Return top N authors by commit count."""
    all_commits = len(commits)
    cnt = Counter()
    for d in commits:
        cnt[d["author"]] += 1

    res = [item + (item[1] * 100 / all_commits,) for item in cnt.most_common(n)]
    return res


def monthly_activity(commits: list[dict]) -> dict[str, int]:
    """Return commit count per month (YYYY-MM -> count)."""
    cnt = Counter()
    for d in commits:
        cnt[d["date"][0:7]] += 1

    return dict(cnt)


def longest_gap(commits: list[dict]) -> tuple[int, str, str]:
    """Return longest gap between commits (days, start_date, end_date)."""

    dates = []
    for d in commits:
        dates.append(datetime.strptime(d["date"], "%Y-%m-%d"))

    days = []
    for start, end in zip(dates, dates[1:]):
        diff = end - start
        days.append((diff.days, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")))

    if not days:
        return (0, "", "")

    longest = max(days)

    return longest


def save_report_csv(filepath: str, authors: dict, activity: dict, gap: tuple):
    """Save report to CSV file using sys.stdout redirection."""
    gap_days, gap_start, gap_end = gap

    original_stdout = sys.stdout

    try:
        with open(filepath, mode="w", encoding="utf-8") as f:
            sys.stdout = f

            print("AUTORZY,")
            print("Autor,Liczba commitow,Udzial")
            for author, count, percentage in authors:
                # Ręcznie wstawiamy przecinki między trzema wartościami
                print(f"{author},{count},{percentage:.2f}")
            print(",,")

            print("AKTYWNOSC,")
            print("Data,Liczba commitow")
            for date_key, count in activity.items():
                print(f"{date_key},{count}")
            print(",,")

            print("NAJDLUZSZA PRZERWA,,")
            print("Liczba dni,Poczatek,Koniec")
            print(f"{gap_days},{gap_start},{gap_end}")
    finally:
        sys.stdout = original_stdout


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
    last_monts = {
        key: value for id, (key, value) in enumerate(activity.items()) if id < 12
    }
    for date, cnt in last_monts.items():
        print(f"{date}: {cnt}")
    # Najdłuższy gap
    gap_days, gap_start, gap_end = longest_gap(commits)
    print(f"\nNAJDŁUŻSZA PRZERWA: {gap_days} dni ({gap_start} → {gap_end})")

    # Zapis do CSV
    save_report_csv("report.csv", authors, activity, (gap_days, gap_start, gap_end))
    print(f"\nRaport zapisany do: report.csv")


if __name__ == "__main__":
    main()
