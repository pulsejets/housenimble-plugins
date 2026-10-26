# HouseNimble plugins · setup til næste AI-session

Statusdato: **2026-10-26**. Offentlig dokumentation uden core-implementation,
credentials eller private enhedsdata. Commitreferencer er funktionelle milepæle
før denne dokumentationsopdatering, ikke et løfte om nuværende HEAD eller release.

## De tre repos

| Repository | Formål |
| --- | --- |
| `pulsejets/housenimble-core` | Fortrolig core; altid privat, aldrig kopieret hertil |
| `pulsejets/housenimble-plugins` | Dette offentlige katalog, plugins og SDK |
| `housenimble/HouseNimble` | Hjemmesiden housenimble.com, opsætninger og katalogvisning |

Pluginudvikleren skal kun behøve dette repo og en enhed med en separat,
ejerinstalleret udviklings-core. Core vedligeholder Wi-Fi og fælles tjenester.
Et valgt plugin kan testes isoleret; de øvrige plugins eller private core-kilder
skal ikke installeres eller udleveres. Målmodellen er Lua gennem afgrænset host-API,
ikke native firmwarebygning pr. offentligt plugin.

Nye plugins skal virke uden obligatoriske interne Home API-servere/databaser
eller andre plugins. Netværk og credentials håndteres af godkendte host-tjenester.
Kopiér ikke privat eksisterende C++ til et offentligt Lua-plugin.

## Struktur og kategori-konfiguration

```text
catalog.json                 status, installable, plannedPlugins og categories
<pluginnavn>/README.md       formål, data, land/region og opsætning
<pluginnavn>/config.schema.json
<pluginnavn>/DEVICE-TEST.md  isoleret test og ærlige resultater/begrænsninger
<pluginnavn>/LICENSE
<pluginnavn>/plugin.json    når manifestet er implementeret
<pluginnavn>/main.lua       når porten er implementeret
_sdk/                      offentlig kontrakt og testvejledning
_tools/                    validering, pakning og branchespecifik USB-klient
_tests/                    offentlige checks; ingen privat core nødvendig
```

Der er 22 pluginmapper i kategorikonfigurationen:

| Kategori | Pluginmapper |
| --- | --- |
| Dit hjem | overview, water_tank, water_heater, shelly, shelly_lnm, webcam |
| Energi | electricity, power_prices, live_power, watts_live, top_consumers, consumption, growatt |
| Hverdag | calendar, dishwasher |
| Hobby | kiln, kiln_graph, printer, bambu |
| På farten | flight, id4 |
| Eksempler | counter |

`catalog.json.categories` er en ordnet liste af `{ "name": "Energi", "plugins": [...] }`.
Hvert plugin-id er mappenavnet og tilhører præcis én kategori. Det er metadata til
hjemmesiden, ikke en indstilling der sendes til plugin-runtime. Opdatér listen og
kategoritesten, når mapper tilføjes. Første kategori er åben på hjemmesiden;
søgning/filtre åbner grupper med match. Kategorisering giver ingen releasegodkendelse.

Kataloget er fortsat `draft`, `installable` er tom, og 21 mapper er planlagte
Lua-porte. Counter er et eksempel. Eksisterende native funktioner eller beskrivelser
betyder ikke, at deres tilsvarende offentlige Lua-plugin er implementeret.

## Parallelle feature-branches — vigtigt

- `codex/lua-device-test`, milepæl `6573bfb`, er uploadet; draft-PR
  https://github.com/pulsejets/housenimble-plugins/pull/1 til `dev`.
  Her findes den faktiske Python/USB-klient og dokumenteret første counter-smoke.
- `codex/plugin-categories`, milepæl `4b4ff70`, blev oprettet fra `origin/dev`
  for kun at ændre katalogmetadata. Kategoriændringen var endnu ikke push'et.
  Denne branch har baseline-klienten, hvis `test` afviser uden at kontakte enheden.
- En feature-PR er ikke en merge til `dev`, `test` eller `main`. Kontrollér faktisk
  Git-historik før test eller promovering. Overfør ikke alle ændringer mellem de
  to branches blot for at opdatere kategorier eller dokumentation.

På USB-feature-branchen er counter fysisk vist og brugt; stop/genindlæsning og
udvalgte fejlgrænser blev afprøvet 2026-10-26. Det er en smoke-test, ikke fuld
produktionsgodkendelse. Core-builddetaljer og private rapporter hører til core-repoet.
Den aktuelle udviklings-API tilbyder tekst/knapper og numerisk lager. HTTP/MQTT,
billeder og større UI-/konfigurationsfunktioner er fortsat fremtidigt arbejde.

Kommandoen nedenfor gælder **kun en branch med implementeret USB-klient** og
kræver, at enhedstest er godkendt. Enheden parres fysisk med en frisk kode:

```sh
python3 _tools/hn.py test counter --port <USB-port> --isolated --duration 840
```

Undersøg `python3 _tools/hn.py --help` og `_sdk/DEVICE-TEST.md` på den konkrete
branch først. Kommandoer i et API-forslag er ikke automatisk tilgængelige.

## Hjemmesidens integration

Web-feature `codex/public-plugin-catalog` i `housenimble/HouseNimble` viser `/plugins`.
Den henter én begrænset ZIP-snapshot fra dette offentlige repos `main`, `test`
eller `dev`; standard er `main`. Feature-branches indgår ikke automatisk.
Kategorier/rækkefølge læses fra den valgte grens katalog. Webændringen `8a781ae`
med foldbare grupper var lokal; første webkatalog `6909061` var push'et.
Visning er ikke installation. Opsætningssidens native firmwareplugins er separat.

## Genoptagelse og næste arbejde

1. Læs AGENTS.md, git status, branch, sidste commits og remote.
2. Brug den branch, der passer til opgaven, og kontrollér faktisk implementeret API.
3. Kør de relevante offentlige tests. Sidste kategori-check havde 11 beståede tests;
   USB-feature har yderligere egne transporttests. Testtal er branchespecifikke.
4. Ejeren har også bedt om strømprisplugin på enheden. `electricity/` er ikke klar;
   der mangler godkendt netværksadgang i host-API og den faktiske Lua-port.
5. Følg feature → dev → test → main. Spørg før ny push eller enheds-/serverupload;
   oplys præcise repos og branches. En docs-opdatering er ikke uploadaccept.

Branchbeskyttelse og PR-status skal verificeres på ny, når de er relevante.
Dokumentér kun test, der faktisk er udført; gem aldrig tokens, parringskoder,
private logs eller core-artifacts her.
