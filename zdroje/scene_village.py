"""Chico Curumim — klikaci scena vesnice.

Vizualni system prevzaty z pobyt.curadafloresta.org: ploche tvary,
silueta #1F3C36 na tyrkysove zemi #528E82, kremova a zluta/oranzova
jako akcenty, zadne dekorativni obrysy.

Pravidla, ktera scena drzi:
- kazdy prvek dostava base_y a kresli se nahoru, nic nelevituje
- nic nelze za hranu viewBoxu
- prales je tropicky: palmy a sirokolista korona, ne jehlicnate trojuhelniky
"""

import math

W, H = 1200, 700

GREEN = "#1F3C36"
GREEN_MID = "#3E6F66"
TEAL = "#528E82"
CREAM = "#FFF2D9"
YELLOW = "#F8BC4C"
ORANGE = "#ED6E2C"

out = []
add = out.append


def rnd(i, lo, hi):
    """Deterministicke 'nahodne' cislo, aby byl render stabilni."""
    return lo + (hi - lo) * (((i * 7919 + 104729) % 1000) / 1000.0)


# ---------------------------------------------------------------- prales
def broadleaf(x, base_y, h, fill):
    """Sirokolisty strom: uzky kmen a tri prekryvajici se koruny."""
    tw = h * 0.05
    top = base_y - h
    # kmen zacina uz pod korunou, jinak mezi korunami trci holy pahyl
    p = [f'<rect x="{x-tw/2:.1f}" y="{top+h*0.46:.1f}" '
         f'width="{tw:.1f}" height="{h*0.54:.1f}" fill="{fill}" />']
    for dx, dy, rx, ry in ((0.00, 0.26, 0.32, 0.25),
                           (-0.27, 0.42, 0.24, 0.19),
                           (0.27, 0.42, 0.24, 0.19)):
        p.append(f'<ellipse cx="{x+h*dx:.1f}" cy="{top+h*dy:.1f}" '
                 f'rx="{h*rx:.1f}" ry="{h*ry:.1f}" fill="{fill}" />')
    return "".join(p)


def palm(x, base_y, h, fill, lean=0.0):
    """Palma. Kmen se zuzuje a pokracuje az do koruny, listy se obloukem
    sklaneji dolu. Drive to byly rovne cepele z jednoho bodu, coz se cetlo
    jako zlomena hvezdice."""
    tw = h * 0.032
    top = base_y - h
    tipx = x + h * lean
    p = [f'<path d="M{x-tw:.1f} {base_y:.1f} '
         f'C {x-tw*0.9:.1f} {base_y-h*0.45:.1f}, {tipx-tw*0.6:.1f} {top+h*0.28:.1f}, '
         f'{tipx-tw*0.48:.1f} {top:.1f} L{tipx+tw*0.48:.1f} {top:.1f} '
         f'C {tipx+tw*0.6:.1f} {top+h*0.28:.1f}, {x+tw*0.9:.1f} {base_y-h*0.45:.1f}, '
         f'{x+tw:.1f} {base_y:.1f} Z" fill="{fill}" />',
         f'<ellipse cx="{tipx:.1f}" cy="{top+h*0.014:.1f}" rx="{tw*1.6:.1f}" '
         f'ry="{tw*1.2:.1f}" fill="{fill}" />']
    L = h * 0.46
    for uhel, delka in ((28, 0.82), (60, 1.0), (89, 0.88)):
        for smer in (-1, 1):
            a = math.radians(smer * uhel - 90)
            ca, sa = math.cos(a), math.sin(a)
            d = L * delka
            sir = d * 0.24
            hx, hy = tipx, top + h * 0.012
            kx, ky = hx + ca*d*0.58, hy + sa*d*0.58 + d*0.13
            tx, ty = hx + ca*d,      hy + sa*d      + d*0.40
            nx, ny = -sa, ca
            p.append(f'<path d="M{hx+nx*sir*0.20:.1f} {hy+ny*sir*0.20:.1f} '
                     f'Q {kx+nx*sir:.1f} {ky+ny*sir:.1f} {tx:.1f} {ty:.1f} '
                     f'Q {kx-nx*sir*0.7:.1f} {ky-ny*sir*0.7:.1f} '
                     f'{hx-nx*sir*0.20:.1f} {hy-ny*sir*0.20:.1f} Z" fill="{fill}" />')
    return "".join(p)


