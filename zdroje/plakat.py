# -*- coding: utf-8 -*-
"""Letak na festival, A5 na 300 dpi, anglicky.

Sazi se v HTML a renderuje headless Chromem, protoze konektor do Canvy
neumi menit pismo. Vystup je PNG na nahled a PDF do tiskarny.

Pozor: headless Chrome nedava viewport takovy, jaky se mu zada, a zbytek
dorenderuje bile. Proto se renderuje s rezervou, orizne a na zaver se
kontroluje, ze krajni radek ani sloupec nejsou bile.
"""

import base64
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
A = HERE / "assets"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# A5 na 300 dpi
W, H = 1748, 2480

CREAM = "#FFF2D9"
YELLOW = "#F8BC4C"
ORANGE = "#ED6E2C"
TEAL = "#528E82"
GREEN = "#1F3C36"
GREEN_DEEP = "#162C28"


def b64(cesta):
    return base64.b64encode(pathlib.Path(cesta).read_bytes()).decode()


def qr(text):
    sys.path.insert(0, str(HERE / "vendor"))
    import segno
    kod = segno.make(text, error="q")          # vyssi korekce, letak se pomackа
    cil = HERE / "assets" / "qr.png"
    kod.save(str(cil), scale=20, border=2, dark=GREEN, light=None)
    return b64(cil), kod.version


ODKAZ = "https://curadafloresta.org"
QR_B64, QR_VER = qr(ODKAZ)

FONT_EXT = (A / "font0-HankenGrotesk.txt").read_text().strip()
FONT_LAT = (A / "font1-HankenGrotesk.txt").read_text().strip()
ZNAK = (A / "img-hero__badge.txt").read_text().strip()
PAS = (A / "css-braid::before.txt").read_text().strip()
FOTO = (A / "foto" / "plakat.txt").read_text().strip()

HTML = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<style>
@font-face {{
  font-family:"Hanken Grotesk"; font-style:normal; font-weight:400 700;
  src:url(data:font/woff2;base64,{FONT_EXT}) format("woff2");
  unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,
    U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,
    U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF;
}}
@font-face {{
  font-family:"Hanken Grotesk"; font-style:normal; font-weight:400 700;
  src:url(data:font/woff2;base64,{FONT_LAT}) format("woff2");
  unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,
    U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,
    U+2212,U+2215,U+FEFF,U+FFFD;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:{W}px; height:{H}px; }}
body {{
  font-family:"Hanken Grotesk",sans-serif; background:{GREEN};
  color:{CREAM}; -webkit-font-smoothing:antialiased;
  display:flex; flex-direction:column;
}}

