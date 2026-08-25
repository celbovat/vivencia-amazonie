# Nový rok v Amazonii

Jednostránková pozvánka na výpravu do vesnice Chico Curumim na řece Jordão
v brazilském Acre, 27. 12. 2026 až 8. 1. 2027.

Živě: https://celbovat.github.io/vivencia-amazonie/

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

## Co je kde

| soubor | k čemu |
|---|---|
| `build.py` | šablona stránky a slepení všeho dohromady |
| `content.py` | všechny texty, česky i anglicky, klíč po klíči |
| `app.js` | chování: jazyk, přílet a plavba, vesnice, přihláška, hudba |
| `styles.css` | vzhled |
| `scene_village.py` | vesnice jako SVG, včetně rozklikávacích míst |
| `ikony.py` | ikonky u zastávek cesty |
| `geo.py`, `geo.json` | mapová data, zjednodušená z Natural Earth |
| `assets/` | fotky, písma, kené pásy a zvuk, vložené jako base64 |
| `qr.py` | QR kódy v barvách značky, každý se po výrobě přečte zpátky |
| `test_prihlaska.py` | proklikání přihlášky, osm případů v obou jazycích |
| `cdp.py` | řízení prohlížeče přes DevTools protokol |
| `plakat.py` | rozdělaný A5 leták, práce na něm je pozastavená |

## Dvě věci, o kterých je dobré vědět

Některé soubory v `assets/` mají v názvu dvojtečku, například
`css-braid::before.txt`. Na macOS a v gitu to nevadí, na Windows se ale
takový soubor nedá vytvořit, takže tam repozitář nepůjde naklonovat celý.

`test_prihlaska.py` a `cdp.py` čekají Chrome v
`/Applications/Google Chrome.app`. Chrome 139 už nepodporuje `--dump-dom`,
proto se stránka řídí přes DevTools protokol a ne přes ten přepínač.
