# Test ét Lua-plugin på en enhed

USB-værktøjet og den private udviklings-core er implementeret på featurebranchen.
Bygning og offline-tests er adskilt fra den endnu ikke gennemførte fysiske prøve.
Enheden skal først provisioneres af ejeren med den rigtige private udviklings-core.
Der findes ingen offentlig core-download; pluginudvikleren behøver kun dette repo.

## Første installation — udføres af ejeren

Ejeren bygger og installerer udviklings-core til den konkrete hardware. Den indeholder
Wi-Fi, touch, display, generelle indstillinger og Lua-host, men ingen legacyplugins.
Installation kræver særskilt ejeraccept og en plan for at vende tilbage til den
nuværende firmware. Enhedsopsætning i NVS bevares; flash må ikke slettes.
Core-genstart indlæser aldrig automatisk en tidligere testpakke.

## På pluginudviklerens computer

Kør fra roden af plugin-repoet:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r _tools/requirements.txt
python3 _tools/hn.py check counter
python3 _tools/hn.py test counter --port /dev/cu.usbmodemDIN_ENHED --isolated
```

På Windows anvendes fx `--port COM5`; aktiver venv via `.venv\Scripts\activate`.
Luk andre serielle terminaler. Vælg porten eksplicit; værktøjet vælger ikke en vilkårlig enhed.
Tryk **USB · par enhed** fysisk på skærmen og skriv koden i terminalens skjulte prompt.
Koden gælder 60 sekunder og spærres efter fem fejl. Sessionstoken gemmes kun i RAM
og udskrives ikke. Brug helst prompten frem for `--pin`, som kan ses i shellhistorik.

Kun denne mappe pakkes og overføres. Intet core-build eller andet plugin overføres.
Pakke og Lua-state er midlertidige i RAM; et ugyldigt/afbrudt upload aktiveres ikke.
Pakker med netværkstilladelser eller billeder afvises i den første API-delversion.

Programmet viser status og holder sessionen i live hvert femte sekund. Test tælleren
med 20 tryk. **Ctrl+C**, skærmens **Stop plugin** eller `--duration 60` stopper testen.
Ved mistet forbindelse stopper core pluginet efter højst 30 sekunder; parring udløber
altid efter 15 minutter. En ny fysisk parring stopper også det gamle plugin.

```sh
# Læs ufølsom core-/pluginstatus uden at starte noget:
python3 _tools/hn.py status --port /dev/cu.usbmodemDIN_ENHED
# Stop fra en anden terminal efter ny fysisk parring:
python3 _tools/hn.py stop --port /dev/cu.usbmodemDIN_ENHED
```

Ingen rå corelogs eller dumps hentes. UI, numerisk pluginlager, hukommelses- og
instruktionsgrænser er implementeret. HTTP/MQTT, billeder, konfigurationseditor,
produktinstallation og signerede releases er endnu ikke understøttet af denne delversion.

## Testnotat og promotion

Notér plugincommit og pakke-SHA-256, core-build-id/API-version, hardware-revision,
20 fysiske tryk, stop/genindlæsning, genstart, offline/reconnect og afbrudt USB.
Gem resultatet i pluginets DEVICE-TEST.md. En normal core-genstart skal vise core,
ikke et fejlende plugin. Pluginets numeriske testdata bevares separat fra coreopsætning.
`dev` → `test` → fysisk prøve → `main` gælder stadig. Automatisk CI er ikke fysisk test.