def canopy_wall(y_base, count, hmin, hmax, fill, opacity=None, x0=-40, x1=W + 40):
    """Vzdalena stena pralesa: jen prekryvajici se koruny, kmeny nejsou videt."""
    parts = []
    step = (x1 - x0) / count
    for i in range(count):
        x = x0 + step * i
        h = rnd(i, hmin, hmax)
        parts.append(f'<ellipse cx="{x:.1f}" cy="{y_base - h * 0.42:.1f}" '
                     f'rx="{h * 0.40:.1f}" ry="{h * 0.46:.1f}" fill="{fill}" />')
        if i % 2:
            parts.append(f'<ellipse cx="{x + step * 0.5:.1f}" '
                         f'cy="{y_base - h * 0.26:.1f}" rx="{h * 0.34:.1f}" '
                         f'ry="{h * 0.30:.1f}" fill="{fill}" />')
    parts.append(f'<rect x="{x0:.0f}" y="{y_base - 24:.0f}" '
                 f'width="{x1 - x0:.0f}" height="40" fill="{fill}" />')
    op = f' opacity="{opacity}"' if opacity else ""
    return f"<g{op}>" + "".join(parts) + "</g>"


def banana(x, base_y, h, fill):
    """Banovnik: silny kmen a velke listy, ktere stoupaji vzhuru a teprve
    na konci se prohybaji dolu. Drive to byly tuhe listy z jednoho bodu
    do vsech stran, coz se cetlo jako zlomena hvezdice."""
    tw = h * 0.075
    vrch = base_y - h * 0.38
    p = [f'<path d="M{x-tw:.1f} {base_y:.1f} '
         f'C {x-tw*0.92:.1f} {base_y-h*0.16:.1f}, {x-tw*0.7:.1f} {vrch+h*0.06:.1f}, '
         f'{x-tw*0.6:.1f} {vrch:.1f} L{x+tw*0.6:.1f} {vrch:.1f} '
         f'C {x+tw*0.7:.1f} {vrch+h*0.06:.1f}, {x+tw*0.92:.1f} {base_y-h*0.16:.1f}, '
         f'{x+tw:.1f} {base_y:.1f} Z" fill="{fill}" />']
    for uhel, delka, sirka in ((-12, 0.94, 0.26), (13, 0.88, 0.24),
                               (-44, 1.00, 0.28), (46, 0.96, 0.26),
                               (-72, 0.86, 0.25), (74, 0.82, 0.23)):
        a = math.radians(uhel - 90)
        ca, sa = math.cos(a), math.sin(a)
        d = h * 0.95 * delka
        w = d * sirka
        hx, hy = x, vrch + h * 0.02
        kx, ky = hx + ca * d * 0.52, hy + sa * d * 0.52 + d * 0.14
        tx, ty = hx + ca * d,        hy + sa * d        + d * 0.42
        nx, ny = -sa, ca
        p.append(f'<path d="M{hx+nx*w*0.14:.1f} {hy+ny*w*0.14:.1f} '
                 f'Q {kx+nx*w:.1f} {ky+ny*w:.1f} {tx:.1f} {ty:.1f} '
                 f'Q {kx-nx*w*0.7:.1f} {ky-ny*w*0.7:.1f} '
                 f'{hx-nx*w*0.14:.1f} {hy-ny*w*0.14:.1f} Z" fill="{fill}" />')
    return "".join(p)


