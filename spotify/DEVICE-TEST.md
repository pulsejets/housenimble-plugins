# Enhedstest · Spotify og Sonos

Status 2026-10-26: Lua-prototype testet offline; **ikke kørt på en fysisk enhed**.
Ingen Spotify-login, lydstyrkeændring eller afspilning er udført mod rigtige konti.
Den installerede dev-core mangler nødvendige HTTP/OAuth/tick/config-bindinger.
En gyldig ZIP betyder ikke, at pakken kan indlæses eller køre på denne core.

## Før fysisk test

1. Få konkret ejeraccept til netop enhedstesten og eventuel nødvendig core-upload.
2. Bekræft privat provisioneret core med den præcise [host-kontrakt](HOST-CONTRACT.md),
   Spotify credentialprofil/scopes og konfigurationsvalidering. Ingen core-kilde deles.
3. Kør de isolerede Lua-tests og check/pack. Registrér præcis plugin-SHA og
   kompatibel core-API/version i et redigeret testnotat, aldrig credentials.
4. Brug den faktisk implementerede USB-klient fra SDK-feature-branchen. Dens
   nuværende begrænsning til ingen netværksgrants må **ikke** omgås.
5. Par fysisk med en frisk kode; indlæs kun `spotify`. Bevar core/Wi-Fi.

## Manuel kontrol med testhøjttaler

- Uden login: forståelig fejl og ingen syntetisk sang. Vælg aldrig en højttaler automatisk efter navn.
- Find Connect-enheder; vælg en præcis testhøjttaler. Opstart/valg må ikke starte musik eller gruppere rum.
- Se faktisk titel/kunstner og korrekt højttaler. En anden aktiv enhed må ikke få sin metadata vist som den valgte.
- Test eksplicit Play/Pause/Next/Previous, hurtige gentagne Next og bounded kø.
- Test kendt lydstyrke, ukendt/null lydstyrke, øvre/nedre grænse, shuffle og repeat.
- Se første bibliotekside og afspil en eksplicit valgt URI. Tøm/ødelæg svar i host-fixture, ikke i rigtige konti.
- Fjern/restrict/manglende mål: ingen kommando. Timeout efter skrivning: ingen automatisk gentagelse.
- 429: behold hele Retry-After, også ved skjul/genindlæsning. Ingen genafspilning af tidligere knaptryk.
- Skjul/stop/genindlæs: gamle svar ignoreres, ressourcer frigives, core og Wi-Fi fortsætter.
- Notér fysiske resultater og resterende mangler. Markér ikke Sonos-grupper, covers,
  favorit-skrivninger eller fuld SpotifyESP-paritet som testet; de er ikke porteret.

Følg også [fælles testprocedure](../_sdk/DEVICE-TEST.md). Lokal test bruger kun
mock-host og kræver ingen privat core eller ændring i den oprindelige SpotifyESP-mappe.
