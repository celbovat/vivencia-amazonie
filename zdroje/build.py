# -*- coding: utf-8 -*-
"""Sestavi vivencia.html: fonty a obrazky inline, scena z scene_village.py,
texty z content.py. Vystup je jeden samostatny soubor bez externich zdroju
(CSP v artifactu blokuje cizi hosty)."""

import base64
import hashlib
import importlib.util
import json
import pathlib
import struct

HERE = pathlib.Path(__file__).parent
A = HERE / "assets"

# Velke assety uz nejdou do HTML jako data URI, ale vedle nej jako soubory.
# Duvod: zvuk delal 40 % stranky a stahoval si ho i ten, kdo ho nikdy nepustil,
# a `loading="lazy"` u fotek nedelalo nic, protoze na data URI neplati.
# Slozka se generuje pri buildu, v gitu neni - zdrojem zustavaji assets/.
MEDIA = HERE.parent / "media"

# Slozka se cisti jednou na zacatku, at se v ni nehromadi assety z minulych
# buildu (jmena nesou otisk, takze by kazda zmena nechala lezet starou verzi).
if MEDIA.exists():
    for _stary in MEDIA.iterdir():
        _stary.unlink()
else:
    MEDIA.mkdir(parents=True)


def rozmer(data):
    """Sirka a vyska z hlavicky PNG nebo JPEG. Bez rozmeru v HTML skace layout,
    az se obrazek dotahne. Jen stdlib, aby build nepotreboval Pillow."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            znacka = data[i + 1]
            # SOF0..SOF15 nesou rozmer; SOF4 a SOF12 jsou jine tabulky
            if znacka in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                          0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                v, s = struct.unpack(">HH", data[i + 5:i + 9])
                return s, v
            if znacka in (0xD8, 0x01) or 0xD0 <= znacka <= 0xD7:
                i += 2
                continue
            i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    return None


def atr_rozmer(rm):
    return ' width="%d" height="%d"' % rm if rm else ""


def uloz(jmeno, data):
    """Zapise asset vedle stranky a vrati cestu, kterou ma dat do HTML.

    Do jmena se vklada otisk obsahu. Diky nemu jde na media/ pustit rok dlouhou
    cache s `immutable` a pritom se zmenena fotka projevi hned - dostane jine
    jmeno. Bez otisku by se muselo vybirat mezi cachovanim a aktualnosti."""
    zaklad, _, pripona = jmeno.rpartition(".")
    otisk = hashlib.sha256(data).hexdigest()[:8]
    cele = "%s.%s.%s" % (zaklad, otisk, pripona)
    (MEDIA / cele).write_bytes(data)
    return "media/" + cele


def bin_asset(cesta_txt, jmeno):
    """Asset do media/. Bere original, kdyz je po ruce, jinak dekoduje base64."""
    original = A / cesta_txt.replace(".txt", jmeno[jmeno.rfind("."):])
    data = (original.read_bytes() if original.exists()
            else base64.b64decode((A / cesta_txt).read_text().strip()))
    return uloz(jmeno, data), rozmer(data)


def modul(jmeno, soubor):
    spec = importlib.util.spec_from_file_location(jmeno, HERE / soubor)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


C = modul("content", "content.py")
SV = modul("scene_village", "scene_village.py")
CS, EN = C.CS, C.EN


def b64(jmeno):
    return (A / jmeno).read_text().strip()


def foto(klic, alt_klic, cls="foto", hned=False):
    """Obrazek vedle stranky, ne v ni. alt se prepina s jazykem.

    Rozmery jdou do HTML, aby se layout nehnul, az se obrazek dotahne.
    `hned=True` je pro to, co je videt bez scrollovani; zbytek je liny."""
    cesta, rm = bin_asset("foto/%s.txt" % klic, "%s.jpg" % klic)
    velikost = ' width="%d" height="%d"' % rm if rm else ""
    nacitani = ('decoding="async" fetchpriority="high"' if hned
                else 'loading="lazy" decoding="async"')
    return ('<img class="%s" %s src="%s"%s data-i18n="%s" data-i18n-attr="alt" '
            'alt="%s" />' % (cls, nacitani, cesta, velikost, alt_klic, CS[alt_klic]))


FONT_EXT = b64("font0-HankenGrotesk.txt")
FONT_LAT = b64("font1-HankenGrotesk.txt")
IMG_ZNAK, RM_ZNAK = bin_asset("img-hero__badge.txt", "znak.png")
IMG_DIAMANT = b64("img-hero__diamond.txt")
IMG_JACARE, RM_JACARE = bin_asset("img-practical__jacare.txt", "jacare.png")
IMG_HAD, RM_HAD = bin_asset("img-snake.txt", "had.png")
HLAS = uloz("hlas.m4a", (A / "zvuk" / "hlas.m4a").read_bytes())
HERO_FOTO, RM_HERO = bin_asset("foto/hero.txt", "hero.jpg")
CITAT_FOTO, RM_CITAT = bin_asset("foto/citat.txt", "citat.jpg")
ZAVER_FOTO, RM_ZAVER = bin_asset("foto/zaver.txt", "zaver.jpg")
PAS_COP = b64("css-braid::before.txt")
PAS_LAB = b64("css-braid--lab::before.txt")
LINKA = b64("css-hero__rule.txt")
IKONA = b64("img-favicon.txt")

MAIL = "hello@curadafloresta.org"
WA = "420734490078"

# Adresa stranky. Pri prechodu na vlastni domenu se meni JEN tady.
ADRESA = "https://journey.curadafloresta.org/"
HRA = "https://cesta.curadafloresta.org/hra/"
HRA_EN = "https://cesta.curadafloresta.org/en/hra/"


# --------------------------------------------------------------- pomocnici
def txt(klic, tag="span", cls="", html=False, **atr):
    """Element s textem v cestine a data-i18n klicem pro prepnuti."""
    obsah = CS.get(klic, "")
    a = ' class="%s"' % cls if cls else ""
    for k, v in atr.items():
        a += ' %s="%s"' % (k.replace("_", "-"), v)
    h = " data-i18n-html" if html else ""
    return '<%s%s data-i18n="%s"%s>%s</%s>' % (tag, a, klic, h, obsah, tag)


# Znacka Instagramu k ohlasu. Plna plocha s evenodd jako ostatni ikony:
# ramecek, krouzek objektivu a tecka jsou dohromady jedna cesta.
IKONA_IG = (
    '<svg class="ohlas__ig" viewBox="0 0 24 24" fill="currentColor" '
    'aria-hidden="true" focusable="false"><path fill-rule="evenodd" d="'
    'M8 2.5H16A5.5 5.5 0 0 1 21.5 8V16A5.5 5.5 0 0 1 16 21.5H8'
    'A5.5 5.5 0 0 1 2.5 16V8A5.5 5.5 0 0 1 8 2.5Z'
    'M8.3 4.4H15.7A3.9 3.9 0 0 1 19.6 8.3V15.7A3.9 3.9 0 0 1 15.7 19.6H8.3'
    'A3.9 3.9 0 0 1 4.4 15.7V8.3A3.9 3.9 0 0 1 8.3 4.4Z'
    'M7.6 12A4.4 4.4 0 1 0 16.4 12A4.4 4.4 0 1 0 7.6 12Z'
    'M9.4 12A2.6 2.6 0 1 0 14.6 12A2.6 2.6 0 1 0 9.4 12Z'
    'M15.85 7A1.15 1.15 0 1 0 18.15 7A1.15 1.15 0 1 0 15.85 7Z'
    '"/></svg>'
)


IK = modul("ikony", "ikony.py").IKONY


def ikona(jmeno):
    """evenodd je nutne: okna domu jsou podcesty, ktere se maji vykousnout."""
    return ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" '
            'focusable="false"><path fill-rule="evenodd" d="%s"/></svg>' % IK[jmeno])


# kazda zastavka ma vlastni ikonu; dohromady je to sestup z velkomesta
# pres mensi mesto a mestecko k ricnimu pristavu a nakonec do vesnice
ZASTAVKY = [
    ("praha", "vzlet", "letadlo"),
    ("saopaulo", "velkomesto", "letadlo"),
    ("riobranco", "mesto", "auto"),
    ("taruaca", "mestecko", "mini"),
    ("jordao", "pristav", "lod"),
    ("vesnice", "kupixawa", None),
]


def trasa():
    kusy = []
    for i, (klic, ik, spoj) in enumerate(ZASTAVKY):
        kusy.append(
            '<button type="button" class="zastavka" data-skupina="cesta" '
            'data-cil="%s" aria-pressed="false">'
            '<span class="zastavka__krouzek">%s</span>'
            '%s%s</button>' % (
                klic, ikona(ik),
                txt("cesta.%s.jmeno" % klic, "span", "zastavka__jmeno"),
                txt("cesta.%s.pod" % klic, "span", "zastavka__pod")))
        if spoj:
            kusy.append(
                '<span class="spojka" aria-hidden="true">'
                '<span class="spojka__cara"></span>%s</span>'
                % txt("cesta.%s.spoj" % ZASTAVKY[i][0], "span", "spojka__jak"))
    return "\n        ".join(kusy)


def karty_cesta():
    return "\n        ".join(
        '<div class="polozka" data-klic="%s" hidden>%s%s</div>' % (
            klic,
            txt("cesta.%s.h" % klic, "h3"),
            txt("cesta.%s.p" % klic, "p", html=True))
        for klic, _, _ in ZASTAVKY)


def body_vesnice():
    rows = []
    for klic, x, y in SV.HOTSPOTS:
        rows.append(
            '<button type="button" class="bod" data-skupina="vesnice" '
            'data-cil="%s" aria-pressed="false" style="left:%.1f%%;top:%.1f%%" '
            'data-i18n="scena.%s.bod" data-i18n-attr="aria-label" '
            'aria-label="%s"><span></span></button>'
            % (klic, x / SV.W * 100, y / SV.H * 100, klic,
               CS["scena.%s.bod" % klic]))
    return "\n          ".join(rows)


def chipy_vesnice():
    return "\n        ".join(
        '<button type="button" class="chip" data-skupina="vesnice" '
        'data-cil="%s" aria-pressed="false" data-i18n="scena.%s.chip">%s</button>'
        % (k, k, CS["scena.%s.chip" % k]) for k, _, _ in SV.HOTSPOTS)


KARTA_FOTO = {"reka", "samauma", "kupixawa", "ohen", "lazen", "kene", "tance", "hamaka"}
# Hospedaria je dum na vysku, do sirokeho formatu ostatnich karticek se nevejde.
KARTA_FOTO_VYSKA = {"hamaka"}


def karty_vesnice():
    kusy = []
    for klic, _, _ in SV.HOTSPOTS:
        hlava = txt("scena.%s.h" % klic, "h3")
        obraz = ""
        if klic in KARTA_FOTO:
            tvar = ("polozka__foto polozka__foto--vysoka"
                    if klic in KARTA_FOTO_VYSKA else "polozka__foto")
            obraz = foto(klic, "scena.%s.h" % klic, tvar)
        text = txt("scena.%s.p" % klic, "p", html=True)
        if ("scena.%s.p2" % klic) in CS:
            text += txt("scena.%s.p2" % klic, "p", html=True)
        if klic in KARTA_FOTO_VYSKA:
            # fotka na vysku je uzka, text jde vedle ni, at karta nezeje prazdnotou
            telo = hlava + ('<div class="polozka__radek">%s'
                            '<div class="polozka__text">%s</div></div>' % (obraz, text))
        else:
            telo = hlava + obraz + text
        kusy.append('<div class="polozka" data-klic="%s" hidden>%s</div>' % (klic, telo))
    return "\n        ".join(kusy)


PROGRAM = ["d5", "d67", "d8", "d9", "d10", "d11", "d12", "d13"]


def program():
    return "\n        ".join(
        '<div class="proud__den">%s%s</div>' % (
            txt("program.%s.t" % d, "p", "proud__kdy"),
            txt("program.%s" % d, "p", "proud__co"))
        for d in PROGRAM)


LIDE = ["tamani", "shane", "yube", "paje"]


def lide():
    return "\n        ".join(
        '<div class="clovek">%s<div class="clovek__text">%s%s%s</div></div>' % (
            foto(k, "lide.%s.jmeno" % k, "clovek__foto"),
            txt("lide.%s.jmeno" % k, "h3"),
            txt("lide.%s.role" % k, "p", "clovek__role"),
            txt("lide.%s.p" % k, "p"))
        for k in LIDE)


HRY = [
    ("kviz", "🐾", "", "", True),
    ("lod", "🛶", "lod.html", "lod.html", False),
    ("batoh", "🎒", "batoh.html", "batoh.html", False),
    ("tapir", "🐽", "tapir.html", "tapir.html", False),
    ("lov", "🎯", "lov.html", "lov.html", False),
]


def hry():
    kusy = []
    for klic, ik, cesta_cs, cesta_en, velka in HRY:
        cls = "hra hra--velka" if velka else "hra"
        kusy.append(
            '<a class="%s" href="%s" data-hra-cs="%s" data-hra-en="%s" '
            'target="_blank" rel="noopener">'
            '<span class="hra__ikona" aria-hidden="true">%s</span><span>%s%s</span></a>'
            % (cls, HRA + cesta_cs, HRA + cesta_cs, HRA_EN + cesta_en, ik,
               txt("hry.%s.h" % klic, "h3"),
               txt("hry.%s.p" % klic, "p")))
    return "\n        ".join(kusy)


# Na strance zustavaji jen otazky, ktere brani prihlasce. Zbytek jde do PDF.
FAQ_NA_STRANCE = [1, 2, 3, 5]


def otazky():
    return "\n        ".join(
        '<details class="otazka">%s%s</details>' % (
            txt("faq.%d.q" % i, "summary"),
            txt("faq.%d.a" % i, "p"))
        for i in FAQ_NA_STRANCE)


def pruvodkyne():
    """Pruvodkyne sedi ve stejne mrizce jako lide z vesnice, aby to byl
    jeden blok Kdo tam bude, ne dve sekce za sebou."""
    kusy = []
    for k, jm, role in (("karolina", "pruvodci.karolina.jmeno", "pruvodci.karolina.role"),
                        ("tereza", "pruvodci.tereza.jmeno", "pruvodci.tereza.role")):
        kusy.append(
            '<div class="clovek clovek--pruvodce">%s<div class="clovek__text">%s%s%s</div></div>'
            % (foto(k, jm, "clovek__foto"),
               txt(jm, "h3"),
               txt(role, "p", "clovek__role"),
               txt("pruvodci.%s.p" % k, "p", html=True)))
    return "\n        ".join(kusy)


def seznam(prefix, pocet, cls=""):
    return "\n          ".join(
        txt("%s.%d" % (prefix, i), "li") for i in range(1, pocet + 1))


NAV = [("kam", "nav.kam"), ("cesta", "nav.cesta"), ("lide", "nav.lide"),
       ("provas", "nav.provas"), ("prihlaska", "nav.cena"), ("otazky", "nav.otazky")]


def navigace():
    return "".join('<a href="#%s" data-i18n="%s">%s</a>' % (kotva, klic, CS[klic])
                   for kotva, klic in NAV)


def fakta_seznam():
    """Prakticke informace jako harmonika: na strance je vidiet jen devet
    otazek, odpovedi se rozkliknou. Delka stranky tim klesne o dve tretiny."""
    radky = []
    for k in ["spani", "jidlo", "namaha", "vizum", "skupina"]:
        dd = CS["prakt.%s.dd" % k]
        if k == "kontakt":
            telo = '<a href="mailto:%s" data-i18n="prakt.kontakt.dd">%s</a>' % (MAIL, dd)
        else:
            telo = '<span data-i18n="prakt.%s.dd">%s</span>' % (k, dd)
        tiche = ""
        if ("prakt.%s.q" % k) in CS:
            if k == "kontakt":
                tiche = ('<span class="tise"><span data-i18n="prakt.kontakt.q">%s</span> '
                         '<a href="https://wa.me/%s" target="_blank" rel="noopener">'
                         'WhatsApp</a>.</span>' % (CS["prakt.kontakt.q"], WA))
            else:
                tiche = txt("prakt.%s.q" % k, "span", "tise")
        radky.append('<details class="otazka">%s<p>%s%s</p></details>'
                     % (txt("prakt.%s.dt" % k, "summary"), telo, tiche))
    return "\n        ".join(radky)


# ----------------------------------------------------------------- sablona
HTML = """<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>{jmeno}</title>
<meta name="description" content="{desc}" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="Cura da Floresta" />
<meta property="og:locale" content="cs_CZ" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{desc}" />
<meta property="og:url" content="{adresa}" />
<meta property="og:image" content="{adresa}nahled.jpg" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content="{alt}" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="canonical" href="{adresa}" />
<!-- Ikona musi byt v hlavicce, i kdyz je to jen par kB. Bez ni si ji
     prohlizec sam vyzada na /favicon.ico, jenze Pages tam vrati celou
     stranku s kodem 200 - a kazda navsteva tak stahne HTML jeste jednou
     navic. Naposledy to bylo 147 kB pro nic. -->
