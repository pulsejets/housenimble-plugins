# Spotify-pluginets nødvendige host-binding · forslag

Dette er **krav til en kommende binding**, ikke dokumentation for allerede
implementeret core. Pluginet bruger udkast-API 1's UI/lifecycle og en konkret
HTTP-form nedenfor. Løsningen må ikke implementeres som en intern mellemserver.
Privat core-kode og SpotifyESP skal ikke ændres som del af denne pluginleverance.

## UI og konfiguration

`ctx.ui.page`, `label`, `button`, `set_text` følger counter-eksemplet. Maksimalt
12 widgets. Core validerer `config.schema.json`; pluginet begrænser også værdier
og metadata. Ingen string-storage kræves, og der gemmes ikke brugertokens.

Core kalder create/show/hide/event/destroy. Tick-events leveres kun til aktivt
plugin: `{name="tick", now_ms=<monotont millisekundtal>}`. Alle HTTP-events får
samme monotone tidsbasis. Ingen polling i et skjult/fjernet plugin.

## HTTP

```lua
local id = ctx.http.request({
    method = "GET", -- GET / PUT / POST på nedenstående specifikke ruter
    url = "https://api.spotify.com/v1/me/player/devices",
    credential = "spotify", -- kun et alias; aldrig et token til Lua
    tag = "<livscyklus>:<generation>:<sekvens>",
    timeout_ms = 8000,
    max_response_bytes = 32768,
    json = nil -- valideret JSON-objekt ved afspilning af URI
})
ctx.http.cancel(id)
```

Request er asynkron og må ikke kalde Lua tilbage før returnering. Returnér nil
ved manglende grant/kapacitet. Host'en skal levere ét succes-/fejl-event for et
accepteret job (bortset fra annullerede jobs). Et resultat har `name="http"`,
`id`, uændret `tag`, HTTP `status`, afgrænset dekodet `json`, `now_ms` og ved
429 en normaliseret `retry_after_ms`. Fejl markeres med `error`; ingen rå headers,
credentials eller privat log sendes til pluginet. JSON-null bliver nil.

Host'en håndhæver origin/path/method/grant, TLS-verifikation, ingen redirects,
timeouts, svar-/JSON-budgetter og køer. Den må ikke følge `href`, `next`,
cover-URL'er eller andre vilkårlige links fra Spotify-svar på Lua's vegne.
Requests får ikke adgang til andre plugins, LAN, Home API eller databaseservere.
Ingen automatisk gentagelse af PUT/POST eller fallback til anden transport.
Global Retry-After skal håndhæves på tværs af Spotify HTTP/tokenjobs og plugin-
genindlæsning; lange serverpauser må ikke forkortes. OAuth-refresh må ikke genafspille
en tvetydig player-skrivning. UI viser først nyt playback-state efter en læsning.

Tilladte ruter til denne delversion:

- GET `/v1/me/player/devices`, `/v1/me/player`, `/v1/me/playlists`, `/v1/me/tracks`, `/v1/search`.
- PUT `/v1/me/player/play`, `/pause`, `/volume`, `/shuffle`, `/repeat`.
- POST `/v1/me/player/next`, `/previous`.

Alle player-skrivninger kræver eksplicit `device_id` fra en frisk valideret
Connect-enhedsliste. Kommandoen beholder sit oprindelige id; ingen match på navn
eller fallback til den implicit aktive enhed. Afvis restricted, dublerede,
ugyldige og utilgængelige enheder. Konfigureret device-id er ikke selv et grant.

Fjernelse annullerer køer/timers, lukker jobs og forhindrer events til frigivet
Lua-state. HTTP-id'er/generationer skal også adskilles mellem nye plugininstanser.
Afbrudt skrivning kan have ukendt udfald; det giver ikke tilladelse til retry.

## OAuth

PKCE-login og refresh foregår kun i hosten med fysisk/ejerstyret opsætning.
Credentialprofilen `spotify` er bundet til `housenimble.spotify`, det præcise
origin, ovenstående ruter og de nødvendige scopes. Aliaset i Lua kan aldrig
bruge credentials til et andet plugin eller et andet origin. Pluginet anmoder
ikke om adgang til tokenendpointet og ser ingen rå tokens.

## Fremtidig direkte Sonos-port

Denne delversion bruger kun Spotify Connect. SSDP/topologi/SOAP kræver senere
afgrænsede, ejerautoriserede host-tjenester til lokal discovery og eksplicitte
rum/koordinatorer. Genbrug ikke rå sockets eller frit HTTP til vilkårlige LAN-adresser,
og læg ikke den private native Sonos-controller i det offentlige repo.
