# Tæller

Et lille Lua-plugin uden netværk. Formålet er at bevise, at kun ét plugin kan
indlæses, bruges med fysisk touch og fjernes igen, mens core beholder Wi-Fi.

**Status:** Lua-runtime og USB-test er implementeret i udviklings-core.
Fysisk installation/test afventer ejeraccept; den hidtidige firmware kan ikke
indlæse Lua-pakker før denne engangsopdatering.

Schemaet beskriver land/marked (`GLOBAL`, `DK`, `SE`, `DE`) og sprog (`da`, `en`).
Første runtime-delversion anvender kun `GLOBAL` og `da`; indstillingseditor kommer senere.
Ingen credentials, landespecifik tjeneste eller interne API-servere kræves.

```sh
python3 _tools/hn.py check counter
python3 _tools/hn.py pack counter --out /tmp/counter.hnplugin
```

Se [enhedstest](DEVICE-TEST.md) og [host-kontrakt](../_sdk/API.md).

USB-test af denne mappe er implementeret. Enheden skal først have ejerinstalleret udviklings-core; første fysiske prøve afventer godkendelse. Se DEVICE-TEST.md.