def jungle(y_base, count, hmin, hmax, fill, opacity=None, x0=-30, x1=W + 30,
           skip=()):
    """skip = intervaly x, kde se nekresli nic (aby vynikla Samauma)."""
    parts = []
    step = (x1 - x0) / count
    for i in range(count):
        x = x0 + step * i + (step * 0.5 if i % 2 else 0)
        if any(a <= x <= b for a, b in skip):
            continue
        h = rnd(i, hmin, hmax)
        yb = y_base + rnd(i + 41, -8, 8)
        if i % 3 == 0:
            parts.append(palm(x, yb, h * 1.12, fill, lean=rnd(i + 7, -0.10, 0.10)))
        else:
            parts.append(broadleaf(x, yb, h, fill))
    op = f' opacity="{opacity}"' if opacity else ""
    return f"<g{op}>" + "".join(parts) + "</g>"


add(f'''<defs>
  <path id="frond" d="M0 0 C 40 -28, 106 -25, 144 0 C 106 25, 40 28, 0 0 Z" />
</defs>''')

add("<!-- vzdaleny kopec -->")
add(f'<path d="M0 226 Q 170 172 340 204 Q 500 234 660 192 Q 830 146 1000 196 '
    f'Q 1110 228 1200 202 L1200 320 L0 320 Z" fill="{TEAL}" opacity="0.38" />')

add("<!-- vzdaleny prales -->")
add(canopy_wall(292, 24, 108, 176, GREEN_MID, 0.6))
add("<!-- blizsi prales -->")
add(jungle(310, 12, 138, 186, GREEN, skip=((30, 330),)))


# ------------------------------------------------- posvatny strom Samauma
def samauma(x, base_y, h):
    """Samauma: nejvyssi strom sceny.
    Kmen prochazi az do korony (zadna mezera), korenove nabehy jsou tri
    oddelene klinky s mezerami, korona je kopule, ne placka."""
    tw = h * 0.055
    top = base_y - h
    trunk_top = top + h * 0.26
    p = []

    # korenove nabehy: tri klinky na kazdou stranu, mezi nimi mezery
    for sgn in (-1, 1):
        for spread, rise, wide in ((4.6, 0.200, 0.62), (2.9, 0.132, 0.52),
                                   (1.5, 0.072, 0.44)):
            x0 = x + sgn * tw * spread
            x1 = x + sgn * tw * spread * wide
            p.append(f'<path d="M{x0:.1f} {base_y} '
                     f'C {x0 - sgn * tw * 0.1:.1f} {base_y - h * rise * 0.45:.1f}, '
                     f'{x + sgn * tw * 0.9:.1f} {base_y - h * rise * 0.78:.1f}, '
                     f'{x + sgn * tw * 0.78:.1f} {base_y - h * rise:.1f} '
                     f'L{x + sgn * tw * 0.3:.1f} {base_y - h * rise * 0.94:.1f} '
                     f'L{x1:.1f} {base_y} Z" fill="{GREEN}" />')

    # kmen: dole sirsi, nahoru se zuzuje, vede az do korony
    p.append(f'<path d="M{x - tw:.1f} {base_y} '
             f'C {x - tw * 0.92:.1f} {base_y - h * 0.34:.1f}, '
             f'{x - tw * 0.72:.1f} {trunk_top + h * 0.10:.1f}, '
             f'{x - tw * 0.62:.1f} {trunk_top:.1f} '
             f'L{x + tw * 0.62:.1f} {trunk_top:.1f} '
             f'C {x + tw * 0.72:.1f} {trunk_top + h * 0.10:.1f}, '
             f'{x + tw * 0.92:.1f} {base_y - h * 0.34:.1f}, '
             f'{x + tw:.1f} {base_y} Z" fill="{GREEN}" />')

    # dve vodorovne vetve pod koronou, s listovym chomacem na konci
    for sgn, dy, ln in ((-1, 0.235, 0.20), (1, 0.205, 0.16)):
        y = top + h * dy
        xe = x + sgn * h * ln
        p.append(f'<path d="M{x:.1f} {y:.1f} L{xe:.1f} {y - h * 0.018:.1f} '
                 f'L{xe:.1f} {y + h * 0.012:.1f} L{x:.1f} {y + h * 0.026:.1f} Z" '
                 f'fill="{GREEN}" />')
        p.append(f'<ellipse cx="{xe:.1f}" cy="{y - h * 0.012:.1f}" '
                 f'rx="{h * 0.072:.1f}" ry="{h * 0.046:.1f}" fill="{GREEN}" />')

    # korona: kopule z prekryvajicich se ovalu, nejvys uprostred
    for dx, dy, rx, ry in ((0.00, 0.075, 0.17, 0.075), (0.00, 0.140, 0.26, 0.130),
                           (-0.20, 0.190, 0.19, 0.100), (0.20, 0.190, 0.19, 0.100),
                           (-0.36, 0.235, 0.13, 0.072), (0.36, 0.235, 0.13, 0.072)):
        p.append(f'<ellipse cx="{x + h * dx:.1f}" cy="{top + h * dy:.1f}" '
                 f'rx="{h * rx:.1f}" ry="{h * ry:.1f}" fill="{GREEN}" />')
    return "".join(p)


