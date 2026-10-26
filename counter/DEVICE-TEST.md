# Enhedstest: counter

Fysisk smoke-test bestået 2026-10-26 på ESP32-P4 rev1.3 / Waveshare 7B.
Core-API 1, core-build-id `afe8f5c2252afc72`; plugin/SDK-kode fra `5b61e42`.
Pakkens SHA-256: `d508df6257925ba53d70ff269bbf6a05ca5a0f9ae01bc8ff90a1ad53adbc63e9`.
Ingen core-kilde, privat build eller corelog indgår i dette offentlige testnotat.

- Ejeren bekræftede, at tæller og Tæl op vises, og at et fysisk tryk øger tallet.
- Fysisk USB-parring og upload af kun counter lykkedes: 2 widgets / 12487 bytes Lua-RAM.
- Stop gav 0 widgets / 0 bytes Lua-RAM; genindlæsning lykkedes uden core-genbygning.
- Defekt ZIP blev afvist; en bevidst Lua-løkke blev stoppet af instruktionsbudgettet.
  Korrekt counter kunne derefter indlæses igen.
- Wi-Fi var tilsluttet under alle kontroller. Efter 33 sekunder uden heartbeat
  var pluginet automatisk fjernet, uden tab af Wi-Fi.

Testen sluttede med pluginet stoppet med vilje. Start en ny test med frisk fysisk
parring; værktøjet skal forblive åbent. Se [USB-proceduren](../_sdk/DEVICE-TEST.md).

## Fuld tjekliste — endnu ikke afsluttet

Præcis 20 fysiske tryk, genstart med kontrol af gemt tal, tvunget Wi-Fi-udfald/
genforbindelse, fuldt lager og afbrudt fysisk upload er endnu ikke bekræftet på
hardware. Native tests dækker flere af disse fejltilfælde; de erstatter ikke fysisk test.
Kontrollér også coreknapper og Indstillinger. Ingen produktionsgodkendelse er givet.
