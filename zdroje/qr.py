# -*- coding: utf-8 -*-
"""QR kod na stranku vypravy, v barvach Cura da Floresta.

Korekce chyb H (30 %), aby kod snesl znak uprostred i pomackany papir.
Kazdy vyrobeny soubor se na zaver opravdu precte, ne jen vyrobi.
"""
import base64
import io
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent / "vendor"))
import segno
from PIL import Image

HERE = pathlib.Path(__file__).parent
CIL = pathlib.Path.home() / "Downloads/vivencia-prosinec-2026/qr"
CIL.mkdir(parents=True, exist_ok=True)

import sys as _s
ODKAZ = _s.argv[1] if len(_s.argv) > 1 else "https://journey.curadafloresta.org/"
PREDPONA = _s.argv[2] if len(_s.argv) > 2 else "qr-journey"

GREEN = "#1F3C36"
CREAM = "#FFF2D9"
HRANA = 2400            # 300 dpi na 20 cm, na letak i na plakat dost

kod = segno.make(ODKAZ, error="h")
print("odkaz:", ODKAZ)
print("verze QR: %s, korekce H, modulů %d" % (kod.version, kod.symbol_size(border=0)[0]))


def uloz_png(jmeno, pozadi):
    b = io.BytesIO()
    moduly = kod.symbol_size(border=4)[0]
    kod.save(b, kind="png", scale=max(1, HRANA // moduly), border=4,
             dark=GREEN, light=pozadi)
    im = Image.open(io.BytesIO(b.getvalue())).convert("RGBA")
    cesta = CIL / jmeno
    im.save(cesta)
    return cesta, im


def se_znakem(zaklad_im, jmeno):
    im = zaklad_im.copy()
    W = im.size[0]
    znak = Image.open(io.BytesIO(base64.b64decode(
        (HERE / "assets" / "img-hero__badge.txt").read_text()))).convert("RGBA")
    # znak sedi na kremovem kotouci, at se neslije s moduly
    prumer = int(W * 0.20)
    kotouc = Image.new("RGBA", (prumer, prumer), (0, 0, 0, 0))
    from PIL import ImageDraw
    ImageDraw.Draw(kotouc).ellipse((0, 0, prumer - 1, prumer - 1),
                                   fill=(255, 242, 217, 255))
    z = znak.resize((int(prumer * 0.78), int(prumer * 0.78)), Image.LANCZOS)
    kotouc.alpha_composite(z, ((prumer - z.size[0]) // 2, (prumer - z.size[1]) // 2))
    im.alpha_composite(kotouc, ((W - prumer) // 2, (W - prumer) // 2))
    cesta = CIL / jmeno
    im.save(cesta)
    return cesta


def precti(cesta):
    r = subprocess.run(["swift", str(pathlib.Path.home() / ".claude/tools/precti-qr.swift"),
                        str(cesta)], capture_output=True, text=True)
    return r.stdout.strip()


hotovo = []
c1, im1 = uloz_png(PREDPONA + ".png", CREAM)
hotovo.append(c1)
c2, im2 = uloz_png(PREDPONA + "-pruhledny.png", None)
hotovo.append(c2)
hotovo.append(se_znakem(im1, PREDPONA + "-se-znakem.png"))

# vektor do tiskarny
svg = CIL / (PREDPONA + ".svg")
kod.save(str(svg), scale=10, border=4, dark=GREEN, light=CREAM)
print("SVG:", svg.name, svg.stat().st_size, "B")

print()
for c in hotovo:
    text = precti(c)
    stav = "ČTE SE SPRÁVNĚ" if text == ODKAZ else ("PŘEČTENO JINAK: %r" % text if text else "NEPŘEČTENO")
    print("%-30s %8d kB   %s" % (c.name, c.stat().st_size // 1024, stav))