# ---------------------------------------------------------------- reka
add("<!-- podrost na brehu -->")
add(f'<g fill="{GREEN}">'
    + "".join(
        f'<ellipse cx="{x}" cy="{300 + (x % 7) - 3}" rx="{46 + (x % 5) * 8}" '
        f'ry="{42 + (x % 4) * 8}" />' for x in range(-20, 1240, 54))
    + f'<rect x="-30" y="300" width="1260" height="26" /></g>')

add("<!-- reka Jordao -->")
add(f'<path d="M0 316 Q 300 302 600 322 Q 900 342 1200 316 L1200 404 '
    f'Q 900 430 600 408 Q 300 386 0 402 Z" fill="{GREEN_MID}" />')
add(f'<g fill="none" stroke="{CREAM}" stroke-width="5" stroke-linecap="round" '
    f'opacity="0.45">'
    f'<path d="M76 352 Q 150 344 224 354" />'
    f'<path d="M660 374 Q 734 382 808 374" />'
    f'<path d="M916 364 Q 990 356 1064 366" />'
    f'<path d="M272 382 Q 346 390 420 382" />'
    f'<path d="M1004 392 Q 1064 386 1124 394" />'
    f'</g>')

add("<!-- zem vesnice -->")
add(f'<path d="M0 402 Q 300 386 600 408 Q 900 430 1200 404 L1200 700 L0 700 Z" '
    f'fill="{TEAL}" />')


# ---------------------------------------------------------------- figury
def person(base=(0, 0), s=1.0, flip=False, arms=None):
    x, base_y = base
    body_h, hw = 62 * s, 22 * s
    g = [f'<circle cx="0" cy="{-body_h-11*s:.1f}" r="{13*s:.1f}" />',
         f'<path d="M{-hw:.1f} 0 Q {-hw:.1f} {-body_h:.1f} 0 {-body_h:.1f} '
         f'Q {hw:.1f} {-body_h:.1f} {hw:.1f} 0 Z" />']
    if arms == "up":
        for sgn in (-1, 1):
            g.append(f'<path d="M{sgn*hw*0.7:.1f} {-body_h*0.86:.1f} '
                     f'L{sgn*hw*1.9:.1f} {-body_h*1.40:.1f} '
                     f'L{sgn*hw*1.42:.1f} {-body_h*1.50:.1f} '
                     f'L{sgn*hw*0.22:.1f} {-body_h*0.96:.1f} Z" />')
    elif arms == "side":
        for sgn in (-1, 1):
            g.append(f'<path d="M{sgn*hw*0.6:.1f} {-body_h*0.84:.1f} '
                     f'L{sgn*hw*2.3:.1f} {-body_h*0.74:.1f} '
                     f'L{sgn*hw*2.3:.1f} {-body_h*0.57:.1f} '
                     f'L{sgn*hw*0.6:.1f} {-body_h*0.62:.1f} Z" />')
    elif arms == "reach":
        g.append(f'<path d="M{hw*0.6:.1f} {-body_h*0.84:.1f} L{hw*2.5:.1f} {-body_h*1.04:.1f} '
                 f'L{hw*2.5:.1f} {-body_h*0.88:.1f} L{hw*0.6:.1f} {-body_h*0.62:.1f} Z" />')
    sc = ' transform="scale(-1,1)"' if flip else ""
    return (f'<g transform="translate({x:.0f} {base_y:.0f})"><g{sc}>'
            + "".join(g) + "</g></g>")


