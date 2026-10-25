# HouseNimble plugins

Offentlige Lua-plugins og USB-testværktøj. Den fortrolige core ligger i et separat,
privat repository. Dette repo indeholder ingen core-kilde, intern historik eller firmware.

`counter/` kan valideres, pakkes og testes med en ejerinstalleret udviklings-core.
USB-testfunktionen er implementeret; første fysiske test afventer godkendt core-installation.
De andre pluginmapper er fortsat migrationsspecifikationer, ikke færdige Lua-porte.

```sh
python3 _tools/hn.py check counter
python3 _tools/hn.py pack counter --out /tmp/counter.hnplugin
python3 -m unittest discover -s _tests -v
```

Se [test direkte på en enhed](_sdk/DEVICE-TEST.md) for Python/USB-opsætning,
fysisk parring og test af kun ét plugin. Ingen core-kilde eller core-genbygning
kræves på pluginudviklerens computer. Første delversion understøtter tekst,
knapper og numerisk lager; HTTP/MQTT og større UI-funktioner kommer senere.

Hver pluginmappe har README, konfigurationsschema, DEVICE-TEST.md og licens;
manifest og Lua tilføjes efterhånden som pluginet porteres. Land/region/global
beskrives pr. plugin. Se [API](_sdk/API.md) og [migration](_sdk/MIGRATION.md).

Udvikling følger `dev` → `test` → `main`; se [DEVELOPMENT.md](DEVELOPMENT.md).
Core-builds og signeringsnøgler må aldrig indgå her eller i offentlig CI.
Eksisterende copyright-/licensnotices bevares og skal gennemgås før produktdistribution.
