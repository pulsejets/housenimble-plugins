# Ét plugin på en fysisk enhed

**Forudsætning, endnu ikke implementeret:** enheden er provisioneret privat med
udviklings-core, Lua-loader og autentificeret USB-testprotokol. Ingen offentlig
core-download, privat checkout eller core-build kræves på pluginudviklerens computer.
Core-installation er en særskilt, ejerstyret proces.

1. Kør lokale parser-/UI-/kontrakttests. De erstatter ikke fysisk test.
2. Valider og pak kun pluginets mappe. Uændret core bygges ikke igen.
3. Aktivér udviklingstilstand fysisk på enheden og par USB-sessionen.
4. Indlæs pakken i én reserveret, midlertidig testplads. Core afviser ukendt
   API-version, board, filer, budget eller capabilities. Afbrudt upload aktiverer
   aldrig en halv pakke.
5. Testprofilen består af core og dette ene plugin. Andre offentlige plugins
   installeres ikke; på en eksisterende enhed skal de kunne suspenderes under testen.
6. Kontrollér fysisk touch, korrekt visning, offline, reconnect, timeout,
   ugyldigt JSON, tomme/store svar, fuldt lager og gentagen indlæsning/fjernelse.
7. Test et bevidst Lua-loop, for stort svar og callback efter fjernelse. Core
   skal afslutte pluginet, rydde egne ressourcer og bevare netværks-/core-startsiden.
8. Stop testen og kontrollér oprydning. En genstart skal deaktivere en fejlende
   midlertidig pakke, ikke starte en crash-løkke.
9. Gem pluginversion/hash, core-API-version, core-build-id, chiprevision,
   testtrin og resultat. Del kun pluginets redigerede logs, aldrig ELF,
   core-dumps, nøgler eller core-kilde.

Foreslået CLI, når loaderen er bygget:

```text
hn device pair --usb
hn plugin test ./growatt --usb --isolated
hn plugin logs growatt --usb
hn plugin stop --usb
```

Disse enhedskommandoer er endnu ikke implementeret. Den medfølgende `hn.py`
understøtter kun lokal `check` og `pack`; `test` afviser uden at kontakte enheden.
Godkendt produktionsinstallation/signaturkontrol er separat fra midlertidig udviklingstest.
