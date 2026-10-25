# live_power

Effekt og energimålinger for hus og bil via MQTT.

**Status: planlagt Lua-port.** Den eksisterende native C++-side er ikke kopieret
til dette forslag. Der er endnu ingen installerbar Lua-udgave af dette plugin.
Core-kode, private headers, credentials og Git-historik må aldrig kopieres hertil.

Krav: `main.lua`, `plugin.json`, `config.schema.json`, `LICENSE`, eventuelle
`assets/`, `tests/` og dokumenteret [fysisk enhedstest](DEVICE-TEST.md).

[Konfiguration](config.schema.json): land/marked og sprog er fælles udgangspunkt;
tjenestespecifik region, tidszone, enheder og model vælges pr. plugin.