<link rel="icon" type="image/png" sizes="48x48"
      href="data:image/png;base64,{ikona}" />
<style>
@font-face {{
  font-family: "Hanken Grotesk";
  font-style: normal; font-weight: 400 700; font-display: swap;
  src: url(data:font/woff2;base64,{font_ext}) format("woff2");
  unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF,
    U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020,
    U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;
}}
@font-face {{
  font-family: "Hanken Grotesk";
  font-style: normal; font-weight: 400 700; font-display: swap;
  src: url(data:font/woff2;base64,{font_lat}) format("woff2");
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA,
    U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193,
    U+2212, U+2215, U+FEFF, U+FFFD;
}}
{css}
.hero__linka {{ background-image: url(data:image/png;base64,{linka}); }}
.pas::before {{ background-image: url(data:image/png;base64,{pas_cop}); }}
.pas--lab::before {{ background-image: url(data:image/png;base64,{pas_lab}); }}
</style>
</head>
<body>

<!-- ============ PŘÍJEZD NA LODI ============ -->
<div class="pristav" id="pristav">
  <canvas id="pristav-platno"></canvas>
  <div class="pristav__vrch">
    <p class="pristav__km" id="pristav-hud" data-vidno="0">{km_popis}<b id="pristav-km">0 / 80</b></p>
    <span class="pristav__ovladace">
      <span class="jazyk">
        <button type="button" data-jazyk="cs" aria-pressed="true">CS</button>
        <button type="button" data-jazyk="en" aria-pressed="false">EN</button>
      </span>
      <button type="button" class="zvuk zvuk--maly" aria-pressed="false"
              aria-label="{zvuk_zap}">
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path class="zvuk__repro" d="M4 9v6h4l5 4V5L8 9H4z" />
      <g class="zvuk__vlny" fill="none" stroke="currentColor" stroke-width="2"
         stroke-linecap="round">
        <path d="M16.5 8.5a5 5 0 0 1 0 7" />
        <path d="M19 6a8.5 8.5 0 0 1 0 12" />
      </g>
      <path class="zvuk__krizek" d="M16.5 9.5l5 5m0-5l-5 5" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" />
    </svg>
      </button>
      <button type="button" class="pristav__preskoc" id="pristav-preskoc"
              data-i18n="pristav.preskoc">{preskoc}</button>
    </span>
  </div>
  <div class="pristav__zacatek" id="pristav-zacatek">
    <img class="pristav__znak" src="{znak}"
         alt="Cura da Floresta" width="300" height="298" />
    {pristav_nadpis}
    <button type="button" class="pristav__vyplout" id="pristav-vyplout"
            data-i18n="pristav.vyplout">{vyplout}</button>
  </div>

  <div class="pristav__spodek">
    <span class="pristav__hlaska" id="pristav-hlaska" data-vidno="0"></span>
    <button type="button" class="pristav__naklon" id="pristav-naklon" hidden>
      <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <rect x="7" y="2.5" width="10" height="19" rx="2.4" fill="none"
              stroke="currentColor" stroke-width="2" />
        <circle cx="12" cy="18.4" r="1.1" fill="currentColor" />
        <path d="M3.2 8.6a5 5 0 0 0-1.1 3.4M20.8 8.6a5 5 0 0 1 1.1 3.4"
              fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" />
      </svg>
      <span data-i18n="pristav.naklon">{naklon}</span>
    </button>
    <div class="pristav__stitek" id="pristav-stitek" data-vidno="0">
      {odkud}
      <p class="pristav__misto" id="pristav-misto" data-klic=""></p>
    </div>
    {navod}
  </div>
