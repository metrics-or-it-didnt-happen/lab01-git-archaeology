1. Ile commitów ma projekt?
Short answer: 34354

Long answer:
git log --oneline | Measure-Object -line

Lines Words Characters Property
----- ----- ---------- --------
34354

2. Kto jest autorem największej liczby commitów? Jaki % całości to stanowi?
Short answer:   3374  Tim Graham czyli 9,8%

Long answer:
git shortlog -sn | head -1
  3374  Tim Graham


3. Kiedy projekt był najbardziej aktywny (który rok/miesiąc)?
Short answer: sierpień 2008 miał rekordową liczbę 605 commitów

Long answer:
git log --format="%ad" --date=format:'%Y-%m'| sort | uniq -c | sort -rn | head -10
    605 2008-08
    394 2013-05
    356 2013-02
    352 2013-09
    348 2012-08
    343 2005-11
    318 2005-07
    317 2013-12
    309 2014-11
    300 2008-09


4. Które pliki zmieniano najczęściej? (git log --format=format: --name-only | sort | uniq -c | sort -rn | head -20)

Long answer:
git log --format=format: --name-only | sort | uniq -c | sort -rn | head -20

  34353
   1120 AUTHORS
    628 django/db/models/query.py
    594 django/db/models/sql/query.py
    551 docs/ref/settings.txt
    534 django/db/models/fields/__init__.py
    525 django/db/models/base.py
    488 django/contrib/admin/options.py
    480 docs/internals/deprecation.txt
    479 docs/ref/models/querysets.txt
    468 django/db/models/fields/related.py
    454 docs/ref/contrib/admin/index.txt
    452 tests/admin_views/tests.py
    432 docs/ref/django-admin.txt
    371 docs/ref/models/fields.txt
    367 django/db/models/sql/compiler.py
    366 django/conf/global_settings.py
    364 django/test/testcases.py
    354 docs/releases/1.8.txt
    345 docs/ref/templates/builtins.txt

5. Czy projekt jest wciąż aktywnie rozwijany?
Short answer: repozytorium ma regularne commity w ostatnim czasie, więc można założyć że tak
*dokładniej potwierdzone w raporcie z następnego zadania

Long answer:
git log --format="%ad %s" --date=short| sort -r | head -20
2026-03-04 Fixed #21080 -- Ignored urls inside comments during collectstatic.
2026-03-03 Fixed #36923 -- Added tests for non-hierarchical URI schemes in URLField.to_python().
2026-03-03 Added stub release notes for 6.0.4.
2026-03-03 Added CVE-2026-25673 and CVE-2026-25674 to security archive.
2026-03-01 Refs #35381 -- Moved JSONNull to django.db.models.expressions.
2026-02-27 Refs #35972 -- Returned params in a tuple in further expressions.
2026-02-27 Refs #23919 -- Used yield from in Paginator.
2026-02-27 Fixed #36961 -- Fixed TypeError in deprecation warnings if Django is imported by namespace.
2026-02-27 Fixed #36946 -- Respected test database name when running tests in parallel on SQLite.
2026-02-27 Aligned docs checks between GitHub Actions and local development.
2026-02-26 Fixed #36848 -- Mentioned BadRequest exception in docs/ref/views.txt.
2026-02-26 Fixed #22079 -- Added tests for stripping empty list values in RequestFactory.
2026-02-26 Adjusted default DoS severity level in Security Policy.
2026-02-25 Refs #36936 - Adjusted tests to set PYTHON_COLORS environment variable.
2026-02-25 Refs #36879, #36936 -- Fixed typo in RedisCacheTests.test_client_driver_info.
2026-02-25 Refs #36652, #36936 -- Improved path manipulation in a migration test launching a subprocess.
2026-02-25 Fixed #36948 -- Fixed breadcrumb text overlap at small widths in admin.
2026-02-25 Fixed #36944 -- Removed MAX_LENGTH_HTML and related 5M chars limit references from HTML truncation docs.
2026-02-24 Refs #36873 -- Fixed changelink background image Y position.
2026-02-24 Delete leaking loop iter vars in `smartif.py`