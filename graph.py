import matplotlib.pyplot as plt
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import numpy as np
import seaborn as sns

def get_git_logs(repo_path: str) -> list[dict]:
    """Extract commit data from git log."""
    separator = "|"
    # Format: commit_hash|author|email|date|time|day_of_week|hour|message
    fmt = f"%H{separator}%an{separator}%ae{separator}%ad{separator}%ai{separator}%s"
    
    try:
        result = subprocess.run(
            ["git", "log", f"--format={fmt}", "--date=short"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Błąd: nie mogę uruchomić git log w {repo_path}")
        print(f"Szczegóły: {e.stderr}")
        sys.exit(1)
    
    commits = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split(separator, maxsplit=5)
        if len(parts) >= 5:
            try:
                # Parse datetime from %ai format: YYYY-MM-DD HH:MM:SS +ZZZZ
                datetime_str = parts[4].split(" ")[0:2]
                datetime_obj = datetime.strptime(
                    f"{datetime_str[0]} {datetime_str[1]}", 
                    "%Y-%m-%d %H:%M:%S"
                )
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "email": parts[2],
                    "date": parts[3],
                    "datetime": datetime_obj,
                    "message": parts[5] if len(parts) > 5 else "",
                })
            except (ValueError, IndexError):
                continue
    
    return commits

def calculate_monthly_activity(commits: list[dict]) -> dict[str, int]:
    """Calculate commit count per month."""
    activity = defaultdict(int)
    for commit in commits:
        month = commit["datetime"].strftime("%Y-%m")
        activity[month] += 1
    return dict(sorted(activity.items()))

def calculate_hourly_heatmap(commits: list[dict]) -> np.ndarray:
    """Calculate heatmap data: day_of_week (0-6) × hour_of_day (0-23)."""
    # Create 7x24 matrix (Monday-Sunday × 0-23h)
    heatmap = np.zeros((7, 24), dtype=int)
    
    for commit in commits:
        day_of_week = commit["datetime"].weekday()  # 0=Monday, 6=Sunday
        hour = commit["datetime"].hour
        heatmap[day_of_week, hour] += 1
    
    return heatmap

def plot_monthly_activity(activity: dict[str, int], repo_name: str):
    """Plot monthly commit activity."""
    months = list(activity.keys())
    counts = list(activity.values())
    
    plt.figure(figsize=(14, 5))
    plt.bar(months, counts, color="steelblue")
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Miesiąc")
    plt.ylabel("Liczba commitów")
    plt.title(f"Aktywność projektu: {repo_name}")
    plt.tight_layout()
    plt.savefig("activity_chart.png", dpi=150)
    print("✓ Wykres aktywności monthly zapisany: activity_chart.png")
    plt.show()

def plot_hourly_heatmap(heatmap: np.ndarray, repo_name: str):
    """Plot heatmap of commits by day and hour."""
    days = ["Pon", "Wto", "Śro", "Czw", "Pią", "Sob", "Nie"]
    hours = [f"{h:02d}:00" for h in range(24)]
    
    plt.figure(figsize=(16, 6))
    sns.heatmap(
        heatmap,
        xticklabels=hours,
        yticklabels=days,
        cmap="YlOrRd",
        cbar_kws={"label": "Liczba commitów"},
        annot=False,
    )
    plt.xlabel("Godzina dnia")
    plt.ylabel("Dzień tygodnia")
    plt.title(f"Kiedy developerzy commitują? {repo_name}")
    plt.tight_layout()
    plt.savefig("hourly_heatmap.png", dpi=150)
    print("✓ Heatmap godzinowy zapisany: hourly_heatmap.png")
    plt.show()

def main():
    """Main function to process git repo and generate visualizations."""
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    repo_path = str(Path(repo_path).resolve())
    repo_name = Path(repo_path).name
    
    print(f"Analizuję repozytorium: {repo_path}")
    print("=" * 60)
    
    commits = get_git_logs(repo_path)
    print(f"Znaleziono {len(commits)} commitów\n")
    
    if not commits:
        print("Błąd: brak commitów w repozytorium")
        sys.exit(1)
    
    # Calculate activity data
    activity = calculate_monthly_activity(commits)
    heatmap = calculate_hourly_heatmap(commits)
    
    # Generate visualizations
    plot_monthly_activity(activity, repo_name)
    plot_hourly_heatmap(heatmap, repo_name)
    print("\nWizualizacje zostały wygenerowane!")

if __name__ == "__main__":
    main()