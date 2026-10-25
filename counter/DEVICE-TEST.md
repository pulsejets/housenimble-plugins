# Enhedstest: counter

Status: native runtime-/LVGL-tests er gennemført; fysisk test afventer ejerens uploadaccept.
Følg [USB-proceduren](../_sdk/DEVICE-TEST.md). Vælg kun `counter/`.

1. Par fysisk og start pluginet med `hn.py test counter --port PORT --isolated`.
2. Kontrollér 20 tryk på Tæl op og korrekt opdatering uden UI-frys.
3. Stop og genindlæs; tallet skal være gemt. Kontrollér også genstart: core skal starte uden pluginet.
4. Kontrollér Wi-Fi offline/reconnect, afbrudt upload og USB-frakobling: plugin stopper efter højst 30 sekunder uden heartbeat.
5. Coreknapper, Stop plugin og Indstillinger skal fortsat fungere.

Testpakken indeholder ikke andre plugins. Gem core-build-id, plugin-SHA og fysisk resultat her efter testen.
