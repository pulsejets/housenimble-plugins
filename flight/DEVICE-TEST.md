# Flight · softwareverifikation og fysisk enhedstest

Status 2026-10-26: softwareverificeret, afventer ejeraccept til upload og fysisk test.

Bestået lokalt:

- Faktisk Lua 5.4: placering, km/NM, distance/filtrering, alder/null/fejl, units,
  selektion, rate-limit, annullering og gamle svar.
- Privat core: actual loader + manifest/grant, config/JSON-events og LVGL med
  dette offentlige plugin på 800×480 og 1024×600 under ASan/UBSan.
- Privat policy: afvisning af private/andre hosts, credentials, POST, query/fragment,
  ugyldige koordinater/radius og ukendte/null/forkert typede indstillinger.
- Rev1.3-udviklings-core kompileret; netværkskøens eksisterende regressionschecks bestod.
- Lua-model afprøvet med et frisk verificeret HTTPS-svar fra det offentlige API.

**Ikke testet:** fysisk ESP32-TLS/flight-refresh, touch på denne nye side,
offline/reconnect og langtidshukommelse på enheden. Listevisningen inkluderer
ikke native-versionens kortfliser, ruter, flyselskabslogoer eller SD-billedcache.

## Fysisk forløb — kræver konkret ejeraccept

1. Bekræft hardware/revision og den præcise private core-build. Bevar NVS,
   Wi-Fi, partitioner og rollback. Pluginudvikleren skal ikke have core-kilden.
2. Installér den godkendte udviklings-core én gang. Kontrollér boot, Wi-Fi,
   minimal core-startside og `httpFlight` capability. Den gamle counter-core afvises.
3. Kør `hn.py check/pack`, vælg kun `flight`, og par fysisk med en frisk kode.
   Brug `--config` til valideret placering/radius; ingen andre plugins indlæses.
4. Se live kaldesignaler, højde, fart og afstand. Sammenhold med datakilden.
   Kontrollér Opdater, Forrige/Næste og skift mellem m/km/t og ft/kn/NM.
5. Skift til cores indstillinger og tilbage: ingen polling mens skjult og ingen
   gammel callback til frigivet UI. Stop/genindlæs flere gange; core/Wi-Fi fortsætter.
6. Afbryd netværket kontrolleret, se fejl/dataalder, og genopret forbindelsen.
   Test tomt/ugyldigt/stort/429-svar i host-fixtures, ikke ved at misbruge tjenesten.
7. Lad USB-sessionen udløbe; kontrollér frigivne widgets/Lua og ingen fortsatte jobs.
8. Registrér præcis plugin-commit/pakkehash, core-version/API/capabilities,
   boardrevision og faktisk resultat. Del ikke private core-dumps, kode eller tokens.

Ingen markering som Udgivet eller produktion før det faktiske testforløb og
`dev` → `test` → `main` er gennemført. Se også [fælles procedure](../_sdk/DEVICE-TEST.md).
