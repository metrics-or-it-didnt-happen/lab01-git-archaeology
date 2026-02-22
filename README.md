# Lab 01: Git Archaeology — kto tu naśmiecił?

## Czy wiesz, że...

Według badań (które właśnie wymyśliłem), 73% commitów w projektach open-source zawiera wiadomość "fix" bez dalszego wyjaśnienia. Pozostałe 27% to "initial commit" i "WIP".

## Kontekst

Każdy projekt open-source to historia opowiedziana commitami. `git log` to nie jest nudna lista zmian — to kronika: kto, kiedy, co i (czasem) dlaczego. Umiejętność czytania tej historii to podstawa pracy z cudzym kodem i fundamentalna umiejętność software archaeology.

W realnej pracy inżyniera analiza historii repozytorium przydaje się do: szukania winnego (git blame, ale z klasą), zrozumienia decyzji projektowych, szacowania aktywności projektu przed wyborem zależności, albo po prostu odpowiedzi na pytanie "kto to napisał i o czym myślał".

## Cel laboratorium

Po tym laboratorium będziesz potrafić:
- wyciągać dane z historii gita za pomocą `git log`, `git shortlog` i `git blame`,
- napisać skrypt w Pythonie, który parsuje historię commitów i generuje raport,
- odpowiedzieć na pytanie "czy ten projekt żyje?" patrząc na twarde dane.

## Wymagania wstępne

- Python 3.9+ zainstalowany i dostępny w terminalu
- `git` zainstalowany
- Konto na GitHubie (to chyba masz, skoro to czytasz)
- Podstawowa znajomość terminala (cd, ls, i takie tam)

## Zadania

### Zadanie 1: Ręczna archeologia (45 min)

Zanim napiszemy automat, trzeba wiedzieć co automatyzujemy. Czas pobawić się detektywa.

**Krok 1:** Sklonuj duży projekt open-source. Wybierz coś z co najmniej kilkuletnią historią i setkami commitów. Propozycje (ale możesz wybrać coś innego):

```bash
# Wybierz JEDEN:
git clone https://github.com/psf/requests.git
git clone https://github.com/pallets/flask.git
git clone https://github.com/fastapi/fastapi.git
git clone https://github.com/django/django.git
```

**Krok 2:** Wejdź do katalogu projektu i rozejrzyj się:

```bash
cd <nazwa_projektu>

# Ile jest commitów w całej historii?
git log --oneline | wc -l

# Top 10 autorów wg liczby commitów
git shortlog -sn | head -10

# Kiedy był pierwszy commit?
git log --reverse --format="%ad %s" --date=short | head -1

# Kiedy był ostatni commit?
git log -1 --format="%ad %s" --date=short
```

**Krok 3:** Użyj `git blame` na wybranym pliku (najlepiej jakimś kluczowym, np. `setup.py`, `README.md` albo głównym module):

```bash
# Kto napisał poszczególne linie?
git blame README.md

# Wersja skrócona (sam hash + autor)
git blame --line-porcelain README.md | grep "^author " | sort | uniq -c | sort -rn
```

**Krok 4:** Odpowiedz na pytania (zapiszcie odpowiedzi — przydadzą się do oddania):

1. Ile commitów ma projekt?
2. Kto jest autorem największej liczby commitów? Jaki % całości to stanowi?
3. Kiedy projekt był najbardziej aktywny (który rok/miesiąc)?
4. Które pliki zmieniano najczęściej? (`git log --format=format: --name-only | sort | uniq -c | sort -rn | head -20`)
5. Czy projekt jest wciąż aktywnie rozwijany?

### Zadanie 2: Automat do kopania (60 min)

Ręczne wklepywanie komend to nie jest plan na życie. Napiszcie skrypt `git_archaeology.py`, który zrobi robotę za Was.

**Co skrypt ma robić:**

1. Przyjąć ścieżkę do repozytorium jako argument (lub działać w bieżącym katalogu)
2. Uruchomić `git log` z odpowiednim formatem i sparsować wynik
3. Wygenerować raport z następującymi sekcjami:
   - **Top 10 autorów** (nazwa, liczba commitów, % całości)
   - **Aktywność miesięczna** (ile commitów w każdym miesiącu, format: YYYY-MM → count)
   - **Najdłuższy streak bez commitów** (ile dni, między którymi datami)
4. Zapisać wynik jako CSV (`report.csv`) + wydrukować podsumowanie na konsolę

**Punkt startowy:**

