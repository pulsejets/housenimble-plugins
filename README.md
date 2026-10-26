# HouseNimble plugins

Offentligt monorepo med én mappe pr. plugin. Core er en separat, privat
kodebase. Dette repo indeholder **ingen core-kildekode,
firmwarebinærer, private headers eller tidligere Git-historik**.

**Aktuel status på `codex/flight-plugin`:** `counter/` kan valideres, pakkes og
USB-testes med den ejerinstallerede udviklings-core. `flight/` er en faktisk Lua-
side, softwareverificeret og klar til enhedstest med en **ny** core med
`httpFlight`; den nye firmware er endnu ikke installeret. `spotify/` er en
prototype, der stadig mangler OAuth-/host-understøttelse. De øvrige 20 mapper er
migrationsspecifikationer. Ingen af disse udsagn er produktionsgodkendelser.
Se [AI-SETUP.md](AI-SETUP.md) om de forskellige feature-branches.

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
[DEVELOPMENT.md](DEVELOPMENT.md). Kontrollér aktuelle GitHub-regler før promovering;
en ældre statusnote beviser ikke, at branchbeskyttelsen er aktiv.


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


AI og vedligeholdere: start med [AGENTS.md](AGENTS.md) og den daterede
[setup-/branchoversigt](AI-SETUP.md). USB-klient og kategorikonfiguration ligger
foreløbig på separate feature-branches; læs status for den konkrete checkout.


## Spotify-controller

[spotify/](spotify/README.md) er en selvstændig, eksperimentel Lua-controller
med egne offline tests i kategorien Musik. Det er en første delport, ikke en
færdig SpotifyESP-erstatning. HTTP/OAuth i core og fysisk test mangler; direkte
Sonos-grupper og covers er endnu ikke porteret. Den private kildeapp er urørt.


## Flight til enhedstest

[flight/](flight/README.md) er nu en faktisk Lua-side med live flyliste og
begrænset GET-grant. USB-klienten på `codex/flight-plugin` kontrollerer
`httpFlight` capability og accepterer validerede indstillinger via `--config`.
Ny privat udviklings-core skal godkendes/installeres før fysisk test. Kortfliser,
logoer og SD-billeder er ikke porteret. Spotify OAuth aktiveres ikke af Flight.


## Fælles udviklingsstandard

Se [SDK-vejledningen](_sdk/DEVELOPMENT.md) for individuel USB-test, generisk konfiguration og samme pakke i firmwarebygninger gennem hjemmesiden.
