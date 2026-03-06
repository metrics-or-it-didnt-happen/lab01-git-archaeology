#!/usr/bin/env python3
"""Git Archaeology - mining commit history for fun and metrics."""

import csv
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

OUTPUT_DIR = Path("output")


def run_git_log(repo_path: str) -> list[dict[str, str]]:
    """Run git log and parse output into list of commit dicts."""
    separator = "\x1f"  # unit separator — safe delimiter
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

    commits: list[dict[str, str]] = []
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


def top_authors(
    commits: list[dict[str, str]], n: int = 10
) -> list[tuple[str, int, float]]:
    """Return top N authors by commit count."""
    counts = Counter(c["author"] for c in commits)
    total = len(commits)
    return [(name, count, count / total * 100) for name, count in counts.most_common(n)]


def monthly_activity(commits: list[dict[str, str]]) -> dict[str, int]:
    """Return commit count per month (YYYY-MM -> count), sorted chronologically."""
    counts: Counter[str] = Counter()
    for c in commits:
        counts[c["date"][:7]] += 1
    return dict(sorted(counts.items()))


def longest_gap(commits: list[dict[str, str]]) -> tuple[int, str, str]:
    """Return longest gap between commits (days, start_date, end_date)."""
    dates = sorted({date.fromisoformat(c["date"]) for c in commits})
    if len(dates) < 2:
        return (0, "", "")

    max_gap = 0
    gap_start = dates[0]
    gap_end = dates[0]

    for i in range(1, len(dates)):
        diff = (dates[i] - dates[i - 1]).days
        if diff > max_gap:
            max_gap = diff
            gap_start = dates[i - 1]
            gap_end = dates[i]

    return (max_gap, gap_start.isoformat(), gap_end.isoformat())


def save_report_csv(
    filepath: Path,
    authors: list[tuple[str, int, float]],
    activity: dict[str, int],
    gap: tuple[int, str, str],
) -> None:
    """Save report to CSV file."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow(["Section: Top Authors"])
        writer.writerow(["Author", "Commits", "Percentage"])
        for name, count, pct in authors:
            writer.writerow([name, count, f"{pct:.1f}%"])

        writer.writerow([])
        writer.writerow(["Section: Monthly Activity"])
        writer.writerow(["Month", "Commits"])
        for month, count in activity.items():
            writer.writerow([month, count])

        writer.writerow([])
        writer.writerow(["Section: Longest Gap"])
        writer.writerow(["Days", "Start", "End"])
        writer.writerow([gap[0], gap[1], gap[2]])


def generate_charts(
    activity: dict[str, int],
    authors: list[tuple[str, int, float]],
    repo_name: str,
    output_dir: Path,
) -> None:
    """Generate interactive HTML chart and static PNG of project activity."""
    import altair as alt

    activity_data: list[dict[str, str | int]] = [
        {"month": m, "commits": c} for m, c in activity.items()
    ]
    activity_chart = (
        alt.Chart(alt.Data(values=activity_data))
        .mark_bar(color="steelblue")
        .encode(
            x=alt.X("month:O", title="Month", sort=None),
            y=alt.Y("commits:Q", title="Commits"),
            tooltip=["month:O", "commits:Q"],
        )
        .properties(
            title=f"Monthly commit activity: {repo_name}", width=1200, height=300
        )
    )

    author_data: list[dict[str, str | int]] = [
        {"author": a[0], "commits": a[1]} for a in authors
    ]
    author_chart = (
        alt.Chart(alt.Data(values=author_data))
        .mark_bar(color="coral")
        .encode(
            x=alt.X("commits:Q", title="Commits"),
            y=alt.Y("author:N", title="Author", sort="-x"),
            tooltip=["author:N", "commits:Q"],
        )
        .properties(
            title=f"Top {len(authors)} authors: {repo_name}", width=1200, height=300
        )
    )

    combined = alt.vconcat(activity_chart, author_chart).resolve_scale(x="independent")

    combined.save(str(output_dir / "activity_chart.html"))
    combined.save(str(output_dir / "activity_chart.png"), scale_factor=2)


def main() -> None:
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    repo_path = str(Path(repo_path).resolve())
    repo_name = Path(repo_path).name

    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"Analyzing repository: {repo_path}")
    print("=" * 60)

    commits = run_git_log(repo_path)
    print(f"Found {len(commits)} commits\n")

    # Top authors
    authors = top_authors(commits)
    print("TOP 10 AUTHORS:")
    print("-" * 40)
    for name, count, pct in authors:
        print(f"  {name:<30} {count:>5} ({pct:.1f}%)")

    # Monthly activity
    activity = monthly_activity(commits)
    print("\nMONTHLY ACTIVITY (last 12 months):")
    print("-" * 40)
    last_12 = dict(list(activity.items())[-12:])
    for month, count in last_12.items():
        print(f"  {month}: {count}")

    # Longest gap
    gap_days, gap_start, gap_end = longest_gap(commits)
    print(f"\nLONGEST GAP: {gap_days} days ({gap_start} -> {gap_end})")

    # Save CSV
    csv_path = OUTPUT_DIR / "report.csv"
    save_report_csv(csv_path, authors, activity, (gap_days, gap_start, gap_end))
    print(f"\nReport saved to: {csv_path}")

    # Charts (task 3)
    print("Generating charts...")
    generate_charts(activity, authors, repo_name, OUTPUT_DIR)
    print(f"Saved: {OUTPUT_DIR}/activity_chart.html, {OUTPUT_DIR}/activity_chart.png")


if __name__ == "__main__":
    main()
