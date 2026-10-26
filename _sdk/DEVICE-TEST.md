# Ét plugin på en fysisk enhed

Status 2026-10-26: offentlig USB-klient findes på `codex/lua-device-test` og er
også genbrugt på `codex/flight-plugin`. Den separate kategoribranch har baseline-
klienten. Kontrollér konkret checkout og [AI-SETUP.md](../AI-SETUP.md).

Pluginudvikleren skal kun have det offentlige repo, Python/USB-klienten og en
ejerprovisioneret enhed. Privat core-kilde eller core-genbygning kræves ikke for
hver pluginprøve. En ny host-capability kan kræve en separat, godkendt core-opdatering.

## Lokal validering og pakning

```sh
python3 _tools/hn.py check counter
python3 _tools/hn.py pack counter --out /tmp/counter.hnplugin
python3 -m unittest discover -s _tests -v
```

Pakning eksekverer ikke Lua og beviser ikke hardware-/host-understøttelse.

## Fysisk test — kræver konkret ejeraccept

```sh
python3 -m pip install -r _tools/requirements.txt
python3 _tools/hn.py test counter --port <USB-port> --isolated --duration 840
```

Klienten kræver dev-protokol/API 1. Tryk fysisk “USB · par enhed” og indtast en
frisk sekscifret kode. Sessionstoken holdes kun i RAM. Klienten holder lease aktiv
og stopper pluginet efter testen/Ctrl-C; core stopper også ved manglende heartbeat.
Der indlæses kun den valgte pakke, ikke alle pluginmapper.

Flight kræver den nye `httpFlight` capability og en faktisk Flight-kompatibel core.
Klienten afviser den gamle counter-core, før parring/upload foreslås:

```sh
python3 _tools/hn.py test flight --port <USB-port> --isolated --duration 840 --config /sti/flight-config.json
```

`--config` er valgfrit, ikke-hemmeligt og gælder kun Flight; core validerer værdierne
igen. Se [Flight](../flight/README.md). Spotify kan ikke få Flight-granten til at
virke som OAuth/player-skrivning. MQTT, fri HTTP/LAN og større UI-funktioner er ikke
derfor tildelt. Hostens capability/grants er afgørende, ikke kun manifestets anmodning.

## Checkliste

1. Registrér præcis plugin-commit/pakkehash, core-version/API/capabilities og hardware.
2. Test kun det valgte plugin med fysisk touch og faktisk data. Opstart må ikke sende uønskede writes.
3. Kontrollér fejl/timeouts/tomme/ugyldige/store svar og rate-limit med fixtures.
4. Kontrollér offline/reconnect og dataalder. En simulatortest erstatter ikke fysisk netværk.
5. Skjul/stop/genindlæs og kontrollér oprydning, gamle callbacks og fortsat core/Wi-Fi.
6. Prøv sessionudløb og genstart; et midlertidigt plugin må ikke autoindlæses i en crash-løkke.
7. Gem redigeret testresultat; aldrig credentials, parringskoder eller private core-dumps/builds.

Den tidligere tæller-smoke er ikke en fysisk Flight-test eller en generel
produktionsgodkendelse. Hver port har egen DEVICE-TEST.md. Godkendt produktion,
signaturkontrol og `dev` → `test` → `main` er særskilte trin.


## Fælles udviklingsstandard

Se [udviklingsstandarden](DEVELOPMENT.md) for individuel USB-test, generisk konfiguration og samme pakke i firmwarebygninger gennem hjemmesiden.