</div>

<!-- ============ ŘEKA JAKO OSA ============ -->
<div class="osa" aria-hidden="true">
  <div class="osa__voda">
    <div class="osa__vlny"></div>
    <div class="osa__ujeto" id="osa-ujeto"></div>
  </div>
  <span class="osa__lod" id="osa-lod">
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <circle cx="12" cy="12" r="11" fill="#1F3C36" />
      <!-- pádler sedí v lodi, ne nad ní; jinak to čte jako obličej -->
      <circle cx="12" cy="9.3" r="1.7" fill="#F8BC4C" />
      <path d="M10.6 15.2v-3.4a1.4 1.4 0 0 1 2.8 0v3.4z" fill="#F8BC4C" />
      <path d="M13.3 12.1l3.4 2.1-.8 1.3-3.4-2.1z" fill="#F8BC4C" />
      <path d="M3.4 14.6h17.2c-1.1 2.6-3.4 4-8.6 4s-7.5-1.4-8.6-4z" fill="#FFF2D9" />
      <path d="M5.6 15.9h12.8c-.5.9-1.4 1.5-2.6 1.8H8.2c-1.2-.3-2.1-.9-2.6-1.8z"
            fill="#528E82" />
    </svg>
  </span>
  <span class="osa__stitek" id="osa-stitek"></span>
