Wybrany projekt: https://github.com/django/django

1. Ile ma commitów? **`34 353`**

2. Kto jest autorem największej liczby commitów? 
    
    **`Tim Graham`** `(3 374 commitów)`
    
    Jaki % całości to stanowi? **`~9.82%`**
    

3. Kiedy projekt był najbardziej aktywny (który rok/miesiąc)?
    
     **`2008-08`** `(605 commitów)` 
    
    Komenda: `git log --format="%ad" --date=format:%Y-%m | sort | uniq -c | sort -nr`
    
    Rok największej aktywności (`--date=format:%Y`): **`2013`** `(3 188 commitów)` 
    
    Najaktywniejszy miesiąc (`--date=format:%m)`: **`sierpień`** `(3 406 commitów)` 
    
4. Które pliki zmieniano najczęściej? (`git log --format=format: --name-only | sort | uniq -c | sort -rn | head -21`)
    1. 1120 AUTHORS
    2. 628 django/db/models/query.py
    3. 594 django/db/models/sql/query.py
    4. 551 docs/ref/settings.txt
    5. 534 django/db/models/fields/__init__.py
    6. 525 django/db/models/base.py
    7. 488 django/contrib/admin/options.py
    8. 480 docs/internals/deprecation.txt
    9. 479 docs/ref/models/querysets.txt
    10. 468 django/db/models/fields/related.py
    11. 454 docs/ref/contrib/admin/index.txt
    12. 452 tests/admin_views/tests.py
    13. 432 docs/ref/django-admin.txt
    14. 371 docs/ref/models/fields.txt
    15. 367 django/db/models/sql/compiler.py
    16. 366 django/conf/global_settings.py
    17. 364 django/test/testcases.py
    18. 354 docs/releases/1.8.txt
    19. 345 docs/ref/templates/builtins.txt
    20. 342 docs/releases/1.7.txt

5. Czy projekt jest wciąż aktywnie rozwijany?
    
     `TAK, ale z mniejszą aktywnością niż w szczytowym okresie.`
    
    - 83 commitów w 2026-01
    - 67 commitów w 2026-02
    - 5 commitów w 2026-03