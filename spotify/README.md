# Spotify og Sonos · første selvstændige Lua-udgave

Eksperimentel controller til Spotify Connect, inklusive Sonos-højttalere, **hvis
Spotify faktisk eksponerer dem som tilgængelige og styrbare Connect-enheder**.
Højttaleren afspiller lyden; pluginet streamer eller downloader ikke lyd.
Kategori: **Musik**. GLOBAL og land/marked vælges i konfigurationen.

**Status: implementeret Lua-prototype, ikke en færdig SpotifyESP-port eller
produktionsudgave.** Den faktiske Lua-kode er testet offline. Den kræver generisk
HTTP, OAuth-credentialbinding og tick-events fra core. Disse funktioner er ikke
bevist tilgængelige på ejerens installerede udviklings-core. Biblioteket skal
vise pluginet som et Lua-eksempel, ikke Udgivet. Der er ikke udført fysisk test.

## Hvad er implementeret?

- Vælg en eksplicit Connect-højttaler med Forrige/Næste og Vælg. Ingen implicit
  brug af den enhed, Spotify tilfældigvis har aktiv, og ingen automatisk afspilning.
- Vis titel, kunstner, højttaler og kendt lydstyrke. Data fra en anden aktiv
  højttaler slettes i stedet for at blive mærket som den valgte.
- Afspil/pause, forrige/næste, lydstyrketrin, shuffle og gentagelse.
- Op til otte ventende kommandoer. Enheden genvalideres med Spotify før hver
  skrivning; Next/Previous bliver ikke slået sammen. Tvetydige skrivninger gentages ikke.
- Bibliotek-knappen skifter mellem egne playlister, gemte sange, konfigureret
  søgning og afspiller. Første ti resultater kan vælges med Forrige/Næste.
  Afspil sender kun et valideret Spotify-URI til den valgte enhed.
- Dansk/engelsk, kontrollerede svarstørrelser, tilbageholden polling, 429/Retry-After,
  annullering ved skjul/fjernelse og ignorering af gamle svar.
- Uden netværksbinding viser siden en ærlig besked. Den viser ikke syntetisk musik.

UI'et bruger de eksisterende side-/tekst-/knapprimitiver (12 widgets), og der
kopieres ingen private drivere, fonte, C++-filer, callbacks eller login-data.

## Hvad mangler fra SpotifyESP?

Direkte Sonos SSDP/SOAP, gruppestyring og Sonos-favoritter er **ikke porteret**.
Det samme gælder cover/thumbnail-cache, fuld søgetastatur-/liste-UI, flere sider
med resultater, favorit-skrivning, tilføjelse til playliste og gemte Sonos-rum.
Connect-vejen er ikke en erstatning for alle disse funktioner. Ukendte eller
begrænsede enheder må aldrig udløse en lokal fallback.

OAuth/PKCE, tokenrefresh og sikre credentials skal leveres af core. Der er ingen
Mac-bridge, Home API, intern database eller anden plugin-afhængighed.
Se [HOST-CONTRACT.md](HOST-CONTRACT.md) for nødvendige bindinger og [enhedstest](DEVICE-TEST.md).

## Konfiguration og login

`config.schema.json` indeholder land, sprog, valgfrit eksplicit device-id,
polling (10–300 sekunder), lydstyrketrin (1–10 procent) og søgetekst.
`GLOBAL` udelader marked fra søgningen; et Spotify-brugertoken kan give
kontoens marked forrang. Der vælges ikke en højttaler ud fra land eller navn.

Core skal lade ejeren tilslutte Spotify med Authorization Code + PKCE og binde
profilen `spotify` til netop dette plugin/origin og godkendte ruter. Nødvendige
scopes: `user-read-playback-state`, `user-modify-playback-state`,
`playlist-read-private`, `playlist-read-collaborative`, `user-library-read`.
Ingen Client Secret, access-token eller refresh-token må indgå i schema/Lua/Git.
Adgang afhænger også af Spotify-kontoens/appens tilladelser; playback-API'et kræver Premium.

## Lokal, isoleret test og pakning

Kør fra plugin-repoets rod, med testafhængigheder i et separat miljø:

```sh
python3 -m pip install -r spotify/tests/requirements.txt
python3 -m unittest discover -s spotify/tests -v
python3 _tools/hn.py check spotify
python3 _tools/hn.py pack spotify --out /tmp/spotify.hnplugin
```

Testene kører den faktiske `main.lua` i Lua 5.4 med syntetiske HTTP-svar og en
foreslået host-adapter. Ingen Spotify-konto, Sonos-enhed, privat core eller den
oprindelige SpotifyESP-mappe tilgås. De beviser ikke, at host-bindingen findes.

## Oprindelse og kilder

SpotifyESP blev kun læst for at forstå ejerens ønskede funktioner. Denne mappe
indeholder ny Lua-kode og egne tests; den private firmware og tredjepartsfonte er
ikke kopieret. Den oprindelige mappe ændres eller bygges ikke af dette arbejde.
MIT her omfatter kun denne nye plugin-kode, ikke den private referenceapplikation.

Officielle specifikationer:
[Spotify Web API](https://developer.spotify.com/documentation/web-api),
[PKCE](https://developer.spotify.com/documentation/web-api/tutorials/code-pkce-flow),
[playback](https://developer.spotify.com/documentation/web-api/reference/get-information-about-the-users-current-playback),
[device-id ved afspilning](https://developer.spotify.com/documentation/web-api/reference/start-a-users-playback),
[enheder](https://developer.spotify.com/documentation/web-api/reference/get-a-users-available-devices),
[rate limits](https://developer.spotify.com/documentation/web-api/concepts/rate-limits).