</div>

<!-- ============ LIŠTA ============ -->
<div class="lista" id="lista" data-vidno="0">
  <a class="lista__domu" href="https://curadafloresta.org/"
     data-i18n-attr="title" data-i18n="lista.domu" title="{lista_domu}">
    <img class="lista__znak" src="{znak}"{rm_znak} alt="Cura da Floresta"
         decoding="async" />
  </a>
  {sticky_label}
  <nav class="lista__nav">{nav}</nav>
  <button type="button" class="zvuk zvuk--maly" aria-pressed="false"
          aria-label="{zvuk_zap}">
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path class="zvuk__repro" d="M4 9v6h4l5 4V5L8 9H4z" />
      <g class="zvuk__vlny" fill="none" stroke="currentColor" stroke-width="2"
         stroke-linecap="round">
        <path d="M16.5 8.5a5 5 0 0 1 0 7" />
        <path d="M19 6a8.5 8.5 0 0 1 0 12" />
      </g>
      <path class="zvuk__krizek" d="M16.5 9.5l5 5m0-5l-5 5" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" />
    </svg>
  </button>
  <span class="jazyk">
    <button type="button" data-jazyk="cs" aria-pressed="true">CS</button>
    <button type="button" data-jazyk="en" aria-pressed="false">EN</button>
  </span>
  <a class="cta" href="#prihlaska" data-i18n="sticky.cta"
     style="padding:.5rem 1.1rem;font-size:.85rem">{sticky_cta}</a>
</div>

<!-- zvuk se ovládá tlačítkem v hlavičce, vlastní přehrávač se nezobrazuje -->
<audio id="hudba-prehravac" loop preload="none"
       src="{hlas}"></audio>