```python
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
    # TODO: Twój kod tutaj
    pass


def monthly_activity(commits: list[dict]) -> dict[str, int]:
    """Return commit count per month (YYYY-MM -> count)."""
    # TODO: Twój kod tutaj
    pass


def longest_gap(commits: list[dict]) -> tuple[int, str, str]:
    """Return longest gap between commits (days, start_date, end_date)."""
    # TODO: Twój kod tutaj
    pass


def save_report_csv(filepath: str, authors, activity, gap):
    """Save report to CSV file."""
    # TODO: Twój kod tutaj
    pass


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

    # Najdłuższy gap
    gap_days, gap_start, gap_end = longest_gap(commits)
    print(f"\nNAJDŁUŻSZA PRZERWA: {gap_days} dni ({gap_start} → {gap_end})")

    # Zapis do CSV
    save_report_csv("report.csv", authors, activity, (gap_days, gap_start, gap_end))
    print(f"\nRaport zapisany do: report.csv")


if __name__ == "__main__":
    main()
```

**Oczekiwany output (przykład):**

```
Analizuję repozytorium: /home/student/requests
============================================================
Znaleziono 6234 commitów

TOP 10 AUTORÓW:
----------------------------------------
  Kenneth Reitz                    2847 (45.7%)
  Nate Prewitt                      412 (6.6%)
  Ian Cordasco                      389 (6.2%)
  ...

AKTYWNOŚĆ MIESIĘCZNA (ostatnie 12 miesięcy):
----------------------------------------
  2025-02: 12
  2025-01: 8
  ...

NAJDŁUŻSZA PRZERWA: 47 dni (2023-08-12 → 2023-09-28)

Raport zapisany do: report.csv
```

### Zadanie 3: Wizualizacja (30 min) — dla ambitnych

Liczby to jedno, ale wykres to zupełnie inna liga perswazji. Rozszerzcie skrypt (lub napiszcie oddzielny) o wizualizację aktywności projektu w czasie.

**Do zrobienia:**
- Wykres słupkowy/liniowy: liczba commitów na miesiąc (oś X = miesiąc, oś Y = liczba commitów)
- Bonus: wykres heatmap (dzień tygodnia × godzina dnia) — kiedy developerzy commitują?

```python
import matplotlib.pyplot as plt

# Przykład prostego wykresu aktywności
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
plt.show()
```

## Co oddajecie

W swoim unikatowym branchu `lab01_nazwisko1_nazwisko2`:

1. **`git_archaeology.py`** — działający skrypt z zadania 2
2. **`report.csv`** — wygenerowany raport dla wybranego projektu
3. **`answers.md`** — odpowiedzi na 5 pytań z zadania 1
4. *(opcjonalnie)* **`activity_chart.png`** — wykres z zadania 3

## Kryteria oceny

- Skrypt uruchamia się bez błędów i generuje poprawny raport
- Top autorów jest posortowanych malejąco i zawiera procenty
- Aktywność miesięczna obejmuje pełen zakres historii
- Najdłuższa przerwa jest wyliczona poprawnie
- Raport CSV jest poprawnie sformatowany
- Odpowiedzi na pytania z zadania 1 są konkretne i poparte danymi

## FAQ

**P: Mogę wybrać dowolny projekt open-source?**
O: Tak, ale musi mieć co najmniej 500 commitów i co najmniej 2 lata historii. Inaczej analiza będzie nudna.

**P: Mój skrypt się wysypuje na projekcie z milionem commitów.**
O: Linux kernel ma 1M+ commitów — zacznij od czegoś mniejszego. Albo ogranicz `git log` flagą `--since="2020-01-01"`.

**P: `git log` zwraca dziwne znaki / encoding się sypie.**
O: Dodaj `encoding="utf-8", errors="replace"` do `subprocess.run()`.

**P: Czy mogę użyć biblioteki GitPython zamiast subprocess?**
O: Na tym labie chcemy, żebyś zrozumiał surowy output gita. GitPython będzie na następnych labach mile widziany.

**P: Mój partner/partnerka nie przyszedł/przyszła, mogę pracować sam/sama?**
O: Tak, ale daj znać prowadzącemu na początku zajęć.

## Przydatne linki

- [git log documentation](https://git-scm.com/docs/git-log)
- [git shortlog documentation](https://git-scm.com/docs/git-shortlog)
- [git blame documentation](https://git-scm.com/docs/git-blame)
- [Python subprocess module](https://docs.python.org/3/library/subprocess.html)
- [matplotlib quickstart](https://matplotlib.org/stable/tutorials/introductory/quick_start.html)

---
*"Daj mi sześć godzin na ścięcie drzewa, a pierwsze cztery spędzę na ostrzeniu siekiery."* — Abraham Lincoln (chyba)
