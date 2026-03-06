1. Ile commitów ma projekt?
`git log --oneline | wc -l`
Jest `4762` commitów. 

2. Kto jest autorem największej liczby commitów? Jaki % całości to stanowi?
`git shortlog -sn | head -1`
Jest nim `Jamie Pine` z `1823` commitami. Stanowi to `38.3%` całości.

3. Kiedy projekt był najbardziej aktywny (który rok/miesiąc)?
`git log --date=short --format='%ad' | cut -d'-' -f1,2 | sort | uniq -c | sort -rn | head -1`
Jest to `grudzień 2025 r.`.

1. Które pliki zmieniano najczęściej? (`git log --format=format: --name-only | sort | uniq -c | sort -rn | head -20`)
Najczęściej zmieniany plik to `Cargo.lock`.
Pozostałe pliki zmieniane w formacie `Liczba Zmian | Nazwa pliku`
 464 Cargo.lock
 368 pnpm-lock.yaml
 305 packages/client/src/core.ts
 260 core/Cargo.toml
 237 core/src/lib.rs
 169 Cargo.toml
 163 package.json
 160 README.md
 151 apps/desktop/src-tauri/Cargo.toml
 138 apps/desktop/src-tauri/src/main.rs
 129 core/prisma/schema.prisma
 122 core/src/location/mod.rs
 118 core/src/library/manager.rs
 114 packages/ui/package.json
 104 apps/desktop/src/App.tsx
 102 .github/workflows/release.yml
 100 interface/app/$libraryId/location/$id.tsx
  94 apps/mobile/package.json
  92 apps/desktop/package.json

1. Czy projekt jest wciąż aktywnie rozwijany?
`git log -1 --format="%ad %s" --date=short`
`Tak`, projest jest aktywnie rozwijany. Ostatni commit był dnia `7 lutego 2026 r`.