<!-- ============ 1. HLAVIČKA ============ -->
<header class="hero band grain" id="hero">
  <img class="hero__foto" src="{hero_foto}"{rm_hero} alt="" aria-hidden="true"
       decoding="async" fetchpriority="high" />
  <div class="col">
    <div class="hero__vrch">
      <span class="hero__ovladace">
        <span class="jazyk">
          <button type="button" data-jazyk="cs" aria-pressed="true">CS</button>
          <button type="button" data-jazyk="en" aria-pressed="false">EN</button>
        </span>
        <button type="button" class="zvuk zvuk--velky" aria-pressed="false"
                aria-label="{zvuk_zap}">
          <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path class="zvuk__repro" d="M4 9v6h4l5 4V5L8 9H4z" />
      <g class="zvuk__vlny" fill="none" stroke="currentColor" stroke-width="2"
         stroke-linecap="round">
        <path d="M16.5 8.5a5 5 0 0 1 0 7" />
        <path d="M19 6a8.5 8.5 0 0 1 0 12" />
      </g>
      <path class="zvuk__krizek" d="M16.5 9.5l5 5m0-5l-5 5" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" />
    </svg>
          <span class="zvuk__popis" data-i18n="zvuk.zapnout">{zvuk_zap}</span>
        </button>
      </span>
      <img class="hero__znak" src="{znak}"
           alt="Cura da Floresta · União traz a força" width="300" height="298" />
    </div>
    {eyebrow}
    <h1>
      {h1a}
      {h1b}
      {h1c}
    </h1>
    <div class="hero__linka" aria-hidden="true"></div>
    {sub}
    <div class="hero__tlacitka">
      <a class="cta" href="#prihlaska" data-i18n="hero.cta">{cta}</a>
      <a class="cta cta--duch" href="#kam" data-i18n="hero.cta2">{cta2}</a>
      <a class="cta cta--duch" href="{hra_odkaz}" data-hra-cs="{hra_odkaz}"
         data-hra-en="{hra_odkaz_en}" target="_blank" rel="noopener"
         data-i18n="hero.cta3">{cta3}</a>
    </div>
  </div>
</header>

<!-- ============ SBĚR E-MAILŮ ============
     Hned za hlavičkou schválně: kdo doplul, má za sebou 22 vteřin plavby,
     a formuláře za obsahem konvertují výrazně líp než ty nahoře na stránce.
     Jedno pole a jedno zaškrtávátko, protože každé pole navíc stojí konverzi. -->
<section class="zluty band grain" id="zajem">
  <div class="col">
    {zajem_nadpis}
    {zajem_text}
    <form class="pole" id="zajem-form" novalidate>
      <div>
        <label for="z-mail" data-i18n="zajem.mail">{zajem_mail}</label>
        <input type="email" id="z-mail" name="mail" autocomplete="email"
               inputmode="email" required />
      </div>
      <div class="past" aria-hidden="true">
        <label for="z-firma">Firma</label>
        <input id="z-firma" name="firma" type="text" tabindex="-1" autocomplete="off" />
      </div>
      <label class="zaskrtnout">
        <input type="checkbox" id="z-souhlas" required />
        <span data-i18n="zajem.souhlas">{zajem_souhlas}</span>
      </label>
      <div class="tlacitka">
        <button type="submit" class="tlacitko" id="z-odeslat"
                data-i18n="zajem.odeslat">{zajem_odeslat}</button>
      </div>
      <p class="formpozn" id="z-hlaska" role="status" hidden></p>
    </form>
    <p class="formpozn" id="z-hotovo" tabindex="-1" hidden
       data-i18n="zajem.hotovo">{zajem_hotovo}</p>
  </div>
</section>

<!-- ============ PÁS FAKTŮ ============ -->
<section class="faktapas band">
  <div class="col col--siroky">
    <dl class="faktapas__mrizka">
      <div>{f_kdy}{f_kdy_v}</div>
      <div>{f_kde}{f_kde_v}</div>
      <div>{f_cena}{f_cena_v}</div>
    </dl>
  </div>
</section>

<div class="pas pas--zeleny" aria-hidden="true"></div>

<!-- ============ 2. KAM JEDEME ============ -->
<section class="papir band grain" id="kam" data-usek="usek.uvod">
  <div class="col col--siroky">
    {kam_nadpis}
    <div class="intro">
      {intro_lede}
      {intro_p1}
      {intro_p2}
      {intro_p3}
    </div>
    <div class="pasfotek">
      <figure class="pasfotek__hlavni">{pas1}{pas1_pop}</figure>
      <figure>{pas2}{pas2_pop}</figure>
      <figure>{pas3}{pas3_pop}</figure>
    </div>
  </div>
  <figure class="citat">
    <img class="citat__obraz" src="{citat_foto}"{rm_citat} loading="lazy" decoding="async" alt=""
         aria-hidden="true" loading="lazy" decoding="async" />
    <div class="citat__telo">
      <span class="citat__znak" aria-hidden="true"></span>
      <blockquote>{citat}</blockquote>
    </div>
  </figure>
</section>

<!-- ============ 3. CESTA A VESNICE ============ -->
<section class="papir band grain" id="cesta" data-usek="usek.cesta">
  <div class="col col--siroky">
    {cesta_nadpis}
    {cesta_vyzva}
    <div class="trasa">
      <div class="trasa__pas posuvne">
        <div class="trasa__radek">
        {trasa}
        </div>
      </div>
      <div class="karta" id="karta-cesta" hidden>
        <button type="button" class="karta__zavrit" id="zavrit-cesta"
                data-i18n="zavrit" data-i18n-attr="aria-label"
                aria-label="{zavrit}">&#215;</button>
        <div class="karta__telo">
        {karty_cesta}
        </div>
      </div>
    </div>

    {vesnice_nadpis_h3}
    <p class="lead">
      <span class="jen-siroke" data-i18n="vesnice.vyzva.siroke">{vyzva_s}</span>
      <span class="jen-uzke" data-i18n="vesnice.vyzva.uzke">{vyzva_u}</span>
    </p>
    <div class="vesnice">
      <div class="vesnice__posuv posuvne">
        <div class="vesnice__ramec">
          {scena}
          {body}
        </div>
      </div>
      <div class="karta" id="karta-vesnice" hidden>
        <button type="button" class="karta__zavrit" id="zavrit-vesnice"
                data-i18n="zavrit" data-i18n-attr="aria-label"
                aria-label="{zavrit}">&#215;</button>
        <div class="karta__telo">
        {karty_vesnice}
        </div>
      </div>
      <div class="legenda">
        {chipy}
        <button type="button" class="nulovat" id="nulovat-vesnice" hidden
                data-i18n="vynulovat">{vynulovat}</button>
      </div>
    </div>
  </div>
</section>

<!-- ============ 4. KDO TAM BUDE ============ -->
<section class="tmavy band grain" id="lide" data-usek="usek.lide">
  <div class="col col--siroky">
    {lide_nadpis}
    <div class="lide">
    {lide}
    {pruvodkyne}
    </div>
  </div>