/* ---------- horni pole s fotkou ---------- */
.vrch {{ position:relative; height:1476px; overflow:hidden; flex:none; }}
.vrch__foto {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
.vrch::after {{
  content:""; position:absolute; inset:0;
  background:linear-gradient(to bottom,
    rgba(22,44,40,.90) 0%, rgba(22,44,40,.52) 42%, rgba(22,44,40,.95) 100%);
}}
.vrch__obsah {{ position:relative; z-index:2; padding:96px 104px 0; }}
.znak {{ width:196px; height:auto; display:block; }}
.eyebrow {{
  margin-top:74px; font-size:29px; font-weight:700;
  letter-spacing:.30em; text-transform:uppercase; color:{ORANGE};
}}
h1 {{
  margin-top:26px; font-size:132px; line-height:.96; font-weight:700;
  letter-spacing:-.03em; color:{CREAM};
}}
h1 em {{ font-style:normal; color:{YELLOW}; }}
.podnadpis {{
  margin-top:44px; font-size:44px; line-height:1.32; color:{CREAM};
  max-width:20em; font-weight:400;
}}
.termin {{
  margin-top:56px; display:inline-block;
  padding:20px 40px; border:5px solid {ORANGE}; border-radius:999px;
  font-size:44px; font-weight:700; letter-spacing:.02em; color:{YELLOW};
}}

/* ---------- kene predel ---------- */
.pas {{
  height:96px; flex:none; background:{GREEN};
  background-image:url(data:image/png;base64,{PAS});
  background-repeat:repeat-x; background-position:center;
  background-size:auto 62%;
}}

/* ---------- spodni pole ---------- */
.spodek {{
  flex:1; background:{CREAM}; color:{GREEN};
  padding:64px 104px 76px; display:flex; flex-direction:column;
}}
.fakta {{ display:flex; gap:64px; }}
.fakt__stitek {{
  font-size:24px; font-weight:700; letter-spacing:.22em;
  text-transform:uppercase; color:#B8501A; margin-bottom:10px;
}}
.fakt__hodnota {{ font-size:38px; font-weight:700; line-height:1.2; }}
.cara {{ height:5px; background:rgba(31,60,54,.18); margin:52px 0 46px; }}
.body {{ display:grid; grid-template-columns:1fr 1fr; gap:26px 54px; }}
.bod {{ position:relative; padding-left:46px; font-size:34px; line-height:1.34; }}
.bod::before {{
  content:""; position:absolute; left:0; top:.42em; width:24px; height:24px;
  background:{TEAL}; clip-path:polygon(50% 0,100% 50%,50% 100%,0 50%);
}}
.pata {{ margin-top:auto; display:flex; align-items:center; gap:52px; }}
.qr {{ width:270px; height:270px; flex:none; }}
.pata__text {{ flex:1; }}
.pata__vyzva {{ font-size:36px; font-weight:700; line-height:1.28; }}
.pata__kontakt {{
  margin-top:18px; font-size:31px; line-height:1.5; color:#5C4A22;
}}
.pata__kontakt b {{ color:{GREEN}; }}
</style></head><body>

<div class="vrch">
  <img class="vrch__foto" src="data:image/jpeg;base64,{FOTO}" alt="">
  <div class="vrch__obsah">
    <img class="znak" src="data:image/png;base64,{ZNAK}" alt="Cura da Floresta">
    <p class="eyebrow">Cura da Floresta invites you</p>
    <h1>Celebrate<br>the New Year<br><em>in the Amazon</em></h1>
    <p class="podnadpis">Twelve days with the Huni Kuin in the village
      of Chico Curumim, deep in the Brazilian rainforest.</p>
    <p class="termin">27 December 2026 &ndash; 8 January 2027</p>
  </div>
</div>

<div class="pas"></div>

<div class="spodek">
  <div class="fakta">
    <div>
      <p class="fakt__stitek">Where</p>
      <p class="fakt__hodnota">Jord&atilde;o river<br>Acre, Brazil</p>
    </div>
    <div>
      <p class="fakt__stitek">Price</p>
      <p class="fakt__hodnota">3 200 &euro;<br>without flights</p>
    </div>
    <div>
      <p class="fakt__stitek">Group</p>
      <p class="fakt__hodnota">eight people<br>no more</p>
    </div>
  </div>

  <div class="cara"></div>

  <div class="body">
    <p class="bod">Nine days living in the village</p>
    <p class="bod">Ceremonies, songs and the fire</p>
    <p class="bod">Herbal baths and Mapu clay</p>
    <p class="bod">Sacred ken&eacute; body painting</p>
    <p class="bod">The river, the forest, the fishing</p>
    <p class="bod">Karol&iacute;na and Tereza guide you</p>
  </div>

  <div class="pata">
    <img class="qr" src="data:image/png;base64,{QR_B64}" alt="">
    <div class="pata__text">
      <p class="pata__vyzva">Scan for the whole story,<br>or just write to us.</p>
      <p class="pata__kontakt">
        <b>curadafloresta.org</b><br>
        hello@curadafloresta.org &nbsp;&middot;&nbsp; @curadafloresta_org
      </p>
    </div>
  </div>
</div>

</body></html>
"""


def render():
    (HERE / "plakat.html").write_text(HTML, encoding="utf-8")
    # s rezervou, protoze headless nedava presne zadanou vysku
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                    f"--screenshot={HERE / 'plakat_raw.png'}",
                    f"--window-size={W},{H + 400}",
                    "--virtual-time-budget=6000",
                    f"file://{HERE / 'plakat.html'}"],
                   capture_output=True)
    from PIL import Image
    im = Image.open(HERE / "plakat_raw.png").convert("RGB").crop((0, 0, W, H))
    im.save(HERE / "plakat-a5.png")

    # kontrola, ze se nedorenderoval bily pruh
    px = im.load()
    def bily(b): return all(k > 244 for k in b)
    spodni = [px[x, H - 1] for x in range(0, W, 40)]
    pravy = [px[W - 1, y] for y in range(0, H, 40)]
    assert not all(bily(b) for b in spodni), "spodní řádek je bílý, render se usekl"
    assert not all(bily(b) for b in pravy), "pravý sloupec je bílý, render se usekl"

    # PDF do tiskarny
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={HERE / 'plakat-a5.pdf'}",
                    "--virtual-time-budget=6000",
                    f"file://{HERE / 'plakat.html'}"], capture_output=True)
    print("plakát:", im.size, "| QR verze", QR_VER, "->", ODKAZ)


if __name__ == "__main__":
    render()
