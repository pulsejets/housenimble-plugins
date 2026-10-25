# Offentlig host-API · udkast 1

Kontrakten er offentlig; dens implementering ligger kun i housenimble-core.
Nuværende firmware implementerer ikke denne Lua-kontrakt. Pluginpakker består
af Lua-tekst og data, ikke native moduler eller en distribueret core-firmware.

| Område | Offentlig adgang | Privat ansvar i core |
| --- | --- | --- |
| `ctx.ui` | Side, tekst, knap, billed-id, graf og energiflow | Display, touch, renderer, handles og tråd |
| `ctx.config` | Egen ikke-hemmelig konfiguration | Validering, land/region, tastatur og lagring |
| `ctx.http` | Asynkront job-id og afgrænset JSON-resultat | Wi-Fi, DNS, TLS, kø, tidsfrister og credentials |
| `ctx.mqtt` | Godkendte topics, beskeder og evt. publicering | Forbindelse, broker-login og genforbindelse |
| `ctx.storage` | Eget navnerum og cache med kvote | NVS/SD, atomisk skrivning, stier og mount |
| `ctx.log` | Egen redigeret log med rategrænse | Ingen core-dumps, globale logs eller andre plugins |

Core har altid en minimal startside med Wi-Fi, netværksstatus, opsætning og
plugin-test. Det offentlige overview-plugin er valgfrit.

Lifecycle: `create`, `show`, `hide`, `event`, `destroy`. Netværk, opdagelse og
lange opgaver er asynkrone. Intet plugin må blokere. Core ejer objekter og
annullerer job/timere ved fjernelse; sene svar fra en ældre generation kasseres.

Første prøvepakke har maksimalt 256 KiB RAM, 100.000 instruktioner pr. callback,
4 KiB lager og 128 KiB udpakket indhold. Budgetter er foreslåede grænser og skal
måles på den rigtige chip. Core håndhæver også host-kalds egne tids-/størrelsesgrænser.
Native kode, `io`, `os`, `package`, `debug`, bytecode, filindlæsning og dynamiske
moduler eksponeres ikke. Lua-isolering beskytter ikke mod alle fejl i runtime/C-bindinger.

Manifestet kan kun anmode om tilladelser. Core giver dem ud fra en kontrolleret
politik. Credentials bindes til præcise origins, metoder/stier og plugin-id;
pluginet får aldrig en rå Wi-Fi-kode eller et frit bearer-token til vilkårlige mål.
Regioner skal godkendes hver for sig. Lokale netværksmål kræver særskilt grant.
Redirects og DNS/IP-skift kontrolleres. MQTT-publicering kræver eksplicit topic-grant.

Store moduler kræver kontrollerede host-funktioner: billed-/kortcache, medievisning,
OAuth, discovery og midlertidig Wi-Fi-provisionering. Det er grunde til en
trinvis portering; mapperne alene gør ikke nuværende C++-plugins isolerede.