</section>

<!-- ============ 5. JE TO PRO VÁS ============ -->
<section class="tmavsi band grain" id="provas" data-usek="usek.bezpeci">
  <div class="col col--siroky">
    {provas_nadpis}
    <div class="dvasloupce">
      <div class="intro">
        {bezpeci_nadpis_h3}
        {bezpeci_p1}
        {bezpeci_p2}
        {bezpeci_p3}
      </div>
      <div>
        {prokoho_pro}
        <ul class="odrazky">
          {prokoho_pro_li}
        </ul>
        {prokoho_neni}
        <ul class="odrazky odrazky--ne">
          {prokoho_neni_li}
        </ul>
      </div>
    </div>
  </div>
</section>

<!-- ============ OHLAS ============ -->
<section class="ohlas band grain">
  <div class="col">
    {ohlas_stitek}
    <figure class="ohlas__karta">
      <figcaption class="ohlas__hlava">
        <span class="ohlas__portret" aria-hidden="true">M</span>
        <span class="ohlas__zdroj">
          <a class="ohlas__jmeno" href="https://www.instagram.com/milinka7/"
             target="_blank" rel="noopener">@milinka7</a>
          <span class="ohlas__kdy">{ikona_ig}<span data-i18n="ohlas.kdo">{ohlas_kdo}</span></span>
        </span>
      </figcaption>
      <blockquote class="ohlas__text">
        {ohlas_p1}
        {ohlas_p2}
      </blockquote>
    </figure>
  </div>
</section>

<!-- ============ 6. CENA A PŘIHLÁŠKA ============ -->
<section class="zluty band grain" id="prihlaska" data-usek="usek.cena">
  <div class="col col--siroky">
    {cena_nadpis}
    <div class="cenovka">
      <div class="cenovka__radek cenovka__radek--hlavni">
        {cena_hlavni_popis}{cena_hlavni}
      </div>
      <div class="cenovka__radek">{cena_letenka_popis}{cena_letenka}</div>
    </div>

    <div class="sloupce">
      <div>
        {vcene_nadpis}
        <ul>
          {vcene_li}
        </ul>
      </div>
      <div>
        {platba_nadpis}
        <ol class="platba__kroky">
          {platba_li}
        </ol>
        {platba_pozn}
      </div>
    </div>

    {hloubka_nadpis_h3}
    <div class="nabidky">
      <div class="nabidka">
        <div class="nabidka__hlava">{meka_h}{meka_cena}</div>
        {meka_foto}
        {meka_p}
      </div>
      <div class="nabidka">
        <div class="nabidka__hlava">{hapaya_h}{hapaya_cena}</div>
        {hapaya_foto}
        {hapaya_p}
        {hapaya_pozn}
      </div>
    </div>

    {kroky_nadpis_h3}
    <div class="kroky">
      <div class="krok">{krok1h}{krok1p}</div>
      <div class="krok">{krok2h}{krok2p}</div>
      <div class="krok">{krok3h}{krok3p}</div>
      <div class="krok">{krok4h}{krok4p}</div>
    </div>

    <form class="pole" id="f-prihlaska" novalidate>
      <div class="pole pole--dve" style="margin-top:0">
        <div>
          <label for="f-jmeno" data-i18n="prih.jmeno">{prih_jmeno}</label>
          <input id="f-jmeno" name="jmeno" type="text" autocomplete="name" required />
        </div>
        <div>
          <label for="f-mail" data-i18n="prih.mail">{prih_mail}</label>
          <input id="f-mail" name="mail" type="email" autocomplete="email" required />
        </div>
      </div>
      <div>
        <label for="f-tel" data-i18n="prih.tel">{prih_tel}</label>
        <input id="f-tel" name="tel" type="tel" autocomplete="tel" />
      </div>
      <div>
        <label for="f-zprava" data-i18n="prih.zprava">{prih_zprava}</label>
        <textarea id="f-zprava" name="zprava"></textarea>
      </div>
      <label class="zaskrtnout">
        <input type="checkbox" id="f-hloubka" />
        <span data-i18n="prih.hapaya">{prih_hapaya}</span>
      </label>
      <div class="past" aria-hidden="true">
        <label for="f-firma">Firma</label>
        <input id="f-firma" name="firma" type="text" tabindex="-1" autocomplete="off" />
      </div>
      <div class="tlacitka">
        <button type="button" class="tlacitko" id="poslat-mail"
                data-i18n="prih.odeslat">{prih_odeslat}</button>
        <button type="button" class="tlacitko tlacitko--druhe" id="poslat-wa"
                data-i18n="prih.wa">{prih_wa}</button>
      </div>
      <p class="formpozn" id="f-hlaska" hidden></p>
      {prih_pozn}
    </form>
    <div class="hotovo" id="f-hotovo" tabindex="-1" hidden>
      <strong data-i18n="prih.hotovo.h">{hotovo_h}</strong>
      {hotovo_p}
    </div>
  </div>
</section>

<!-- ============ 7. OTÁZKY ============ -->
<section class="papir band grain" id="otazky" data-usek="usek.otazky">
  <img class="jacare" src="{jacare}"{rm_jacare} alt="" aria-hidden="true"
       loading="lazy" decoding="async" />
  <div class="col">
    {otazky_nadpis}
    {pdf_slib}
    <div class="otazky">
    {fakta_seznam}
    {otazky}
    </div>
  </div>
</section>

<!-- ============ ZÁVĚR ============ -->
<section class="zaver band grain">
  <img class="zaver__foto" src="{zaver_foto}"{rm_zaver} loading="lazy" decoding="async" alt=""
       aria-hidden="true" loading="lazy" decoding="async" />
  <img class="zaver__had" src="{had}"{rm_had} alt="" aria-hidden="true"
       loading="lazy" decoding="async" />
  <div class="col">
    {zaver1}
    {zaver2}
    {zaver3}
  </div>
</section>