def seated(base=(0, 0), s=1.0, flip=False):
    x, base_y = base
    g = [f'<circle cx="0" cy="{-46*s:.1f}" r="{12*s:.1f}" />',
         f'<path d="M{-19*s:.1f} 0 Q {-19*s:.1f} {-36*s:.1f} 0 {-36*s:.1f} '
         f'Q {17*s:.1f} {-36*s:.1f} {17*s:.1f} 0 Z" />',
         f'<path d="M{9*s:.1f} 0 L{40*s:.1f} {-4*s:.1f} L{40*s:.1f} {-17*s:.1f} '
         f'L{11*s:.1f} {-21*s:.1f} Z" />']
    sc = ' transform="scale(-1,1)"' if flip else ""
    return (f'<g transform="translate({x:.0f} {base_y:.0f})"><g{sc}>'
            + "".join(g) + "</g></g>")


def flower(x, y, s, petal, mid):
    p = [f'<ellipse cx="0" cy="{-5*s:.1f}" rx="{3*s:.1f}" ry="{5*s:.1f}" '
         f'fill="{petal}" transform="rotate({a})" />' for a in (0, 72, 144, 216, 288)]
    p.append(f'<circle r="{2.4*s:.1f}" fill="{mid}" />')
    return f'<g transform="translate({x} {y})">' + "".join(p) + "</g>"


# --------------------------------------------------------- kanoe na rece
add("<!-- kanoe a lov ryb -->")
add(f'''<g id="kanoe">
  <!-- odraz na hladine -->
  <path d="M356 400 Q 442 414 528 400 Q 442 408 356 400 Z" fill="{CREAM}" opacity="0.22" />

  <!-- dlabana kanoe: cocka se spicatymi konci, ne prkno -->
  <path d="M340 380 Q 442 366 544 380 Q 442 412 340 380 Z" fill="{GREEN}" />
  <!-- vydlabana vnitrni cast, aby byla poznat lod a ne deska -->
  <path d="M366 380 Q 442 372 518 380 Q 442 396 366 380 Z" fill="{GREEN_MID}" />
  <!-- lavicka -->
  <rect x="424" y="376" width="40" height="5" rx="2" fill="{GREEN}" />

  <!-- padler: sedici postava, jedna pazi drzi padlo -->
  <g fill="{GREEN}">
    <circle cx="438" cy="330" r="12" />
    <path d="M424 380 Q 424 344 438 344 Q 452 344 452 380 Z" />
    <path d="M448 352 L482 372 L476 380 L444 362 Z" />
  </g>

  <!-- padlo: rovna zerd s listem ve vode -->
  <path d="M452 340 L462 336 L492 398 L482 402 Z" fill="{GREEN}" />
  <path d="M478 392 L500 384 L510 406 L488 414 Z" fill="{GREEN}" />
''' + "</g>")

# --------------------------------------------------------------- samauma
add("<!-- posvatny strom Samauma -->")
add(samauma(212, 502, 400))

