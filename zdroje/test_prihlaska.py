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
  /* Prihlaska chodi na /api/prihlaska, ktere na file:// neexistuje. Fetch se
     tedy podstrcuje a __odpoved rika, co ma server odpovedet: objekt se posle
     jako JSON, retezec 'sit' simuluje vypadek site. */
  window.__odpoved = { ok: true };
  window.__poslano = null;
  /* Po uspesnem odeslani zustane tlacitko disabled a s popiskem
     'Odesilam...' - formular uz je zaroven pryc, takze to na strance
     nevadi. Test ale klika dal, tak si puvodni podobu schova. */
  window.__popisMail = document.getElementById('poslat-mail').textContent;
  window.fetch = function(url, nast){
    window.__poslano = { url: url, telo: nast && nast.body };
    if (window.__odpoved === 'sit') return Promise.reject(new Error('vypadek'));
    var o = window.__odpoved;
    return Promise.resolve({ json: function(){ return Promise.resolve(o); } });
  };
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
  window.__poslano = null;
  var bm = document.getElementById('poslat-mail');
  bm.disabled = false; bm.textContent = window.__popisMail;
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
    zachyceno: window.__zachyceno.slice(),
    poslano: window.__poslano
  };
})()
"""

PLATNY = {"jmeno": "Jan Dvořák", "mail": "jan@example.com"}
PLNY = {"jmeno": "Jan Dvořák", "mail": "jan@example.com", "tel": "+420 777 123 456",
        "zprava": "Můžu přijet i s partnerkou?", "hloubka": True}

# nazev, data, tlacitko, odpoved serveru, co se ceka
#   chyba   - vytkne se nevyplnene pole, nic neodejde
#   ticho   - past na roboty: neodejde nic a clovek se nic nedozvi
#   uspech  - podekovani, formular zmizi
#   posta   - otevre se posta se zalohou, podekovani se neukaze
PRIPADY = [
    ("prázdný formulář",        {},        "poslat-wa",   None,                 "chyba"),
    ("chybí e-mail",            {"jmeno": "Jan Dvořák"},
                                           "poslat-wa",   None,                 "chyba"),
    ("e-mail bez zavináče",     {"jmeno": "Jan Dvořák", "mail": "jan.example.com"},
                                           "poslat-wa",   None,                 "chyba"),
    ("chybí jméno",             {"mail": "jan@example.com"},
                                           "poslat-wa",   None,                 "chyba"),
    ("past na roboty vyplněná", {"jmeno": "Bot", "mail": "b@spam.ru", "past": "SEO"},
                                           "poslat-wa",   None,                 "ticho"),
    ("platné minimum",          PLATNY,    "poslat-wa",   None,                 "uspech"),
    ("platné plné",             PLNY,      "poslat-wa",   None,                 "uspech"),
    ("server přijal",           PLNY,      "poslat-mail", {"ok": True},         "uspech"),
    ("server bez klíče",        PLNY,      "poslat-mail", {"configured": False},"posta"),
    ("server hlásí chybu",      PLNY,      "poslat-mail", {"error": "upstream"},"posta"),
    ("výpadek sítě",            PLNY,      "poslat-mail", "sit",                "posta"),
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
    for nazev, data, tlacitko, odpoved, ceka in PRIPADY:
        b.js("window.__odpoved = %s;" % json.dumps(odpoved, ensure_ascii=False))
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
        if s["poslano"]:
            print("    NA SERVER: %s %s" % (s["poslano"]["url"],
                                            bez(s["poslano"]["telo"] or "", 90)))
        # ocekavani
        if ceka == "chyba":
            ok = s["chybaVidno"] and not s["hotovoVidno"] and not odeslano
        elif ceka == "ticho":
            ok = (not s["chybaVidno"]) and (not s["hotovoVidno"]) and not odeslano \
                and not s["poslano"]
        elif ceka == "posta":
            # zaloha: posta se otevre a podekovani se neukaze. Hlaska se ukazuje
            # jen pri skutecnem vypadku, ne kdyz jen neni nastaveny klic.
            ceka_hlasku = odpoved != {"configured": False}
            ok = bool(odeslano) and not s["hotovoVidno"] \
                and s["chybaVidno"] == ceka_hlasku
        else:
            posilalo_se = bool(odeslano) or bool(s["poslano"])
            ok = s["hotovoVidno"] and s["formSkryty"] and posilalo_se \
                and not s["chybaVidno"]
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