<footer class="paticka">
  <img src="{znak}" alt="" aria-hidden="true" width="300" height="298"
       loading="lazy" decoding="async" />
  <strong>Cura da Floresta</strong>
  <em>União traz a força</em>
  <div class="paticka__odkazy">
    <a class="paticka__odkaz" href="https://www.instagram.com/curadafloresta_org/"
       target="_blank" rel="noopener">
      <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <rect x="3" y="3" width="18" height="18" rx="5.4" fill="none"
              stroke="currentColor" stroke-width="2" />
        <circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="2" />
        <circle cx="17.3" cy="6.7" r="1.45" fill="currentColor" />
      </svg>
      <span>@curadafloresta_org</span>
    </a>
    <a class="paticka__odkaz paticka__odkaz--wa" href="https://wa.me/{wa}"
       target="_blank" rel="noopener">
      <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5.1-1.3A10 10 0 1 0 12 2Zm0 2a8 8 0 1 1-4.1 14.9l-.3-.2-2.6.7.7-2.5-.2-.3A8 8 0 0 1 12 4Zm-3.3 4.3c-.2 0-.5.1-.7.4-.3.3-.9.9-.9 2.1s1 2.4 1.1 2.6c.1.2 1.8 2.9 4.5 3.9 2.2.9 2.7.7 3.2.7.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.2.1-1.3-.1-.1-.3-.2-.5-.3l-1.8-.9c-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.6.1-.2-.1-1-.4-1.9-1.2-.7-.6-1.2-1.4-1.3-1.7-.1-.2 0-.4.1-.5l.4-.5c.1-.2.2-.3.3-.5v-.5l-.8-1.9c-.2-.4-.4-.4-.6-.4h-.4Z" />
      </svg>
      <span data-i18n="foot.wa">{foot_wa}</span>
    </a>
    <a class="paticka__odkaz" href="mailto:{mail}">
      <span>{mail}</span>
    </a>
    <a class="paticka__odkaz" href="https://curadafloresta.org/">
      <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2" />
        <path d="M3 12h18M12 3c2.5 2.7 2.5 15.3 0 18M12 3c-2.5 2.7-2.5 15.3 0 18"
              fill="none" stroke="currentColor" stroke-width="2" />
      </svg>
      <span>curadafloresta.org</span>
    </a>
  </div>
  <p class="paticka__znovu">
    <a href="?znovu" data-i18n="foot.znovu">{foot_znovu}</a>
  </p>
</footer>

