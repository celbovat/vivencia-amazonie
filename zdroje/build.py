# -*- coding: utf-8 -*-
"""Sestavi vivencia.html: fonty a obrazky inline, scena z scene_village.py,
texty z content.py. Vystup je jeden samostatny soubor bez externich zdroju
(CSP v artifactu blokuje cizi hosty)."""

import importlib.util
import json
import pathlib

HERE = pathlib.Path(__file__).parent
A = HERE / "assets"


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


def foto(klic, alt_klic, cls="foto"):
    """Obrazek z decku, vlozeny jako data URI. alt se prepina s jazykem."""
    return ('<img class="%s" loading="lazy" decoding="async" '
            'src="data:image/jpeg;base64,%s" data-i18n="%s" data-i18n-attr="alt" '
            'alt="%s" />' % (cls, (A / "foto" / (klic + ".txt")).read_text().strip(),
                             alt_klic, CS[alt_klic]))


FONT_EXT = b64("font0-HankenGrotesk.txt")
FONT_LAT = b64("font1-HankenGrotesk.txt")
IMG_ZNAK = b64("img-hero__badge.txt")
IMG_DIAMANT = b64("img-hero__diamond.txt")
IMG_JACARE = b64("img-practical__jacare.txt")
IMG_HAD = b64("img-snake.txt")
PAS_COP = b64("css-braid::before.txt")
PAS_LAB = b64("css-braid--lab::before.txt")
LINKA = b64("css-hero__rule.txt")

MAIL = "hello@curadafloresta.org"
WA = "420734490078"

# Adresa stranky. Pri prechodu na vlastni domenu se meni JEN tady.
ADRESA = "https://celbovat.github.io/vivencia-amazonie/"
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
    <img class="pristav__znak" src="data:image/png;base64,{znak}"
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
  <img class="lista__znak" src="data:image/png;base64,{znak}" alt="Cura da Floresta" />
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
<audio id="hudba-prehravac" loop preload="auto"
       src="data:audio/mp4;base64,{hlas}"></audio>

<!-- ============ 1. HLAVIČKA ============ -->
<header class="hero band grain" id="hero">
  <img class="hero__foto" src="data:image/jpeg;base64,{hero_foto}" alt="" aria-hidden="true" />
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
      <img class="hero__znak" src="data:image/png;base64,{znak}"
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
    <img class="citat__obraz" src="data:image/jpeg;base64,{citat_foto}" alt=""
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

    <h3 class="podnadpis">{vesnice_nadpis_h3}</h3>
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
    <figure>
      {ohlas_stitek}
      <blockquote>
        {ohlas_p1}
        {ohlas_p2}
      </blockquote>
      <figcaption class="ohlas__kdo">
        <a href="https://www.instagram.com/milinka7/" target="_blank"
           rel="noopener">@milinka7</a> <span data-i18n="ohlas.kdo">{ohlas_kdo}</span>
      </figcaption>
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

    <h3 class="podnadpis">{hloubka_nadpis_h3}</h3>
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

    <h3 class="podnadpis">{kroky_nadpis_h3}</h3>
    <div class="kroky">
      <div class="krok">{krok1h}{krok1p}</div>
      <div class="krok">{krok2h}{krok2p}</div>
      <div class="krok">{krok3h}{krok3p}</div>
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
  <img class="jacare" src="data:image/png;base64,{jacare}" alt="" aria-hidden="true" />
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
  <img class="zaver__foto" src="data:image/jpeg;base64,{zaver_foto}" alt=""
       aria-hidden="true" loading="lazy" decoding="async" />
  <img class="zaver__had" src="data:image/png;base64,{had}" alt="" aria-hidden="true" />
  <div class="col">
    {zaver1}
    {zaver2}
    {zaver3}
  </div>
</section>

<footer class="paticka">
  <img src="data:image/png;base64,{znak}" alt="" aria-hidden="true" width="300" height="298" />
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
  </div>
  <p class="paticka__znovu">
    <a href="?znovu" data-i18n="foot.znovu">{foot_znovu}</a>
  </p>
