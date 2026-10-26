# Tæller

Et lille Lua-plugin uden netværk. Formålet er at bevise, at kun ét plugin kan
indlæses, bruges med fysisk touch og fjernes igen, mens core beholder Wi-Fi.

**Status:** Lua-runtime og USB-test er implementeret i udviklings-core.
Første fysiske smoke-test er bestået 2026-10-26 på en ejerinstalleret udviklings-core.
Den hidtidige firmware kræver stadig en engangsopdatering før Lua-pakker kan indlæses.

Schemaet beskriver land/marked (`GLOBAL`, `DK`, `SE`, `DE`) og sprog (`da`, `en`).
Første runtime-delversion anvender kun `GLOBAL` og `da`; indstillingseditor kommer senere.
Ingen credentials, landespecifik tjeneste eller interne API-servere kræves.

```sh
python3 _tools/hn.py check counter
python3 _tools/hn.py pack counter --out /tmp/counter.hnplugin
```

Se [enhedstest](DEVICE-TEST.md) og [host-kontrakt](../_sdk/API.md).

USB-test af denne mappe er implementeret. Enheden skal først have ejerinstalleret udviklings-core; første fysiske smoke-test er bestået, mens den fulde tjekliste afventer. Se DEVICE-TEST.md.
