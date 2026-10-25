# Offentlig plugin-kodebase

- Dette repository må kun indeholde plugins og den offentlige API-kontrakt.
- Kopiér aldrig core-kode, private headers, Git-historik, firmware/ELF/map-filer,
  credentials, signeringsnøgler eller core-fejldumps hertil.
- Plugins er Lua-tekst og bruger kun den versionerede host-API. Ingen native C/C++,
  rå pointers, sockets, systemkald, tråde, filer eller interne serverafhængigheder.
- Hver pluginmappe er selvstændig og skal testes isoleret. Core ejer Wi-Fi,
  reconnect, MQTT, HTTP/TLS, tidszone, display/touch og begrænset lokalt lager.
- Beskriv region/land/global understøttelse i pluginets README og schema.
- Test på enheden kræver en separat, privat provisioneret udviklings-core.
- Ingen push, publicering, upload eller ændring af repository-synlighed uden
  konkret godkendelse fra ejeren. Native legacykode er ikke en Lua-port. Lua-counter/USB er implementeret lokalt,
  men første fysiske prøve afventer godkendt udviklings-core.

- Udviklingsflow: feature-PR → dev → test → main. Ingen direkte genvej til
  produktion. Se DEVELOPMENT.md; fysisk test skal gælde præcis test-commit.
  Første branch-/CI-upload er godkendt 2026-10-25. Plugin-repoets branches er beskyttet; core var ved seneste kontrol stadig
  ubeskyttet. Verificér remote før senere ændringer. Senere push/deploy kræver konkret accept.
