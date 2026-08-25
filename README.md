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
| `../functions/api/prihlaska.js` | odeslání přihlášky přes Brevo |
| `scene_village.py` | vesnice jako SVG, včetně rozklikávacích míst |
| `ikony.py` | ikonky u zastávek cesty |
| `geo.py`, `geo.json` | mapová data, zjednodušená z Natural Earth |
| `assets/` | fotky, písma, kené pásy a zvuk, vložené jako base64 |
| `qr.py` | QR kódy v barvách značky, každý se po výrobě přečte zpátky |
| `test_prihlaska.py` | proklikání přihlášky, osm případů v obou jazycích |
| `cdp.py` | řízení prohlížeče přes DevTools protokol |
| `plakat.py` | rozdělaný A5 leták, práce na něm je pozastavená |

## Přihláška

Formulář neotevírá poštu, ale posílá se na `/api/prihlaska`. Tam ji Pages
Function předá Brevu, stejně jako to dělá `pobyt.curadafloresta.org`.
Kontakt se nikam neukládá, jde jen o jednu zprávu s obsahem formuláře.
Odpověď míří rovnou přihlášenému, jeho adresa jde jako `replyTo`.

Chce to jednu proměnnou v nastavení Pages projektu:

```bash
npx wrangler pages secret put BREVO_API_KEY --project-name vivencia-amazonie
```

Odesílatel `hello@curadafloresta.org` musí zůstat v Brevu mezi ověřenými
adresami, jinak Brevo zprávu odmítne a nic neodejde.

**Dokud klíč není nastavený, funkce vrátí `{ configured: false }`** a stránka
se tiše vrátí k tomu, co dělala dřív: otevře návštěvníkovi poštu s vyplněnou
přihláškou. Formulář tedy nikdy neskončí slepě, jen se přihláška nedoručí
sama. Při skutečném výpadku se pošta otevře taky, ale s vysvětlující hláškou.

Ve formuláři je skryté pole `firma` jako past na roboty. Když ho něco vyplní,
funkce odpoví `ok`, ale žádný e-mail neodejde.

Funkci jde vyzkoušet lokálně, i s celou stránkou:

```bash
cd zdroje && python3 build.py && cp vivencia.html ../index.html && cd ..
mkdir -p dist && cp index.html nahled.jpg dist/
npx wrangler pages dev dist --binding BREVO_API_KEY=klic
```

Složka `functions/` zůstává v kořeni, i když se nahrává `dist/` – wrangler ji
hledá vedle nahrávané složky, ne uvnitř. Že se povedla, pozná se ve výpisu
podle řádky `Uploading Functions bundle`.

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
| `prihlaska_odeslana` | `vysledek` je ok / posta / chyba / whatsapp |

Přihláška se měří přímo v `app.js`, kde je vidět, jak dopadla, takže
`vysledek` odliší doručenou přihlášku od té, co spadla do pošty. Stejné
hodnoty jako na `pobyt`, aby šly obě domény porovnat v jednom grafu.
Plavba se neměří vůbec, když se nepustí (vracející se návštěvník, `?rovnou`,
odkaz s kotvou), aby to nevypadalo, že ji všichni přeskakují.

Do adresy jde přidat `?od=neco` a v datech je pak vidět, odkud kdo přišel –
třeba `?od=letak` na QR kódech z `qr.py`.

## Dvě věci, o kterých je dobré vědět

Některé soubory v `assets/` mají v názvu dvojtečku, například
`css-braid::before.txt`. Na macOS a v gitu to nevadí, na Windows se ale
takový soubor nedá vytvořit, takže tam repozitář nepůjde naklonovat celý.

`test_prihlaska.py` a `cdp.py` čekají Chrome v
`/Applications/Google Chrome.app`. Chrome 139 už nepodporuje `--dump-dom`,
proto se stránka řídí přes DevTools protokol a ne přes ten přepínač.
