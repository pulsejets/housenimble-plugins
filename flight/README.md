# Flight · fly i nærheden

En selvstændig Lua-side, der henter fly i nærheden direkte fra
[adsb.fi](https://adsb.fi/) gennem cores afgrænsede HTTPS-binding.
Ingen Home API, database, login eller andre plugins er nødvendige.

**Status 2026-10-26: klar til enhedstest med den nye Flight-kompatible udviklings-core.**
Lua, den faktiske private loader/LVGL og firmwarebygning er verificeret lokalt.
Pluginet og den nye core er **ikke installeret eller fysisk testet** på ejerens enhed.
Den tidligere installerede counter-core understøtter ikke Flight-netværket.

## Visning og betjening

- Liste over fly med kaldesignal, afstand, højde, fart og retning.
- Registrering, type og position for det valgte fly. Forrige/Næste bevarer valget
  efter opdatering, når samme fly stadig findes.
- Filtrering efter placering/radius, friske positioner og eventuelt fly på jorden.
- Sortering efter afstand, metrisk/luftfarts-enheder, manuel og automatisk opdatering.
- Dataalder, fejl og rate-limit vises. Gamle data bevares tydeligt ved udfald;
  gamle positioner mærkes GAMMEL/OLD. Ukendte tal bliver ikke til nul.
- Op til 80 modtagne fly; ved afgrænset svar vises en begrænsningsmarkering.
  Det er ikke en garanti for alle eller de globalt nærmeste fly ved store områder.
- Dansk/engelsk og synlig kildeangivelse.

**Denne første Lua-version er en listevisning.** Kortfliser, ruteopslag,
flyselskabslogoer og SD-billedcache fra den gamle native side er ikke porteret.
De er ikke forudsætninger for live-listen og skal ikke vises som implementerede.
Data kan være ufuldstændige og afhænger af modtagere og tjenestens dækning.

## Konfiguration

Skemaet indeholder GLOBAL, sprog, breddegrad, længdegrad, radius (1–450 km),
opdatering (10–300 sekunder), antal fly (1–80) og visning af fly på jorden.
Standardplaceringen er **Københavns centrum**, ikke ejerens hjem. Land/område
bestemmes af koordinater; der kræves ingen intern geokodning eller database.

Gem eksempelvis denne **ikke-hemmelige** fil uden for Git som `flight-config.json`:

```json
{"latitude":55.6761,"longitude":12.5683,"radius_km":30,"language":"da"}
```

Hent/installer først en ejerautoriseret udviklings-core med capability `httpFlight`.
Testklienten kontrollerer dette før fysisk parring og afviser en ældre core:

```sh
python3 -m pip install -r _tools/requirements.txt
python3 _tools/hn.py test flight --port <USB-port> --isolated --duration 840 --config /sti/flight-config.json
```

Omitér `--config` for schemaets standarder. Core validerer alle værdier igen.
Dette kræver ingen genbygning af core pr. ændring eller installation af andre plugins.
Der er endnu ingen generel indstillingseditor på skærmen til Lua-pluginers felter;
konfigurationen leveres ved USB-test. Wi-Fi og generelle indstillinger ejes af core.

## Afgrænset netværk

Manifestet anmoder kun om `https://opendata.adsb.fi`. Core giver kun dette
plugin en anonym **GET**-adgang til `/api/v3/lat/LAT/lon/LON/dist/NM` med validerede
koordinater/radius. Kilometer omregnes til NM. Ingen redirects, frie LAN-mål,
credentials, cookies eller andre origins. Lua kan ikke tilføje headers eller token.

Netværksarbejdet kører uden for UI/Lua. Rå svardata, JSON, jobkø og leveret resultat
har separate budgetter. Core leverer kun godkendte scalarfelter for op til 80 fly.
Nye requests begrænses også i hosten, så genindlæsning ikke omgår tjenestens pause.
Callbacks annulleres ved skjul/fjernelse og må ikke ramme en ny plugininstans.
Se [HOST-CONTRACT.md](HOST-CONTRACT.md) og [enhedstest](DEVICE-TEST.md).

## Lokal test og pakning

```sh
python3 -m pip install -r flight/tests/requirements.txt
python3 -m unittest discover -s flight/tests -v
python3 _tools/hn.py check flight
python3 _tools/hn.py pack flight --out /tmp/flight.hnplugin
```

De offentlige tests kræver ingen privat core, fysisk enhed eller netværkskonto.
De udfører den faktiske Lua-kode med syntetiske svar. Privat core har derudover
testet samme offentlige Lua-pakke gennem sin reelle loader, JSON/config-binding
og LVGL på to skærmstørrelser. En lokal modelkontrol med en frisk HTTPS-respons
fra den offentlige kilde bestod også. Dette er ikke en fysisk test af ESP32-netværk.

## Data og vilkår

Kilde: [adsb.fi API](https://github.com/adsbfi/opendata). v3-positionsendpointet
anbefales til nye integrationer og tillader radius op til 250 NM.
API'et er til personlig, ikke-kommerciel brug; kommerciel anvendelse kræver en
særskilt aftale/egnet datakilde. Bevar kildeangivelsen i UI. Pluginets nye Lua-kode
er MIT; det ændrer ikke dataleverandørens vilkår. Ingen privat C++ er kopieret hertil.