# -------------------------------------------------------------- kupixawa
def kupixawa(cx, zem, polosirka, vys_strechy, vys_steny):
    """Kupixawa podle fotek z Chico Curumim (kupixawa-hotova.jpg):
    siroka nizka zvonova doskova strecha, ctupr na vrcholu, roztrepeny
    okraj a pod nim nizka stena ze svetlych svislych kulu."""
    okap = zem - vys_steny
    vrchol = okap - vys_strechy
    p = []

    # stin na zemi
    p.append(f'<ellipse cx="{cx}" cy="{zem + 8}" rx="{polosirka + 22}" ry="24" '
             f'fill="{GREEN}" opacity="0.24" />')

    # --- nizka stena ze svislych kulu, uzsi nez okap (strecha presahuje) ---
    sw = polosirka * 0.83
    p.append(f'<rect x="{cx - sw:.0f}" y="{okap - 4:.0f}" '
             f'width="{2 * sw:.0f}" height="{vys_steny + 4:.0f}" fill="{CREAM}" />')
    x = cx - sw + 7
    while x < cx + sw - 4:
        p.append(f'<rect x="{x:.0f}" y="{okap - 2:.0f}" width="2" '
                 f'height="{vys_steny + 2:.0f}" fill="{GREEN}" opacity="0.32" />')
        x += 7
    # vchod
    p.append(f'<path d="M{cx - 27} {zem} L{cx - 27} {okap + 6} '
             f'Q {cx} {okap - 6} {cx + 27} {okap + 6} L{cx + 27} {zem} Z" '
             f'fill="{GREEN}" />')
    p.append(f'<path d="M{cx - 12} {zem} L{cx - 12} {okap + 15} '
             f'Q {cx} {okap + 9} {cx + 12} {okap + 15} L{cx + 12} {zem} Z" '
             f'fill="{YELLOW}" opacity="0.8" />')
    p.append(f'<rect x="{cx - sw:.0f}" y="{zem - 5:.0f}" '
             f'width="{2 * sw:.0f}" height="7" rx="3" fill="{GREEN}" />')

    # --- zvonova strecha: nahore strmejsi, dole se rozevira ---
    k1x, k1y = polosirka * 0.41, vys_strechy * 0.16
    k2x, k2y = polosirka * 0.88, vys_strechy * 0.64
    p.append(f'<path d="M{cx} {vrchol} '
             f'C {cx + k1x:.0f} {vrchol + k1y:.0f}, {cx + k2x:.0f} {vrchol + k2y:.0f}, '
             f'{cx + polosirka} {okap} L{cx - polosirka} {okap} '
             f'C {cx - k2x:.0f} {vrchol + k2y:.0f}, {cx - k1x:.0f} {vrchol + k1y:.0f}, '
             f'{cx} {vrchol} Z" fill="{GREEN}" />')
    # --- doskove radky: obtacaji kuzel, proto mirne prohnute dolu ---
    for f in (0.30, 0.52, 0.74):
        y = vrchol + vys_strechy * f
        w = polosirka * (f ** 0.72)
        p.append(f'<path d="M{cx - w:.0f} {y:.0f} Q {cx} {y + w * 0.10:.0f} '
                 f'{cx + w:.0f} {y:.0f}" fill="none" stroke="{GREEN_MID}" '
                 f'stroke-width="3" opacity="0.45" />')

    # --- roztrepeny okap ---
    zuby = []
    n = 44
    for i in range(n + 1):
        xx = cx - polosirka + (2 * polosirka) * i / n
        zuby.append(f'{xx:.0f} {okap + (2 + (i * 7919 % 5))}')
    p.append(f'<path d="M{cx - polosirka} {okap} L' + ' L'.join(zuby)
             + f' L{cx + polosirka} {okap} Z" fill="{GREEN}" />')

    # --- cupr na vrcholu: tesna capka primo na hrebeni, zadna stopka ---
    p.append(f'<ellipse cx="{cx}" cy="{vrchol - 3:.0f}" rx="{polosirka * 0.075:.0f}" '
             f'ry="{vys_strechy * 0.105:.0f}" fill="{GREEN}" />')
    return "".join(p)


add("<!-- kupixawa: kruhovy ceremonialni dum -->")
add(f'<g id="kupixawa">{kupixawa(614, 530, 214, 92, 32)}</g>')

