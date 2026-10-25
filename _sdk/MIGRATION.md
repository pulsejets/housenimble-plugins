# Fra samlet firmware til privat core og offentlig Lua-kode

De godkendte navne er `pulsejets/housenimble-core` (privat) og
`pulsejets/housenimble-plugins` (offentligt). Begge repositories er oprettet af ejeren og verificeret 2026-10-25.
Første upload af migrationsgrundlag, branchstruktur og CI er godkendt 2026-10-25.
Branchbeskyttelse er endnu ikke aktiveret; enhedsupload er ikke godkendt.

## Fortrolighed før første flytning

- Bekræft det nye core-repos private synlighed med ejeradgang før første push.
  Et anonymt 404-svar fra det nuværende home-api beviser ikke synlighedsindstillingen.
- Offentligt plugin-repo oprettes fra en ren mappe uden gammel `.git`-historik.
  Brug ikke et offentligt fork, Git-submodule til core eller kopiering af hele firmware-mappen.
- Core-filer og private artifacts bliver aldrig input til offentlig CI.
- Signeringsnøgler og rigtige credentials skal ikke i nogen Git-historik.
- Kortlæg eksisterende MIT-, ophavsrets- og tredjepartsnotices før produktlicensen
  fastlægges. Et nyt privat repo kan ikke tilbagekalde tidligere udleverede kopier.
- Fortrolighed for fremtidig kildekode er et mål; absolut beskyttelse mod analyse
  af en fysisk enhed eller en udleveret firmwarebinær kan ikke loves.

## Faser og konkrete godkendelsespunkter

1. Privat core-repo og separat offentligt plugin-grundlag, kontrolleret filudvælgelse.
2. Minimal core-startside uden plugin-afhængigheder, med Wi-Fi, generelle
   indstillinger, diagnostik og en ejerstyret testtilstand.
3. Privat Lua-runtime med hukommelses-/instruktionsgrænser, isolerede UI-handles,
   lifecycle, sikkert lokalt lager og oprydning efter fejl.
4. Første fysisk bevis: counter indlæses/fjernes uden andre plugins og uden
   at genbygge core. Dokumentér begge relevante P4-revisioner.
5. Godkendt HTTP/TLS- og MQTT-API; test Growatt som første netværksplugin.
6. Portér øvrige plugins enkeltvis. Calendar/OAuth, flykort, webcam og Shelly-
   provisioning kræver udvidede, kontrollerede host-funktioner. Interne API- og
   databaseafhængigheder i ældre plugins skal fjernes eller have selvstændige datakilder.
7. Versionerede, signerede pakker og katalog. Offentlig CI har ingen core-token,
   private checkouts eller signeringsnøgle; ukendt PR-kode køres uden ejerens secrets.
8. Fjern legacy C++-plugins fra core-produktbygningen, når deres Lua-afløser
   består kontrakt-, offline- og fysisk enhedstest. Bevar rollback indtil da.

Den eksisterende firmware og enhed er uændret. Nuværende native plugins kan ikke
blot omdøbes til Lua eller flyttes ud af source-træet og blive dynamiske.
Der er ingen Lua-loader eller fungerende enheds-upload i dette forslag.