<script>window.GEO = {geo};</script>
<script>window.TEXTY = {texty};</script>
<script>{mereni}</script>
<script>{js}</script>
</body>
</html>
"""


def sestav():
    return HTML.format(
        jmeno=CS["meta.jmeno"], title=CS["meta.title"], desc=CS["meta.desc"],
        font_ext=FONT_EXT, font_lat=FONT_LAT, css=(HERE / "styles.css").read_text(),
        linka=LINKA, pas_cop=PAS_COP, pas_lab=PAS_LAB,
        znak=IMG_ZNAK, diamant=IMG_DIAMANT,
        hero_foto=HERO_FOTO, rm_hero=atr_rozmer(RM_HERO),
        jacare=IMG_JACARE, rm_jacare=atr_rozmer(RM_JACARE),
        had=IMG_HAD, rm_had=atr_rozmer(RM_HAD), hlas=HLAS,
        mail=MAIL, wa=WA, adresa=ADRESA,
        alt="Vesnice Chico Curumim shora, doškové chýše u řeky Jordão",
        texty=json.dumps({"cs": CS, "en": EN}, ensure_ascii=False),
        geo=(HERE / "geo.json").read_text(),
        js=(HERE / "app.js").read_text(),
        mereni=(HERE / "mereni.js").read_text(),

        # ---- sber e-mailu ------------------------------------------------
        zajem_nadpis=txt("zajem.nadpis", "h2", "zajem__nadpis"),
        zajem_text=txt("zajem.text", "p", "zajem__text"),
        zajem_mail=CS["zajem.mail"],
        zajem_souhlas=CS["zajem.souhlas"],
        zajem_odeslat=CS["zajem.odeslat"],
        zajem_hotovo=CS["zajem.hotovo"],

        # ---- prijezd -----------------------------------------------------
        km_popis=CS["pristav.km"], preskoc=CS["pristav.preskoc"],
        odkud=txt("pristav.odkud", "p", "pristav__odkud"),
        naklon=CS["pristav.naklon"],
        vyplout=CS["pristav.vyplout"],
        pristav_nadpis=txt("pristav.nadpis", "p", "pristav__nadpis"),
        navod=txt("pristav.navod.mys", "p", "pristav__navod", id="pristav-navod",
                  data_vidno="0"),

        # ---- lista a hlavicka --------------------------------------------
        sticky_label=txt("sticky.label", "span", "lista__popis"),
        sticky_cta=CS["sticky.cta"],
        nav=navigace(),
        zvuk_zap=CS["zvuk.zapnout"],
        eyebrow=txt("hero.eyebrow", "p", "hero__eyebrow"),
        h1a=txt("hero.h1.a", "span", "uvod"),
        h1b=txt("hero.h1.b", "span"),
        h1c=txt("hero.h1.c", "span", "cil"),
        sub=txt("hero.sub", "p", "hero__sub"),
        cta=CS["hero.cta"], cta2=CS["hero.cta2"], cta3=CS["hero.cta3"],
        hra_odkaz=HRA, hra_odkaz_en=HRA_EN,

        # ---- pas faktu ----------------------------------------------------
        f_kdy=txt("fakt.kdy", "dt"), f_kdy_v=txt("fakt.kdy.v", "dd"),
        f_kde=txt("fakt.kde", "dt"), f_kde_v=txt("fakt.kde.v", "dd"),
        f_cena=txt("fakt.cena", "dt"), f_cena_v=txt("fakt.cena.v", "dd"),

        # ---- 2. kam jedeme ------------------------------------------------
        kam_nadpis=txt("kam.nadpis", "h2", "nadpis-sekce"),
        intro_lede=txt("intro.lede", "p", "veta"),
        intro_p1=txt("intro.p1", "p", html=True),
        intro_p2=txt("intro.p2", "p", html=True),
        intro_p3=txt("intro.p3", "p", html=True),
        pas1=foto("pas1", "pas1.alt"), pas1_pop=txt("pas1.pop", "figcaption"),
        pas2=foto("pas2", "pas2.alt"), pas2_pop=txt("pas2.pop", "figcaption"),
        pas3=foto("pas3", "pas3.alt"), pas3_pop=txt("pas3.pop", "figcaption"),
        citat=txt("citat", "p"),
        citat_foto=CITAT_FOTO, rm_citat=atr_rozmer(RM_CITAT),
        rm_znak=atr_rozmer(RM_ZNAK),

        # ---- 3. cesta a vesnice -------------------------------------------
        cesta_nadpis=txt("cesta.nadpis", "h2", "nadpis-sekce"),
        cesta_vyzva=txt("cesta.vyzva", "p", "lead"),
        trasa=trasa(), karty_cesta=karty_cesta(), zavrit=CS["zavrit"],
        vesnice_nadpis_h3=txt("vesnice.nadpis", "h3", "podnadpis"),
        vyzva_s=CS["vesnice.vyzva.siroke"], vyzva_u=CS["vesnice.vyzva.uzke"],
        scena=SV.svg(), body=body_vesnice(),
        karty_vesnice=karty_vesnice(), chipy=chipy_vesnice(),
        vynulovat=CS["vynulovat"],

        # ---- 4. kdo tam bude ----------------------------------------------
        lide_nadpis=txt("lide.spolecny", "h2", "nadpis-sekce"),
        lide=lide(), pruvodkyne=pruvodkyne(),

        # ---- 5. je to pro vas ---------------------------------------------
        provas_nadpis=txt("provas.nadpis", "h2", "nadpis-sekce"),
        bezpeci_nadpis_h3=txt("bezpeci.nadpis", "h3", "podnadpis"),
        bezpeci_p1=txt("bezpeci.p1", "p", html=True),
        bezpeci_p2=txt("bezpeci.p2", "p", html=True),
        bezpeci_p3=txt("bezpeci.p3", "p", html=True),
        prokoho_pro=txt("prokoho.pro", "h3", "podnadpis"),
        prokoho_pro_li=seznam("prokoho.pro", 4),
        prokoho_neni=txt("prokoho.neni", "h3", "podnadpis"),
        prokoho_neni_li=seznam("prokoho.neni", 2),

        # ---- 6. cena a prihlaska ------------------------------------------
        ohlas_stitek=txt("ohlas.stitek", "p", "ohlas__stitek"),
        ohlas_p1=txt("ohlas.p1", "p"),
        ohlas_p2=txt("ohlas.p2", "p"),
        ikona=IKONA,
        ohlas_kdo=CS["ohlas.kdo"],
        ikona_ig=IKONA_IG,
        cena_nadpis=txt("cenaprih.nadpis", "h2", "nadpis-sekce"),
        cena_hlavni_popis=txt("cena.hlavni.popis", "span", "cenovka__popis"),
        cena_hlavni=txt("cena.hlavni", "span", "cenovka__castka"),
        cena_letenka_popis=txt("cena.letenka.popis", "span", "cenovka__popis"),
        cena_letenka=txt("cena.letenka", "span", "cenovka__castka"),
        vcene_nadpis=txt("cena.vcene.nadpis", "h3"),
        vcene_li=seznam("cena.vcene", 6),
        platba_nadpis=txt("cena.platba.nadpis", "h3"),
        platba_li=seznam("cena.platba", 2),
        platba_pozn=txt("cena.platba.pozn", "p", "pozn"),
        hloubka_nadpis_h3=txt("hloubka.nadpis", "h3", "podnadpis"),
        meka_h=txt("hloubka.meka.h", "h3"),
        meka_cena=txt("hloubka.meka.cena", "span", "nabidka__cena"),
        meka_foto=foto("meka", "hloubka.meka.h", "nabidka__foto"),
        meka_p=txt("hloubka.meka.p", "p"),
        hapaya_h=txt("hloubka.hapaya.h", "h3"),
        hapaya_cena=txt("hloubka.hapaya.cena", "span", "nabidka__cena"),
        hapaya_foto=foto("hapaya", "hapaya.alt", "nabidka__foto"),
        hapaya_p=txt("hloubka.hapaya.p", "p"),
        hapaya_pozn=txt("hloubka.hapaya.pozn", "p", "nabidka__pozn"),
        kroky_nadpis_h3=txt("kroky.nadpis", "h3", "podnadpis"),
        krok1h=txt("kroky.1.h", "h3"), krok1p=txt("kroky.1.p", "p", html=True),
        krok2h=txt("kroky.2.h", "h3"), krok2p=txt("kroky.2.p", "p", html=True),
        krok3h=txt("kroky.3.h", "h3"), krok3p=txt("kroky.3.p", "p", html=True),
        krok4h=txt("kroky.4.h", "h3"), krok4p=txt("kroky.4.p", "p", html=True),
        prih_jmeno=CS["prih.jmeno"], prih_mail=CS["prih.mail"],
        prih_tel=CS["prih.tel"], prih_zprava=CS["prih.zprava"],
        prih_hapaya=CS["prih.hapaya"],
        prih_odeslat=CS["prih.odeslat"], prih_wa=CS["prih.wa"],
        prih_pozn=txt("prih.pozn", "p", "formpozn"),
        hotovo_h=CS["prih.hotovo.h"], hotovo_p=txt("prih.hotovo.p", "p"),

        # ---- 7. otazky -----------------------------------------------------
        otazky_nadpis=txt("otazky.nadpis", "h2", "nadpis-sekce"),
        pdf_slib=txt("pdf.slib", "p", "lead"),
        fakta_seznam=fakta_seznam(), otazky=otazky(),

        # ---- 8. hry a zaver -------------------------------------------------
        zaver_foto=ZAVER_FOTO, rm_zaver=atr_rozmer(RM_ZAVER),
        zaver1=txt("zaver.p1", "p"),
        zaver2=txt("zaver.p2", "p", html=True),
        zaver3=txt("zaver.p3", "p"),
        lista_domu=CS["lista.domu"],
        foot_wa=CS["foot.wa"],
        foot_znovu=CS["foot.znovu"],
    )


if __name__ == "__main__":
    out = HERE / "vivencia.html"
    out.write_text(sestav(), encoding="utf-8")
    print("napsáno", out, len(out.read_text(encoding="utf-8")), "znaků")
