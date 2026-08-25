# -*- coding: utf-8 -*-
"""Test prihlasky. Klikaci sonda pres DevTools protokol, na neupravenou stranku.

Pouziti: python3 test_prihlaska.py [cesta/k/vivencia.html]
Bez argumentu vezme vivencia.html vedle sebe.
"""
import cdp, json, pathlib, sys, urllib.parse

STRANKA = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                       else pathlib.Path(__file__).parent / "vivencia.html").resolve()

PRIPRAVA = """
(function(){
  window.__zachyceno = [];
  window.__puvodniOpen = window.open;
  window.open = function(u){ window.__zachyceno.push(u); return null; };
  return !!document.getElementById('f-prihlaska');
})()
"""

VYPLN = """
(function(){
  var d = %s;
  document.getElementById('f-jmeno').value   = d.jmeno   || '';
  document.getElementById('f-mail').value    = d.mail    || '';
  document.getElementById('f-tel').value     = d.tel     || '';
  document.getElementById('f-zprava').value  = d.zprava  || '';
  document.getElementById('f-hloubka').checked = !!d.hloubka;
  document.getElementById('f-firma').value   = d.past    || '';
  var h = document.getElementById('f-hlaska');
  h.hidden = true; h.textContent = '';
  document.getElementById('f-hotovo').hidden = true;
  document.getElementById('f-prihlaska').hidden = false;
  window.__zachyceno.length = 0;
  return true;
})()
"""

STAV = """
(function(){
  var h = document.getElementById('f-hlaska');
  var ho = document.getElementById('f-hotovo');
  var f  = document.getElementById('f-prihlaska');
  return {
    chybaVidno: !h.hidden,
    chybaText: (h.textContent||'').trim(),
    hotovoVidno: !ho.hidden,
    formSkryty: !!f.hidden,
    hotovoText: (ho.textContent||'').trim().replace(/\\s+/g,' ').slice(0,150),
    zachyceno: window.__zachyceno.slice()
  };
})()
"""

PLATNY = {"jmeno": "Jan Dvořák", "mail": "jan@example.com"}
PLNY = {"jmeno": "Jan Dvořák", "mail": "jan@example.com", "tel": "+420 777 123 456",
        "zprava": "Můžu přijet i s partnerkou?", "hloubka": True}

PRIPADY = [
    ("prázdný formulář",        {},                                                     "poslat-wa"),
    ("chybí e-mail",            {"jmeno": "Jan Dvořák"},                                "poslat-wa"),
    ("e-mail bez zavináče",     {"jmeno": "Jan Dvořák", "mail": "jan.example.com"},      "poslat-wa"),
    ("chybí jméno",             {"mail": "jan@example.com"},                            "poslat-wa"),
    ("past na roboty vyplněná", {"jmeno": "Bot", "mail": "b@spam.ru", "past": "SEO"},    "poslat-wa"),
    ("platné minimum",          PLATNY,                                                 "poslat-wa"),
    ("platné plné",             PLNY,                                                   "poslat-wa"),
    ("platné plné",             PLNY,                                                   "poslat-mail"),
]


def bez(s, n=95):
    return s if len(s) <= n else s[:n] + "…"


def spust(jazyk, port):
    b = cdp.Prohlizec("file://%s?rovnou&lang=%s" % (STRANKA, jazyk), port=port)
    b.volej("Page.enable")
    assert b.cekej("document.readyState === 'complete'", 60), "stránka se nenačetla"
    assert b.cekej("!!document.getElementById('f-prihlaska')", 30), "formulář v DOM není"
    assert b.js(PRIPRAVA), "příprava selhala"
    print("=" * 78)
    print("JAZYK %s   |   jazyk stránky podle html: %s" % (jazyk.upper(), b.js("document.documentElement.lang")))
    print("=" * 78)
    vse_ok = True
    for nazev, data, tlacitko in PRIPADY:
        b.js(VYPLN % json.dumps(data, ensure_ascii=False))
        b.nasbirane(0.2)
        b.js("document.getElementById('%s').click()" % tlacitko)
        udal = b.nasbirane(1.2)          # mailto: se pozna z navigacnich udalosti
        s = b.js(STAV)
        mailto = ""
        for u in udal:
            t = json.dumps(u, ensure_ascii=False)
            if "mailto:" in t:
                i = t.index("mailto:")
                mailto = t[i:t.index('"', i)]
                break
        cesta = "WhatsApp" if tlacitko == "poslat-wa" else "e-mail"
        print("\n  %-26s [%s]" % (nazev, cesta))
        print("    chyba: %-5s %s" % (s["chybaVidno"], bez(s["chybaText"], 60)))
        print("    panel hotovo: %-5s   formulář skrytý: %s" % (s["hotovoVidno"], s["formSkryty"]))
        odeslano = (s["zachyceno"][0] if s["zachyceno"] else mailto)
        if odeslano:
            print("    ODESLÁNO: %s" % bez(odeslano.split("?")[0], 60))
            q = urllib.parse.urlparse(odeslano)
            par = urllib.parse.parse_qs(q.query)
            for k in ("text", "body", "subject"):
                if k in par:
                    for r in par[k][0].split("\n"):
                        print("      | %s" % r)
        else:
            print("    ODESLÁNO: nic")
        # ocekavani
        ceka_uspech = nazev in ("platné minimum", "platné plné")
        ceka_chybu = nazev in ("prázdný formulář", "chybí e-mail",
                               "e-mail bez zavináče", "chybí jméno")
        ceka_ticho = nazev == "past na roboty vyplněná"
        if ceka_chybu:
            ok = s["chybaVidno"] and not s["hotovoVidno"] and not odeslano
        elif ceka_ticho:
            ok = (not s["chybaVidno"]) and (not s["hotovoVidno"]) and not odeslano
        else:
            ok = s["hotovoVidno"] and s["formSkryty"] and bool(odeslano) and not s["chybaVidno"]
        print("    -> %s" % ("SEDÍ" if ok else "!!! NESEDÍ"))
        vse_ok = vse_ok and ok
    b.zavri()
    return vse_ok


ok_cs = spust("cs", 9341)
ok_en = spust("en", 9342)
print("\n" + "=" * 78)
print("CELKEM: CS %s | EN %s" % ("v pořádku" if ok_cs else "CHYBA",
                                 "v pořádku" if ok_en else "CHYBA"))
sys.exit(0 if (ok_cs and ok_en) else 1)
