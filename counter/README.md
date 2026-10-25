# Tæller

Et lille Lua-plugin uden netværk. Formålet er at bevise, at kun ét plugin kan
indlæses, bruges med fysisk touch og fjernes igen, mens core beholder Wi-Fi.

**Status: API-udkast.** Kan valideres og pakkes lokalt. Kan endnu ikke køres på
nuværende firmware, som mangler Lua-runtime og udviklingsprotokol.

Konfiguration: land/marked (`GLOBAL`, `DK`, `SE`, `DE`) og sprog (`da`, `en`).
Ingen credentials, landespecifik tjeneste eller interne API-servere kræves.

```sh
python3 _tools/hn.py check counter
python3 _tools/hn.py pack counter --out /tmp/counter.hnplugin
```

Se [enhedstest](DEVICE-TEST.md) og [host-kontrakt](../_sdk/API.md).
