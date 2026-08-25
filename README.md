# Nový rok v Amazonii

Jednostránková pozvánka na výpravu do vesnice Chico Curumim na řece Jordão
v brazilském Acre, 27. 12. 2026 až 8. 1. 2027.

Živě: https://journey.curadafloresta.org/ (Cloudflare Pages, nasazuje se samo z main)

`index.html` je celá stránka v jednom souboru. Písma, fotky, zvuk i mapová
data jsou v něm vložené přímo, takže si stránka při načtení nesahá nikam ven.
Proto má skoro 3 MB, a proto funguje i bez připojení.

## Jak ji znovu postavit

```bash
cd zdroje
python3 build.py          # vyrobí vivencia.html
python3 pocet.py          # kontrola, že se v CSS nic neusekalo
cp vivencia.html ../index.html
```

`pocet.py` porovná, kolik pravidel v CSS napočítá prohlížeč a kolik jich je
v souboru. Když čísla nesedí, někde je rozbitý selektor a zbytek stylopisu
prohlížeč zahodil. Jednou se to už stalo a stránka kvůli tomu vyrostla o 3 700
pixelů, než se na to přišlo.

## Jak se to nasazuje

Každý push do `main` spustí `.github/workflows/nasazeni.yml`. Ten sestaví
stránku ze `zdroje/`, a když se výsledek liší od commitnutého `index.html`,
commitne ho zpátky – takže zdroje a nasazená stránka se nikdy nerozejdou.
Pak výsledek pošle na Cloudflare Pages (projekt `vivencia-amazonie`).

Build v CI je čistý stdlib Python, žádné závislosti se neinstalují. `pocet.py`
v CI neběží, protože potřebuje Chrome – ten je pořád na tobě, lokálně.

Workflow potřebuje dva secrets v repozitáři:

| secret | co to je |
|---|---|
| `CLOUDFLARE_API_TOKEN` | token s oprávněním *Cloudflare Pages: Edit* |
| `CLOUDFLARE_ACCOUNT_ID` | ID účtu, kde je zóna `curadafloresta.org` |

## Co je kde

| soubor | k čemu |
|---|---|
| `build.py` | šablona stránky a slepení všeho dohromady |
| `content.py` | všechny texty, česky i anglicky, klíč po klíči |
| `app.js` | chování: jazyk, přílet a plavba, vesnice, přihláška, hudba |
| `styles.css` | vzhled |
| `mereni.js` | PostHog: návštěvnost a trychtýř přihlášky |
| `scene_village.py` | vesnice jako SVG, včetně rozklikávacích míst |
| `ikony.py` | ikonky u zastávek cesty |
| `geo.py`, `geo.json` | mapová data, zjednodušená z Natural Earth |
| `assets/` | fotky, písma, kené pásy a zvuk, vložené jako base64 |
| `qr.py` | QR kódy v barvách značky, každý se po výrobě přečte zpátky |
| `test_prihlaska.py` | proklikání přihlášky, osm případů v obou jazycích |
| `cdp.py` | řízení prohlížeče přes DevTools protokol |
| `plakat.py` | rozdělaný A5 leták, práce na něm je pozastavená |

## Měření

`mereni.js` posílá návštěvnost do PostHogu, do projektu *Cura da Floresta web*
(id 203731) společně s `cesta.` a `pobyt.curadafloresta.org` – rozliší se
doménou. Je to jediné místo, kde si stránka sahá ven; když se knihovna
nestáhne, stránka funguje dál, jen se nic nezměří.

Bez cookies a tedy i bez lišty se souhlasem: `cookieless_mode: 'always'`
a `persistence: 'memory'`. Pozor na `defaults` – bez něj knihovna
`cookieless_mode` potichu ignoruje a cookies zase nasadí. Z `pages.dev`
a z localhostu se neměří nic.

| událost | kdy |
|---|---|
| `$pageview` | načtení stránky |
| `plavba_dokoncena` | někdo doplul až do vesnice |
| `plavba_preskocena` | přeskočil, `jak` rozliší tlačítko a klávesu |
| `chci_jet` | kliknutí na přihlašovací CTA, `misto` je hlavička/lišta |
| `hra_otevrena` | odchod na cesta.curadafloresta.org/hra |
| `jazyk_prepnut` | přepnutí CS/EN |
| `prihlaska_odeslana` | odeslaná přihláška, `kanal` je mail/whatsapp |

Přihláška se měří až na odkrytí poděkování, ne na kliknutí – kliknout jde
i na formulář, který neprojde kontrolou. Plavba se neměří vůbec, když se
nepustí (vracející se návštěvník, `?rovnou`, odkaz s kotvou), aby to
nevypadalo, že ji všichni přeskakují.

Do adresy jde přidat `?od=neco` a v datech je pak vidět, odkud kdo přišel –
třeba `?od=letak` na QR kódech z `qr.py`.

## Dvě věci, o kterých je dobré vědět

Některé soubory v `assets/` mají v názvu dvojtečku, například
`css-braid::before.txt`. Na macOS a v gitu to nevadí, na Windows se ale
takový soubor nedá vytvořit, takže tam repozitář nepůjde naklonovat celý.

`test_prihlaska.py` a `cdp.py` čekají Chrome v
`/Applications/Google Chrome.app`. Chrome 139 už nepodporuje `--dump-dom`,
proto se stránka řídí přes DevTools protokol a ne přes ten přepínač.
