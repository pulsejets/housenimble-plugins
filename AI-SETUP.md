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

Der er nu 23 pluginmapper i kategorikonfigurationen (efter tilføjelsen af Spotify):

| Kategori | Pluginmapper |
| --- | --- |
| Dit hjem | overview, water_tank, water_heater, shelly, shelly_lnm, webcam |
| Energi | electricity, power_prices, live_power, watts_live, top_consumers, consumption, growatt |
| Hverdag | calendar, dishwasher |
| Musik | spotify |
| Hobby | kiln, kiln_graph, printer, bambu |
| På farten | flight, id4 |
| Eksempler | counter |

`catalog.json.categories` er en ordnet liste af `{ "name": "Energi", "plugins": [...] }`.
Hvert plugin-id er mappenavnet og tilhører præcis én kategori. Det er metadata til
hjemmesiden, ikke en indstilling der sendes til plugin-runtime. Opdatér listen og
kategoritesten, når mapper tilføjes. Første kategori er åben på hjemmesiden;
søgning/filtre åbner grupper med match. Kategorisering giver ingen releasegodkendelse.

Kataloget er fortsat `draft`, og `installable` er tom. På Flight-feature-branchen
er 20 mapper planlagte Lua-porte, Flight er klar til enhedstest, og counter/Spotify
er eksempler uden udgivelsesmarkering. Eksisterende native funktioner eller beskrivelser
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
Den installerede counter-core tilbyder tekst/knapper og numerisk lager. Den
lokale Flight-core udvider med afgrænset read-only Flight-HTTP og konfiguration;
MQTT, Spotify OAuth og billeder er fortsat ikke understøttet.

Kommandoen nedenfor gælder **kun en branch med implementeret USB-klient** og
kræver, at enhedstest er godkendt. Enheden parres fysisk med en frisk kode:

```sh
python3 _tools/hn.py test counter --port <USB-port> --isolated --duration 840
```

Undersøg `python3 _tools/hn.py --help` og `_sdk/DEVICE-TEST.md` på den konkrete
branch først. Kommandoer i et API-forslag er ikke automatisk tilgængelige.

## Ny Spotify-prototype

`codex/spotify-plugin` er baseret på den lokale `codex/plugin-categories` og har
kategori-/AI-noterne som uuploadede afhængigheder. `spotify/` indeholder ny Lua,
manifest, schema, host-kontrakt og offline Lua-tests. Den private referenceapp blev
kun læst; intet fra dens firmware, login-data eller drivere er kopieret hertil.
Den første udgave styrer Spotify Connect (og Sonos kun når den er tilgængelig
via Connect). Direkte Sonos SOAP/discovery/grupper og fuld SpotifyESP-paritet er
ikke porteret. HTTP/OAuth er endnu ikke leveret til denne pluginversion; den må
ikke markeres som fysisk testet eller Udgivet. Se spotify/README.md.

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


## Flight-udvidelsen · 2026-10-26

Aktuel feature `codex/flight-plugin` bygger videre på de lokale kategori-/AI- og
Spotify-ændringer. Den genbruger den allerede offentlige USB-klient fra
`codex/lua-device-test`, inklusive regressionerne, og tilføjer Flight-config og
capability-kontrol. Det er afhængigt featurearbejde, ikke en merge til dev/main.

`flight/` er nu faktisk Lua med live-liste og har `testable`-status i kataloget.
Den kræver ejerens nye private core med `httpFlight`; denne core er endnu ikke
installeret. Flight er ikke længere i plannedPlugins. Der er 23 mapper: 20
planlagte, to eksempler (counter/spotify) og Flight klar til enhedstest. Det er
ikke en produktionsrelease eller et fysisk testresultat.

Core-granten er kun anonym GET til adsb.fi's positionsendpoint. Spotify OAuth,
player-skrivninger, MQTT og fri LAN-adgang bliver ikke aktiveret af den. Flight
har ingen native kort/logocache i første Lua-version; README beskriver omfanget.
Koden er softwareverificeret, og næste handling er ejerens godkendelse af upload,
ikke at kalde den gamle installerede counter-core Flight-kompatibel.


## Offentlig pluginstandard · 2026-10-26

Ejeren har præciseret fælles standard for ALLE plugins: individuel udviklingstest
uden andre plugins samt firmwarebygning via hjemmesiden. Dette er implementeret
lokalt med samme offentlige .hnplugin/config til CLI/browser og private bundles.
Se _sdk/DEVELOPMENT.md.
Ingen ny GitHub-push, serverdeploy eller fysisk flash er udført i denne ændring.
Counter og Flight understøttes af den aktuelle host; Spotify/migrationer kræver
stadig manglende grants/porte. Arkitekturstandard betyder ikke alle porte færdige.
Kilde/private logs/ELF/header må aldrig ud i public repo. Private slutdele er uden
for webrepo og udleveres kun til byggejobbets autentificerede ejer. USB-loader
bevarer fysisk parring; webprofil/firmwareconfig er kun ikke-hemmelige indstillinger.
Tidligere counter-hardwaretest gælder en ældre build. Ejeren har siden brugt den
native webfirmware med Min konto; aktuelt installeret app-hash er ikke aflæst.
Den nye Lua-/bundle-core er IKKE fysisk installeret/testet.

Verificeret lokalt i denne ændring: 52 webtests; offentlig SDK/config/transport
26 Python-tests + browser-USB-kontrakttest; Flight 13 og Spotify 16 offline-tests.
Chrome med simuleret USB gennem rigtigt offentligt SDK/pakker bestod på desktop
og mobil. Privat Lua/LVGL/USB-bundletest bestod ASan/UBSan i 800 og 1024 pixels.
Et isoleret, autentificeret webbyggejob kørte den rigtige private PlatformIO-
compiler med Counter + Flight, og det færdige fire-dels manifest blev valideret
uden NVS-overlap. Ingen fysisk skærm/aktiv database/container blev ændret.
Docker-imageverifikation er separat og må ikke mærkes bestået før faktisk exit0.
