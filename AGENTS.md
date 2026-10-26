# AI-vejledning · offentlige HouseNimble plugins

Læs [AI-SETUP.md](AI-SETUP.md) ved starten af en ny session. Svar som udgangspunkt
på dansk. Kontrollér branch, status og remote; docs kan høre til en anden branch.

## Ansvar og grænser

- Dette repo er `pulsejets/housenimble-plugins`: offentlige plugins, SDK,
  katalogkonfiguration og den offentlige host-API. Den private implementering
  hører til `pulsejets/housenimble-core`; hjemmesiden er `housenimble/HouseNimble`.
- Kopiér aldrig core-kode, private headers, Git-historik, firmware/ELF/bin/map,
  core-fejldumps, credentials, signeringsnøgler eller private logs hertil.
- Plugins er Lua-tekst og data gennem en versioneret, begrænset host-API.
  Ingen native C/C++, rå pointers, sockets, systemkald, tråde eller filadgang.
- Core ejer Wi-Fi/reconnect, MQTT, HTTP/TLS, tidszone, UI/touch og lagring.
  Dokumenterede fremtidige API'er må ikke forveksles med implementerede grants.
- Hvert plugin skal kunne testes alene på en ejerprovisioneret udviklingsenhed,
  uden core-kilde og uden at installere de øvrige plugins.
- Nye plugins må ikke afhænge af interne Home API-servere, interne databaser
  eller andre plugins. Brug tjenestens API eller MQTT gennem godkendt host-adgang.
- Hver mappe skal have beskrivelse, konfigurationsschema med land/region/global,
  licens og enhedstestvejledning. Bevar licensnotices. Manifest/Lua tilføjes ved portering.
- Runtime-konfiguration, credentials og visningsmetadata er forskellige ting.
  Kategorier ligger i `catalog.json`; de ændrer ikke pluginpakker eller capabilities.

## Git, test og godkendelser

- Oplys repo, branch og mål, og spørg før ny push, publicering, serverdeploy,
  enhedsupload eller ændring af synlighed. Genbrug konkret accept for samme
  handling, men aldrig som generel fremtidig tilladelse.
- Lokale rettelser, tests, dokumentation og lokale commits kan gennemføres.
- Flow: `codex/...` fra `dev` → PR til `dev` → PR til `test` → PR til `main`.
  Ingen direkte produktionsgenvej, force-push eller sletning af miljøbranches.
- Følg DEVELOPMENT.md. Verificér GitHubs aktuelle beskyttelsesregler; ældre noter
  om aktivering og en eksisterende Promotion gate er ikke bevis for håndhævelse.
- En fysisk test skal gælde præcis plugin-commit og kompatibel core-version.
  Del kun redigerede pluginresultater, aldrig privat core-kode, logs eller builds.
- `catalog.json` er kilde til release-status og kategorier. Planlagte mapper eller
  en lokal valideret pakke er ikke en installerbar eller produktionsgodkendt port.
- Branch-opmærksomhed: USB-klienten er på `codex/lua-device-test`. Den separate
  `codex/plugin-categories` bygger fra `dev` og har ikke dermed fået USB-klienten.
  Se AI-SETUP.md; lov ikke enhedstest ud fra en README fra en anden branch.

Normale lokale checks:

```sh
python3 -m unittest discover -s _tests -v
python3 _tools/hn.py check counter
python3 _tools/hn.py pack counter --out /tmp/counter.hnplugin
```

Kør enhedstest kun med faktisk implementeret klient, ejeraccept og frisk fysisk
parring. Gem ikke parringskoder, sessionstokens eller credentials i AI-noter.
Opdatér AI-SETUP.md ved væsentlige ændringer, og markér daterede oplysninger som historik.