</footer>

<script>window.GEO = {geo};</script>
<script>window.TEXTY = {texty};</script>
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
        hero_foto=(A / "foto" / "hero.txt").read_text().strip(), jacare=IMG_JACARE, had=IMG_HAD,
        mail=MAIL, wa=WA, adresa=ADRESA,
        alt="Vesnice Chico Curumim shora, doškové chýše u řeky Jordão",
        texty=json.dumps({"cs": CS, "en": EN}, ensure_ascii=False),
        geo=(HERE / "geo.json").read_text(),
        js=(HERE / "app.js").read_text(),

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
        citat_foto=(A / "foto" / "citat.txt").read_text().strip(),

        # ---- 3. cesta a vesnice -------------------------------------------
        cesta_nadpis=txt("cesta.nadpis", "h2", "nadpis-sekce"),
        cesta_vyzva=txt("cesta.vyzva", "p", "lead"),
        trasa=trasa(), karty_cesta=karty_cesta(), zavrit=CS["zavrit"],
        vesnice_nadpis_h3=CS["vesnice.nadpis"],
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
        ohlas_kdo=CS["ohlas.kdo"],
        cena_nadpis=txt("cenaprih.nadpis", "h2", "nadpis-sekce"),
        cena_hlavni_popis=txt("cena.hlavni.popis", "span", "cenovka__popis"),
        cena_hlavni=txt("cena.hlavni", "span", "cenovka__castka"),
        cena_letenka_popis=txt("cena.letenka.popis", "span", "cenovka__popis"),
        cena_letenka=txt("cena.letenka", "span", "cenovka__castka"),
        vcene_nadpis=txt("cena.vcene.nadpis", "h3"),
        vcene_li=seznam("cena.vcene", 6),
        platba_nadpis=txt("cena.platba.nadpis", "h3"),
        platba_li=seznam("cena.platba", 3),
        platba_pozn=txt("cena.platba.pozn", "p", "pozn"),
        hloubka_nadpis_h3=CS["hloubka.nadpis"],
        meka_h=txt("hloubka.meka.h", "h3"),
        meka_cena=txt("hloubka.meka.cena", "span", "nabidka__cena"),
        meka_foto=foto("meka", "hloubka.meka.h", "nabidka__foto"),
        meka_p=txt("hloubka.meka.p", "p"),
        hlas=(HERE / "assets" / "zvuk" / "hlas.txt").read_text().strip(),
        hapaya_h=txt("hloubka.hapaya.h", "h3"),
        hapaya_cena=txt("hloubka.hapaya.cena", "span", "nabidka__cena"),
        hapaya_foto=foto("hapaya", "hapaya.alt", "nabidka__foto"),
        hapaya_p=txt("hloubka.hapaya.p", "p"),
        hapaya_pozn=txt("hloubka.hapaya.pozn", "p", "nabidka__pozn"),
        kroky_nadpis_h3=CS["kroky.nadpis"],
        krok1h=txt("kroky.1.h", "h3"), krok1p=txt("kroky.1.p", "p", html=True),
        krok2h=txt("kroky.2.h", "h3"), krok2p=txt("kroky.2.p", "p", html=True),
        krok3h=txt("kroky.3.h", "h3"), krok3p=txt("kroky.3.p", "p", html=True),
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
        zaver_foto=(A / "foto" / "zaver.txt").read_text().strip(),
        zaver1=txt("zaver.p1", "p"),
        zaver2=txt("zaver.p2", "p", html=True),
        zaver3=txt("zaver.p3", "p"),
        foot_wa=CS["foot.wa"],
        foot_znovu=CS["foot.znovu"],
    )


if __name__ == "__main__":
    out = HERE / "vivencia.html"
    out.write_text(sestav(), encoding="utf-8")
    print("napsáno", out, len(out.read_text(encoding="utf-8")), "znaků")