# ----------------------------------------------- hospedaria a hamaky
add("<!-- hospedaria a hamaky -->")
add(f'''<g id="hospedaria">
  <rect x="866" y="472" width="15" height="38" fill="{GREEN}" />
  <rect x="1024" y="472" width="15" height="38" fill="{GREEN}" />
  <rect x="858" y="418" width="190" height="56" fill="{YELLOW}" />
  <g fill="{ORANGE}" opacity="0.42">
    <rect x="858" y="430" width="190" height="4" />
    <rect x="858" y="446" width="190" height="4" />
    <rect x="858" y="462" width="190" height="4" />
  </g>
  <rect x="884" y="428" width="32" height="26" fill="{CREAM}" />
  <rect x="990" y="428" width="32" height="26" fill="{CREAM}" />
  <path d="M940 474 L940 432 Q 953 422 966 432 L966 474 Z" fill="{GREEN}" />
  <path d="M896 340 L1010 340 L1062 418 L844 418 Z" fill="{GREEN}" />
  <rect x="890" y="332" width="126" height="10" rx="5" fill="{GREEN}" />
  <rect x="852" y="506" width="202" height="10" rx="4" fill="{GREEN_MID}" />
</g>''')
add(f'''<g id="hamaky">
  <rect x="1078" y="446" width="12" height="94" fill="{GREEN}" />
  <rect x="1160" y="452" width="12" height="88" fill="{GREEN}" />
  <path d="M1082 470 Q 1125 528 1166 474" fill="none" stroke="{CREAM}"
        stroke-width="13" stroke-linecap="round" />
  <path d="M1082 470 Q 1125 508 1166 474" fill="none" stroke="{CREAM}"
        stroke-width="4" stroke-linecap="round" opacity="0.55" />
  <path d="M1082 508 Q 1125 560 1166 512" fill="none" stroke="{CREAM}"
        stroke-width="11" stroke-linecap="round" opacity="0.85" />
</g>''')

# ------------------------------------------------- ohniste, kruh, hudba
add("<!-- ohniste, kruh a hudba -->")
add(f'''<g id="ohniste">
  <path d="M190 606 L302 592 L306 610 L194 624 Z" fill="{GREEN}" />
  <path d="M194 592 L300 622 L296 640 L190 610 Z" fill="{GREEN}" />
  <path d="M248 512 C 280 552, 272 578, 248 592 C 224 578, 216 552, 248 512 Z"
        fill="{ORANGE}" />
  <path d="M248 540 C 264 562, 260 576, 248 586 C 236 576, 232 562, 248 540 Z"
        fill="{YELLOW}" />
</g>''')
add(f'<g id="kruh" fill="{GREEN}">'
    + seated((110, 634), 0.94)
    + seated((186, 664), 0.90)
    + seated((316, 664), 0.90, flip=True)
    + seated((388, 632), 0.94, flip=True)
    + "</g>")
add(f'''<g id="hudba" fill="{GREEN}">
  <g transform="translate(430 646) rotate(15) scale(0.78)">
    <rect x="-5" y="-92" width="10" height="50" rx="4" />
    <rect x="-11" y="-104" width="22" height="15" rx="5" />
    <ellipse cx="0" cy="-28" rx="18" ry="21" />
    <ellipse cx="0" cy="4" rx="26" ry="30" />
    <circle cx="0" cy="-5" r="8" fill="{CREAM}" />
  </g>
  <path d="M62 618 L102 618 L96 668 L68 668 Z" />
  <ellipse cx="82" cy="618" rx="20" ry="7" fill="{YELLOW}" />
  <rect x="64" y="634" width="36" height="5" fill="{ORANGE}" />
</g>''')

