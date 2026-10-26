# Flight · host-kontrakt, API 1-udvidelse

Flight bruger de eksisterende UI-primitiver og lifecycle samt følgende afgrænsede
HTTP-del-API. Capability annonceres som `hello.capabilities.httpFlight=true`.
En ældre core må ikke accepteres, blot fordi den tilbyder `coreApi=1`.

```lua
local id = ctx.http.request({
  method="GET",
  url="https://opendata.adsb.fi/api/v3/lat/55.67610/lon/12.56830/dist/16.199",
  tag="<instans>:<sekvens>", timeout_ms=8000, max_response_bytes=32768
})
ctx.http.cancel(id)
```

Kun anmodet og host-godkendt Flight-grant eksponerer `ctx.http`. Ukendte felter,
credentials og andre metoder afvises. Request returnerer et positivt id eller nil
ved afvist grant/rate-limit/fuld kø. Callback er altid asynkron og kommer kun på
UI-tråden med `name="http"`, `id`, uændret `tag`, `status`, `now_ms`, eventuel
`error`, `retry_after_ms` og et begrænset dekodet `json`-objekt. Eventets `json.ac`
indeholder kun scalarfelterne `hex`, `flight`, `r`, `t`, `lat`, `lon`, `alt_baro`,
`gs`, `track`, `seen_pos`; højst 80 rækker, med `json.truncated` ved begrænsning.
Tjenestens root `now` kan medfølge; det er ikke hostens monotone tidsbasis.

Host laver TLS-validering og håndhæver præcist origin/path, koordinater, radius,
requestsinterval, ingen redirects/credentials og separate rå-/JSON-/Lua-budgetter.
Der følges ingen links fra datakilden. Fejl svarer med faste, ufølsomme fejltyper.
Lange numeriske Retry-After-pauser bevares også efter stop/genindlæsning.

`name="tick", now_ms=<monotone millisekunder>` leveres til synligt plugin.
Skjul/stop annullerer job og timers uden at frigive en payload, mens en worker
stadig bruger den. Gamle svar må ikke leveres til en ny plugininstans.
Pluginet har højst ét request i gang og validerer id/tag, data og alder igen.

Host validerer schema-defaults og valgfri USB `begin.config` mod det afgrænsede
Flight-feltsæt. Ingen credentials, andre indstillinger eller ukendte felter tillades.
Konfiguration kopieres til `ctx.config`, ikke en global database.

Denne binding er **ikke** en fri HTTP/OAuth- eller Sonos-tjeneste. Spotify-pluginets
krav til OAuth og player-skrivninger er fortsat ikke understøttet af denne Flight-grant.
