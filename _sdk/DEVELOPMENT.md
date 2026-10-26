# Ét plugin til udviklingstest og firmware

Dette er standarden for alle nye HouseNimble-plugins. Pluginudvikleren behøver
kun dette offentlige repo og en ejerprovisioneret, kompatibel udviklings-core.
Core bygges ikke på ny for hver USB-test, og dens kilde deles aldrig.

## Opret et plugin

Brug `counter/` som minimalt eksempel. Opret din egen `/pluginnavn/` med:

- `plugin.json`: unikt id, navn, beskrivelse, version, API, grants og budgetter.
- `main.lua`: Lua 5.4-tekst med de dokumenterede lifecycle-callbacks.
- `config.schema.json`: land/region/global, sprog og øvrige indstillinger.
- `LICENSE`: licens og nødvendige notices.
- `README.md`: tjeneste, datakilder, opsætning og præcis individuel testvejledning.
- `tests/`: meningsfulde offline-tests af pluginets data og adfærd.

Tilføj kategori og status i `catalog.json`. En katalogpost gør ikke en planlagt
mappe til et fungerende Lua-plugin. Fjern eksempel-id'et fra dit nye manifest;
plugin-id'et adskiller også lagrede værdier på enheden.

Konfiguration bruger **settingsSchema 1**: et lukket objekt
(`additionalProperties: false`), højst 16 felter, primitive typer `string`,
`number`, `integer`, `boolean`, default på alle felter, valgfri enum og relevante
minimum/maximum/minLength/maxLength. Ingen nested objekter, arrays, $ref eller
patterns. Feltnavne er ASCII-bogstav efterfulgt af op til 31 bogstaver/tal/_;
strenge højst 128 tegn og 128 UTF-8-bytes, samlet normaliseret JSON højst 768
bytes. Uunderstøttede schemaer afvises tydeligt. Se `_tools/plugin_config.py`.
Brug aldrig credentials i schema-defaults, Lua, screenshots eller Git.

## Test kun dit plugin

```sh
python3 -m pip install -r _tools/requirements.txt
python3 _tools/hn.py check counter
python3 _tools/hn.py pack counter --out /tmp/counter.hnplugin
python3 _tools/hn.py test counter --port <USB-port> --isolated --duration 840
# Valgfrie ikke-hemmelige overrides:
python3 _tools/hn.py test counter --port <USB-port> --isolated --duration 840 --config /tmp/settings.json
```

Tryk **USB · par enhed** fysisk på skærmen og indtast den nye kode, når klienten
spørger. Koden fra Wi-Fi → Min konto bruges ikke. Gem ikke koder eller tokens.
USB-testen stopper eksisterende firmwareplugins og kører kun den uploadede pakke.
Stop og genindlæs efter hver ændring; Wi-Fi og generelle indstillinger ejes af core.
Testpakken er midlertidig og starter ikke igen efter reboot. Stop med Ctrl-C;
uden heartbeat afslutter core testen efter højst 30 sekunder. Maksimal testtid er
14 minutter i klienten. Kør ikke flere serial-klienter mod samme port.

Dette virker også for et endnu ikke publiceret, lokalt plugin uden GitHub-upload.
Dokumentér præcist plugin-commit, hardware, host-capabilities og faktisk fysisk
resultat. Offline- eller browsermock-tests er ikke fysisk godkendelse.

## Hjemmeside og firmware

**Pluginudvikling** på hjemmesiden henter en fast commit af dette offentlige
repo. Hvert implementeret plugin får egen konfigurationsformular og **Test alene
via USB**. Chrome/Edge på HTTPS eller localhost kræves. Browserklienten er
`_sdk/web-usb.js`; samme canonical `.hnplugin` bruges af CLI, browser og bygning.

Vælg ét til otte kompatible plugins og **Byg firmware med valgte plugins**.
Hjemmesiden gemmer pluginversion, rækkefølge og indstillinger i byggejobbet.
En separat privat worker bygger core; offentlige plugins indeholder kun Lua/data.
Firmwaren indeholder de valgte pakker, starter den første ved boot og tilbyder
valg/skift mellem dem. Kun ét plugin kører ad gangen. Numerisk lager adskilles
pr. plugin-id. Installation sker via USB med separate flashdele uden NVS-erase.

Bygning kræver, at ejeren har tilsluttet den private worker. Den eksisterende
native firmwarebygger er et separat legacy-forløb. Lua-installationen bruger ikke
dens konto-tilknytning eller OTA. Core + Lua-bundles er endnu et udviklingsforløb,
ikke en produktionsrelease. Brug ikke webprofil/firmwareindstillinger til secrets;
credentials skal håndteres gennem en implementeret, separat credential-API.

Nye pluginversioner skal først push'es med ejeraccept, før hjemmesiden kan hente
den faste offentlige commit. UI ændrer ikke et gammelt byggejobs pakker.

## Implementeret host og begrænsninger

Generiske plugins kan bruge tekst, knapper, config/events og numerisk lager
inden for budgets. Denne host har `settingsSchema: 1`, `firmwareBundles: true`
og `bundleSlots: 8`. Flight har derudover en specifik anonym HTTPS-GET-grant til
adsb.fi. Dets udbydervilkår om personlig, ikke-kommerciel brug gælder fortsat.

MQTT, generelle HTTP-grants, Spotify OAuth/player-skrivninger og billeder/assets
mangler stadig i hosten. Plugins, som kræver dem, vises med begrundelse og kan
ikke fejlagtigt vælges til test/bygning. Arkitekturen er fælles for alle plugins;
hver gammel native side skal stadig have en faktisk Lua-port og eventuelle
host-grants, før den kan testes. Denne ændring porterer dem ikke automatisk.