# --------------------------------------------- bylinna lazen a hlina Mapu
add("<!-- bylinna lazen a hlina Mapu -->")
add(f'''<g id="lazen">
  <g fill="none" stroke="{CREAM}" stroke-width="5" stroke-linecap="round" opacity="0.6">
    <path d="M626 570 C 616 552, 636 542, 626 522 C 620 510, 628 502, 634 496" />
    <path d="M668 566 C 658 546, 678 536, 668 514 C 663 503, 670 494, 676 488" />
  </g>
  <path d="M588 590 L710 590 L698 634 Q 649 648 600 634 Z" fill="{GREEN}" />
  <ellipse cx="649" cy="590" rx="61" ry="17" fill="{GREEN}" />
  <ellipse cx="649" cy="591" rx="52" ry="12" fill="{CREAM}" />
''' + flower(618, 588, 1.0, YELLOW, ORANGE) + flower(649, 594, 1.05, ORANGE, YELLOW)
    + flower(679, 588, 0.9, YELLOW, ORANGE) + f'''
  <path d="M642 650 C 654 666, 651 676, 642 682 C 633 676, 630 666, 642 650 Z"
        fill="{ORANGE}" />
  <path d="M744 604 L800 604 L792 630 Q 772 638 752 630 Z" fill="{GREEN}" />
  <ellipse cx="772" cy="604" rx="28" ry="9" fill="{ORANGE}" />
</g>''')

# ---------------------------------------------------------------- kene
add("<!-- posvatne malovani kene -->")
add(f'<g id="kene" fill="{GREEN}">'
    + person((884, 640), 0.98, arms="side")
    + seated((948, 644), 0.90, flip=True)
    + "</g>")
add(f'''<g id="kene-vzor">
  <g fill="none" stroke="{ORANGE}" stroke-width="3.6" stroke-linecap="square">
    <path d="M872 592 L884 604 L872 616 L884 628" />
    <path d="M896 592 L884 604 L896 616 L884 628" />
  </g>
  <g fill="{CREAM}" opacity="0.9">
    <rect x="880" y="580" width="8" height="8" transform="rotate(45 884 584)" />
  </g>
</g>''')

# ---------------------------------------------------------------- tance
add("<!-- tance k privolani duchu rostlin -->")
add(f'<g id="tance" fill="{GREEN}">'
    + person((1006, 654), 0.86, arms="up")
    + person((1072, 664), 0.90, arms="up")
    + person((1138, 652), 0.86, arms="up")
    + "</g>")

# ------------------------------------------------ zahradka a nizka zeleno
add("<!-- banovniky ve vesnici -->")
# Drive tu byly banovniky, ale v teto velikosti se v ploche silueta nedaly
# poznat od palem. Nizke palmy se ctou spolehlive.
add(f'<g id="zelen-u-vody">'
    + palm(300, 506, 150, GREEN, lean=-0.05)
    + palm(362, 516, 118, GREEN, lean=0.06)
    + palm(806, 468, 104, GREEN, lean=-0.04)
    + palm(1152, 436, 90, GREEN, lean=0.05)
    + "</g>")


def svg():
    return (f'<svg class="scena__svg" viewBox="0 0 {W} {H}" '
            f'aria-hidden="true" focusable="false">\n' + "\n".join(out) + "\n</svg>")


# hotspoty: klic a souradnice ve viewBoxu
HOTSPOTS = [
    ("samauma",  150, 150),
    ("reka",     440, 356),
    ("kupixawa", 614, 440),
    ("hamaka",   950, 384),
    ("ohen",     248, 552),
    ("lazen",    649, 604),
    ("kene",     906, 606),
    ("tance",   1072, 622),
]


def hotspots_html(labels):
    rows = []
    for key, x, y in HOTSPOTS:
        rows.append(
            f'          <button type="button" class="bod" data-cil="{key}"\n'
            f'                  style="left: {x / W * 100:.1f}%; top: {y / H * 100:.1f}%"\n'
            f'                  data-i18n-attr="aria-label" data-i18n="scena.{key}.bod"\n'
            f'                  aria-label="{labels[key]}"><span></span></button>')
    return "\n".join(rows)


if __name__ == "__main__":
    print(svg())
