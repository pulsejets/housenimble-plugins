# HouseNimble plugins

Lokalt forslag til et offentligt monorepo med én mappe pr. plugin. Core er en
separat, privat kodebase. Dette forslag indeholder **ingen core-kildekode,
firmwarebinærer, private headers eller tidligere Git-historik**.

**Aktuel status:** `counter/` kan valideres og pakkes. De andre pluginmapper er
migrationsspecifikationer. Den nuværende enhed har endnu ikke Lua-loaderen;
ingen af disse pakker kan køre på nuværende firmware. Der udføres ingen upload
eller netværkskald af værktøjerne i forslaget.

```sh
python3 _tools/hn.py check counter
python3 _tools/hn.py pack counter --out /tmp/counter.hnplugin
python3 -m unittest discover -s _tests -v
```

Hver pluginmappe får beskrivelse, manifest, Lua-kode, konfigurationsschema,
assets, tests, `DEVICE-TEST.md` og licens. Fælles schemas, API-kontrakt og et
simuleret testmiljø må være offentlige. Core-builds og signeringsnøgler må ikke.

Se [API](_sdk/API.md), [enhedstest](_sdk/DEVICE-TEST.md) og
[migrationsplan](_sdk/MIGRATION.md). Licens-/copyright-tekster i den eksisterende
template er bevaret som udgangspunkt og skal kontrolleres før offentliggørelse.

Udvikling og promovering følger `dev` → `test` → `main`; se
[DEVELOPMENT.md](DEVELOPMENT.md). GitHub-reglerne er endnu ikke aktiveret.


## Kategorier på hjemmesiden

`catalog.json` indeholder `categories`: en ordnet liste med `name` og `plugins`.
Hvert plugin-id (mappenavnet) tilhører præcis én kategori. Listen omfatter også
planlagte plugins og eksempler; kategorien ændrer ikke pluginets test- eller
udgivelsesstatus. Tilføj nye pluginmapper til den relevante kategoris `plugins`.

HouseNimble læser kategorierne fra den valgte grens katalog og viser dem som
foldbare grupper i denne rækkefølge. Den første gruppe er åben fra start.
Søgning og filtre åbner automatisk grupper med match. Ukategoriserede nye
mapper kan stadig opdages og vises med en reservekategori.

Kategorier er katalogmetadata. De indgår ikke i pluginets runtime-konfiguration
eller enhedspakke og kræver ingen ændring af den private core eller plugin-API'et.
