/* =================================================================
   Nový rok v Amazonii ;  chování stránky
   1) příjezd na lodi (2D plátno, bez závislostí)
   2) řeka jako osa stránky, loďka jede podle odscrollování
   3) klikací vesnice a zastávky cesty
   4) přepínač CS/EN
   ================================================================= */

(function () {
  "use strict";

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* localStorage umí házet výjimku (soukromé okno, zablokovaná data) */
  function pamet(klic, hodnota) {
    try {
      if (hodnota === undefined) return window.localStorage.getItem(klic);
      window.localStorage.setItem(klic, hodnota);
    } catch (e) { /* nevadí, jen si nic nezapamatujeme */ }
    return null;
  }

  var klidnyRezim = window.matchMedia
    && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ===============================================================
     1. JAZYK
     =============================================================== */

  var T = window.TEXTY || { cs: {}, en: {} };
  var jazyk = "cs";

  function prelozit(l) {
    jazyk = l;
    var slovnik = T[l] || {};
    document.documentElement.lang = l;
    $$("[data-i18n]").forEach(function (el) {
      var v = slovnik[el.getAttribute("data-i18n")];
      if (v == null) return;
      var attr = el.getAttribute("data-i18n-attr");
      if (attr) el.setAttribute(attr, v);
      else if (el.hasAttribute("data-i18n-html")) el.innerHTML = v;
      else el.textContent = v;
    });
    /* v záložce má být jméno stránky, ne celý popis */
    if (slovnik["meta.jmeno"]) document.title = slovnik["meta.jmeno"];
    var d = $('meta[name="description"]');
    if (d && slovnik["meta.desc"]) d.setAttribute("content", slovnik["meta.desc"]);
    $$("[data-hra-cs]").forEach(function (a) {
      a.setAttribute("href", a.getAttribute(l === "en" ? "data-hra-en" : "data-hra-cs"));
    });
    $$(".jazyk button").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-jazyk") === l));
    });
    pamet("cdf-vivencia-jazyk", l);
  }

  $$(".jazyk button").forEach(function (b) {
    b.addEventListener("click", function () { prelozit(b.getAttribute("data-jazyk")); });
  });

  (function zvolJazyk() {
    var ulozeny = pamet("cdf-vivencia-jazyk");
    var zUrl = /[?&]lang=en\b/.test(location.search) ? "en"
      : /[?&]lang=cs\b/.test(location.search) ? "cs" : null;
    var zProhlizece = (navigator.language || "cs").toLowerCase().indexOf("cs") === 0 ? "cs" : "en";
    prelozit(zUrl || ulozeny || zProhlizece);
  })();

  function t(klic) { return (T[jazyk] && T[jazyk][klic]) || (T.cs && T.cs[klic]) || ""; }

  /* ===============================================================
     2. PŘÍJEZD NA LODI
     =============================================================== */

  var pristav = $("#pristav");

  function schovejPristav(dopluli) {
    if (!pristav || pristav.hidden) return;
    pristav.hidden = true;
    document.documentElement.style.overflow = "";
    if (dopluli) pamet("cdf-vivencia-doplul", "1");
  }

  function spustPristav() {
    var cv = $("#pristav-platno");
    if (!cv) return schovejPristav(false);

    var ctx = cv.getContext("2d");
    var DPR = Math.min(window.devicePixelRatio || 1, 2);
    var W = 0, H = 0;

    function zmer() {
      W = cv.clientWidth; H = cv.clientHeight;
      cv.width = Math.round(W * DPR);
      cv.height = Math.round(H * DPR);
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
      prepocti();
    }

    var CREAM = "#FFF2D9", GREEN = "#1F3C36", MID = "#3E6F66",
        TEAL = "#528E82", YELLOW = "#F8BC4C", ORANGE = "#ED6E2C";

    /* Barvy a geometrie řeky jsou převzaté z jejich hry /hra/lod, aby to
       vypadalo stejně. V jejím kódu stojí výslovně: Jordão je kalná
       bělavá voda barvy café au lait, nikdy ne modrá ani zelená. */
    var NEBE = "#DDE0D2",           // sky + fog ve hře
        VODA = "#8C7551",           // střed mezi 0x503D25 a 0xC9AE7E
        VODA_SVETLA = "#C9AE7E",
        VODA_TMAVA = "#503D25",
        BREH = "#33543B",
        LISTY = ["#2E5339", "#3D6B43", "#44715C", "#517D3F"],
        KMEN = "#6B5743", KMEN_SED = "#9A948A", KMEN_PALMA = "#8A7458",
        TRUP = "#7A4F2B", STRISKA = "#F5EFE2", KUL = "#5A3A20",
        KLADA = "#5A3A20", MELCINA = "#D8C49A",
        KANYSTR = "#C0392B", BANAN = "#E8C83B";

    var SIRKA_REKY = 16, MEZ = SIRKA_REKY / 2 - 0.8;
    var KAM_Y = 7, KAM_Z = 11, SKLON = 0.1913;   // kamera (0,7,11) -> (0,1,-20)
    var MLHA_OD = 30, MLHA_DO = 140;

    /* osa řeky přesně jako ve hře */
    function osaReky(d) {
      return 13 * Math.sin(d * 0.014) + 7 * Math.sin(d * 0.006 + 2);
    }

    var GEO = window.GEO || { zeme: [], brazilie: [], acre: [] };
    var RAD = Math.PI / 180;

    /* Souřadnice: střed státu Acre a městečko Jordão na stejnojmenné řece.
       Vesnice Chico Curumim leží na Jordãu proti proudu; přesnou polohu
       neznáme, takže značka ukazuje řeku, ne bod vesnice. */
    var ACRE = [-70.5, -9.0], JORDAO = [-71.87, -9.19];

    var faze = "globus";       /* globus -> reka */
    var zacatek = 0;

    var CIL = 80;                    /* stejný cíl jako hra lod: 80 km */
    var JEDNOTEK_NA_KM = 4.5;        /* aby plavba trvala zhruba čtvrt minuty */

    var km = 0, rychlost = 34;       /* jednotky řeky za vteřinu */
    var t0 = 0, bezi = true, dojel = false, konecT = 0;
    var ujeto = 0;                   /* pozice kamery po řece */
    var lodU = 0, mirim = 0, cil = null;
    var prekazky = [], darky = [];
    var otres = 0, hlaskaDo = 0, dalsi = 0;
    var hlaska = $("#pristav-hlaska");
    var citac = $("#pristav-km");
    var misto = $("#pristav-misto");
    var stitek = $("#pristav-stitek");
    var hud = $("#pristav-hud");
    var navod = $("#pristav-navod");

    function rekni(text, ms) {
      if (!hlaska || !text) return;
      hlaska.textContent = "🦜 " + text;
      hlaska.setAttribute("data-vidno", "1");
      hlaskaDo = performance.now() + (ms || 2200);
    }

    var HL_START = t("pristav.hlaska.start");
    var HL_NARAZ = (t("pristav.hlaska.naraz") || "").split("|");
    var HL_BANAN = (t("pristav.hlaska.banan") || "").split("|");
    var HL_BLIZKO = t("pristav.hlaska.blizko");
    function nahodna(p) { return p[Math.floor(Math.random() * p.length)] || ""; }

    /* ------------------------------------------------------- zeměkoule */

    function hladce(x) {
      x = Math.max(0, Math.min(1, x));
      return x * x * (3 - 2 * x);
    }

    /* Ortografická projekce: přesně to, co vidí oko nad koulí.
       Vrací null pro body na odvrácené straně. */
    function promitni(lon, lat, lam0, phi0, R, cx, cy) {
      var l = (lon - lam0) * RAD, p = lat * RAD, p0 = phi0 * RAD;
      var sp = Math.sin(p), cp = Math.cos(p), cl = Math.cos(l);
      if (Math.sin(p0) * sp + Math.cos(p0) * cp * cl < 0) return null;
      return [cx + R * cp * Math.sin(l),
              cy - R * (Math.cos(p0) * sp - Math.sin(p0) * cp * cl)];
    }

    function kresliTvary(rings, lam0, phi0, R, cx, cy, barva) {
      ctx.fillStyle = barva;
      for (var i = 0; i < rings.length; i++) {
        var r = rings[i], body = [];
        for (var j = 0; j < r.length; j++) {
          var q = promitni(r[j][0], r[j][1], lam0, phi0, R, cx, cy);
          if (q) body.push(q);
        }
        if (body.length < 3) continue;
        ctx.beginPath();
        ctx.moveTo(body[0][0], body[0][1]);
        for (var k = 1; k < body.length; k++) ctx.lineTo(body[k][0], body[k][1]);
        ctx.closePath();
        ctx.fill();
      }
    }

    function znacka(lon, lat, lam0, phi0, R, cx, cy, r, cas) {
      var q = promitni(lon, lat, lam0, phi0, R, cx, cy);
      if (!q) return;
      var tep = 1 + Math.sin(cas * 4) * 0.18;
      ctx.strokeStyle = ORANGE;
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.arc(q[0], q[1], r * 2.2 * tep, 0, Math.PI * 2);
      ctx.stroke();
      ctx.fillStyle = ORANGE;
      ctx.beginPath();
      ctx.arc(q[0], q[1], r, 0, Math.PI * 2);
      ctx.fill();
    }

    /* časová osa náletu, v sekundách od začátku */
    var T_OTOC = 1.8, T_BRAZ = 3.0, T_ACRE = 4.0, T_REKA = 5.6, T_KONEC = 6.5;

    function kresliGlobus(cas) {
      ctx.fillStyle = GREEN;
      ctx.fillRect(0, 0, W, H);

      var cx = W / 2, cy = H * 0.46;
      var R0 = Math.min(W, H) * 0.33;

      /* otočení od Atlantiku k Acre a plynulý sestup */
      var o = hladce(cas / T_OTOC);
      var lam0 = -18 + (ACRE[0] + 18) * o;
      var phi0 = 14 + (ACRE[1] - 14) * o;
      var z = hladce((cas - T_OTOC) / (T_REKA - T_OTOC));
      var R = R0 * Math.pow(22, z);

      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, R, 0, Math.PI * 2);
      ctx.clip();

      /* oceán */
      ctx.fillStyle = MID;
      ctx.beginPath();
      ctx.arc(cx, cy, R, 0, Math.PI * 2);
      ctx.fill();

      kresliTvary(GEO.zeme, lam0, phi0, R, cx, cy, TEAL);

      if (cas > T_OTOC * 0.7) {
        ctx.globalAlpha = hladce((cas - T_OTOC * 0.7) / 1.0);
        kresliTvary(GEO.brazilie, lam0, phi0, R, cx, cy, CREAM);
        ctx.globalAlpha = 1;
      }
      if (cas > T_BRAZ) {
        ctx.globalAlpha = hladce((cas - T_BRAZ) / 0.9);
        kresliTvary(GEO.acre, lam0, phi0, R, cx, cy, YELLOW);
        ctx.globalAlpha = 1;
      }
      if (cas > T_ACRE) {
        znacka(JORDAO[0], JORDAO[1], lam0, phi0, R, cx, cy,
               Math.min(9, 3 + R / 900), cas);
      }
      ctx.restore();

      /* obrys koule, dokud je vidět celá */
      if (R < Math.max(W, H)) {
        ctx.strokeStyle = "rgba(255,242,217,0.28)";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(cx, cy, R, 0, Math.PI * 2);
        ctx.stroke();
      }

      /* popisek místa */
      var m = cas < T_OTOC * 0.9 ? "zeme"
            : cas < T_BRAZ ? "brazilie"
            : cas < T_ACRE ? "acre" : "reka";
      if (misto && misto.getAttribute("data-klic") !== m) {
        misto.setAttribute("data-klic", m);
        misto.textContent = t("pristav.misto." + m);
      }

      /* na konci se mapa ztmaví do zelené, ať přechod na řeku neskočí */
      if (cas > T_REKA) {
        ctx.globalAlpha = hladce((cas - T_REKA) / (T_KONEC - T_REKA));
        ctx.fillStyle = NEBE;
        ctx.fillRect(0, 0, W, H);
        ctx.globalAlpha = 1;
      }

      if (cas > T_KONEC) {
        faze = "reka";
        pristav.classList.add("pristav--reka");
        if (stitek) stitek.setAttribute("data-vidno", "0");
        if (hud) hud.setAttribute("data-vidno", "1");
        if (navod) navod.setAttribute("data-vidno", "1");
        rekni(HL_START, 2800);
      }
    }

    /* ------------------------------------------- perspektiva jako ve hře */

    var f = 0, obzor = 0;

    function prepocti() {
      /* Na širokém displeji rozhoduje svislé fov 65° jako ve hře.
         Na úzkém telefonu by ale koryto přeteklo přes celou šířku a břehy
         by nebyly vidět, proto se ohnisko omezuje i podle šířky. */
      var podleVysky = (H / 2) / Math.tan(32.5 * RAD);
      var podleSirky = 0.9 * W;
      f = Math.min(podleVysky, podleSirky);
      obzor = H / 2 - f * Math.sin(SKLON);
    }

    /* Bod na hladině: d = vzdálenost před kamerou, u = stranou. */
    function naPlatno(d, u) {
      var hl = 7 * Math.sin(SKLON) + d * Math.cos(SKLON);
      if (hl < 0.6) return null;
      return [W / 2 + f * u / hl,
              H / 2 + f * (KAM_Y * Math.cos(SKLON) - d * Math.sin(SKLON)) / hl,
              f / hl];                              /* měřítko pro velikosti */
    }

    function mlha(d) {
      return Math.max(0, Math.min(1, (d - MLHA_OD) / (MLHA_DO - MLHA_OD)));
    }

    function kresliVodu(cas) {
      ctx.fillStyle = NEBE;
      ctx.fillRect(0, 0, W, H);

      /* Pod obzorem je rovnou tmavá džungle. Kdyby tu byla světlá zem
         (bankGround ze hry), čte se okolí řeky jako trávník. */
      ctx.fillStyle = "#2E5339";
      ctx.fillRect(0, obzor, W, H - obzor);
      /* pruh vzdálených korun těsně nad obzorem */
      ctx.fillStyle = "#44715C";
      ctx.beginPath();
      for (var q = -20; q < W + 20; q += 14) {
        var vv = 5 + 4 * Math.sin(q * 0.031 + ujeto * 0.05)
                   + 2.5 * Math.sin(q * 0.077 - ujeto * 0.02);
        if (q === -20) ctx.moveTo(q, obzor - vv); else ctx.lineTo(q, obzor - vv);
      }
      ctx.lineTo(W + 20, obzor + 4);
      ctx.lineTo(-20, obzor + 4);
      ctx.closePath();
      ctx.fill();

      /* koryto: jeden mnohoúhelník od blízka k obzoru */
      var c0 = osaReky(ujeto + KAM_Z);
      var levy = [], pravy = [];
      for (var d = 3; d < 170; d += d < 30 ? 2 : 6) {
        var c = osaReky(ujeto + d) - c0;
        var L = naPlatno(d, c - SIRKA_REKY / 2);
        var P = naPlatno(d, c + SIRKA_REKY / 2);
        if (L && P) { levy.push(L); pravy.push(P); }
      }
      if (levy.length < 2) return;
      ctx.beginPath();
      ctx.moveTo(levy[0][0], levy[0][1]);
      for (var i = 1; i < levy.length; i++) ctx.lineTo(levy[i][0], levy[i][1]);
      for (var j = pravy.length - 1; j >= 0; j--) ctx.lineTo(pravy[j][0], pravy[j][1]);
      ctx.closePath();

      /* U obzoru se v hladině zrcadlí obloha, u přídě je voda temnější.
         Bez tohohle přechodu vypadá koryto jako hnědá cesta. */
      var g = ctx.createLinearGradient(0, obzor, 0, H);
      g.addColorStop(0, "#9C8A67");
      g.addColorStop(0.30, "#7A6444");
      g.addColorStop(1, "#57432A");
      ctx.fillStyle = g;
      ctx.fill();

      /* Žádné příčné pruhy: v perspektivě se čtou jako prkna lávky.
         Vodu prozradí protáhlé odlesky ležící po proudu. */
      ctx.save();
      ctx.clip();
      var krok = 3.2;
      var prvni = Math.ceil((ujeto - 4) / krok) * krok;
      for (var s = prvni; s < ujeto + 140; s += krok) {
        var dd = s - ujeto;
        if (dd < 4) continue;
        var op = 1 - mlha(dd);
        if (op <= 0.03) continue;
        var cc = osaReky(s) - c0;
        for (var k = 0; k < 3; k++) {
          var h1 = ((Math.round(s * 10) * 7919 + k * 104729) % 1000) / 1000;
          var h2 = ((Math.round(s * 10) * 6151 + k * 39163) % 1000) / 1000;
          var u = cc + (h1 - 0.5) * (SIRKA_REKY - 1.5);
          var P = naPlatno(dd + h2 * krok, u);
          if (!P) continue;
          var m = P[2];
          var tep = 0.55 + 0.45 * Math.sin(s * 1.3 + cas * 2.6 + k);
          ctx.globalAlpha = op * 0.30 * tep;
          ctx.fillStyle = h2 > 0.45 ? VODA_SVETLA : VODA_TMAVA;
          ctx.beginPath();
          ctx.ellipse(P[0], P[1], (0.5 + h2 * 1.1) * m, 0.11 * m, 0, 0, Math.PI * 2);
          ctx.fill();
        }
      }
      ctx.globalAlpha = 1;
      ctx.restore();

      /* Lesk: ve hře ho dělá specular 0xB89E68 se sluncem vlevo nahoře.
         Bez něj se hnědé koryto čte jako cesta, ne jako voda. */
      var lx = W * 0.5 - W * 0.13, ly = obzor + (H - obzor) * 0.30;
      var sv = ctx.createRadialGradient(lx, ly, 0, lx, ly, W * 0.30);
      sv.addColorStop(0, "rgba(232,214,168,0.26)");
      sv.addColorStop(0.5, "rgba(232,214,168,0.08)");
      sv.addColorStop(1, "rgba(232,214,168,0)");
      ctx.globalAlpha = 1;
      ctx.fillStyle = sv;
      ctx.fillRect(0, obzor, W, H - obzor);

      ctx.globalAlpha = 1;
      ctx.restore();
    }

    /* deterministicky rozhozeny prales na obou brezich */
    function sum(n, k) { return ((n * 7919 + k * 104729) % 1000) / 1000; }

    /* Přední pás zeleně u samé hladiny. Zadní masu už tvoří tmavé pozadí
       pod obzorem, takže tady stačí obrys, který kopíruje břeh. */
    function stenaVysky(s) {
      return 3.4 + 1.5 * Math.sin(s * 0.11) + 0.9 * Math.sin(s * 0.043 + 1.7);
    }

    function kresliBrehy() {
      var c0 = osaReky(ujeto + KAM_Z);

      for (var strana = -1; strana <= 1; strana += 2) {
        var dole = [], nahore = [];
        for (var d = 5; d < 160; d += d < 34 ? 1.4 : 5) {
          var s = ujeto + d;
          var c = osaReky(s) - c0;
          var A = naPlatno(d, c + strana * (SIRKA_REKY / 2 + 0.4));
          if (!A) continue;
          var h = stenaVysky(s + strana * 41);
          dole.push(A);
          nahore.push([A[0], A[1] - h * A[2]]);
        }
        if (dole.length < 2) continue;
        ctx.beginPath();
        ctx.moveTo(dole[0][0], dole[0][1]);
        for (var i = 1; i < dole.length; i++) ctx.lineTo(dole[i][0], dole[i][1]);
        for (var j = nahore.length - 1; j >= 0; j--) ctx.lineTo(nahore[j][0], nahore[j][1]);
        ctx.closePath();
        ctx.fillStyle = "#3D6B43";
        ctx.fill();
      }

      /* Odraz břehu ve vodě. Bez něj se koryto čte jako cesta,
         protože hrana mezi zelení a hnědou je moc čistá. */
      for (var strana2 = -1; strana2 <= 1; strana2 += 2) {
        var vrch = [], spod = [];
        for (var d2 = 6; d2 < 90; d2 += d2 < 30 ? 1.6 : 5) {
          var s2 = ujeto + d2;
          var c2 = osaReky(s2) - c0;
          var B = naPlatno(d2, c2 + strana2 * (SIRKA_REKY / 2 + 0.2));
          if (!B) continue;
          var h2b = stenaVysky(s2 + strana2 * 41);
          vrch.push(B);
          spod.push([B[0] + strana2 * 0.4 * B[2], B[1] + h2b * B[2] * 0.30]);
        }
        if (vrch.length < 2) continue;
        ctx.save();
        ctx.globalAlpha = 0.30;
        ctx.beginPath();
        ctx.moveTo(vrch[0][0], vrch[0][1]);
        for (var i2 = 1; i2 < vrch.length; i2++) ctx.lineTo(vrch[i2][0], vrch[i2][1]);
        for (var j2 = spod.length - 1; j2 >= 0; j2--) ctx.lineTo(spod[j2][0], spod[j2][1]);
        ctx.closePath();
        ctx.fillStyle = "#2E5339";
        ctx.fill();
        ctx.restore();
      }

      /* rostliny u hladiny, aby hrana nebyla jako pravítko */
      var SEG = 6;
      var od = Math.floor((ujeto + 4) / SEG), do_ = Math.ceil((ujeto + 110) / SEG);
      for (var n = od; n < do_; n++) {
        var sn = n * SEG, dd = sn - ujeto;
        if (dd < 6) continue;
        var cn = osaReky(sn) - c0;
        for (var st = -1; st <= 1; st += 2) {
          var un = cn + st * (SIRKA_REKY / 2 - 0.2 + sum(n, st + 3) * 1.4);
          var p = naPlatno(dd, un);
          if (!p) continue;
          var m = p[2], op = 1 - mlha(dd);
          if (op <= 0.02) continue;
          /* většinou keř u vody; kmen jen občas, jinak vznikne alej */
          var kmen = sum(n, st + 5) > 0.72;
          var vys = kmen ? 3.4 + sum(n, st + 7) * 2.6 : 0.5 + sum(n, st + 7) * 0.9;
          var r = 1.1 + sum(n, st + 11) * 1.4;
          ctx.globalAlpha = op;
          if (kmen) {
            ctx.fillStyle = KMEN_PALMA;
            ctx.fillRect(p[0] - 0.1 * m, p[1] - vys * m, 0.2 * m, vys * m);
          }
          ctx.fillStyle = LISTY[Math.floor(sum(n, st + 13) * LISTY.length)];
          for (var kq = 0; kq < (kmen ? 1 : 3); kq++) {
            var dx = kmen ? 0 : (sum(n, st + kq + 29) - 0.5) * 2.4;
            var dy = kmen ? 0 : sum(n, st + kq + 31) * 0.5;
            ctx.beginPath();
            ctx.ellipse(p[0] + dx * m, p[1] - (vys + dy) * m,
                        r * m * (kmen ? 1 : 0.7), r * 0.62 * m * (kmen ? 1 : 0.7),
                        0, 0, Math.PI * 2);
            ctx.fill();
          }
          ctx.globalAlpha = 1;
        }
      }
    }

    function kresliMlhu() {
      /* jen úzký pás u obzoru; vzdálenost samotnou už řeší mlha() u prvků */
      var g = ctx.createLinearGradient(0, obzor - 4, 0, obzor + H * 0.11);
      g.addColorStop(0, "rgba(221,224,210,0.85)");
      g.addColorStop(1, "rgba(221,224,210,0)");
      ctx.fillStyle = g;
      ctx.fillRect(0, obzor - 4, W, H * 0.12);
    }

    function kresliPrekazky() {
      var c0 = osaReky(ujeto + KAM_Z);
      var vse = prekazky.concat(darky);
      vse.sort(function (a1, b1) { return b1.s - a1.s; });
      for (var i = 0; i < vse.length; i++) {
        var o = vse[i], d = o.s - ujeto;
        if (d < 1.5 || d > 160) continue;
        var c = osaReky(o.s) - c0;
        var p = naPlatno(d, c + o.u);
        if (!p) continue;
        var m = p[2], op = 1 - mlha(d);
        if (op <= 0.02) continue;
        ctx.globalAlpha = op;
        var x = p[0], y = p[1];
        if (o.druh === "klada") {
          ctx.fillStyle = KLADA;
          ctx.beginPath();
          ctx.ellipse(x, y - 0.3 * m, 2.4 * m, 0.5 * m, 0, 0, Math.PI * 2);
          ctx.fill();
        } else if (o.druh === "melcina") {
          ctx.fillStyle = MELCINA;
          ctx.beginPath();
          ctx.ellipse(x, y, 2.4 * m, 0.8 * m, 0, 0, Math.PI * 2);
          ctx.fill();
        } else if (o.druh === "lod") {
          ctx.fillStyle = TRUP;
          ctx.fillRect(x - 0.9 * m, y - 0.9 * m, 1.8 * m, 0.7 * m);
          ctx.fillStyle = MELCINA;
          ctx.fillRect(x - 0.6 * m, y - 1.6 * m, 1.2 * m, 0.8 * m);
        } else if (o.druh === "banan") {
          ctx.fillStyle = BANAN;
          ctx.beginPath();
          ctx.ellipse(x, y - 0.35 * m, 0.45 * m, 0.32 * m, 0, 0, Math.PI * 2);
          ctx.fill();
        } else {
          /* kanystr: tělo, ucho s dírou a hrdlo s uzávěrem.
             Samotný červený obdélník se za kanystr nedal poznat. */
          ctx.fillStyle = KANYSTR;
          ctx.beginPath();
          if (ctx.roundRect) ctx.roundRect(x - 0.38 * m, y - 0.92 * m, 0.76 * m, 0.92 * m, 0.10 * m);
          else ctx.rect(x - 0.38 * m, y - 0.92 * m, 0.76 * m, 0.92 * m);
          ctx.fill();
          ctx.fillRect(x - 0.26 * m, y - 1.10 * m, 0.11 * m, 0.20 * m);
          ctx.fillRect(x + 0.05 * m, y - 1.10 * m, 0.11 * m, 0.20 * m);
          ctx.beginPath();
          if (ctx.roundRect) ctx.roundRect(x - 0.28 * m, y - 1.18 * m, 0.46 * m, 0.11 * m, 0.05 * m);
          else ctx.rect(x - 0.28 * m, y - 1.18 * m, 0.46 * m, 0.11 * m);
          ctx.fill();
          ctx.fillRect(x + 0.20 * m, y - 1.06 * m, 0.17 * m, 0.16 * m);
          ctx.fillStyle = "rgba(0,0,0,0.18)";
          ctx.fillRect(x - 0.24 * m, y - 0.72 * m, 0.48 * m, 0.07 * m);
          ctx.fillRect(x - 0.24 * m, y - 0.42 * m, 0.48 * m, 0.07 * m);
        }
        ctx.globalAlpha = 1;
      }
    }

    /* Loď je ve hře pořád 11 metrů před kamerou, kamera stojí na ose.
       Tvar podle jejího modelu: trup, špice, krémová stříška na čtyřech kůlech. */
    function kresliLod(cas) {
      var p = naPlatno(KAM_Z, lodU);
      if (!p) return;
      var m = p[2], x = p[0], y = p[1] + Math.sin(cas * 2.2) * 1.2;
      var nak = mirim * 0.06;
      ctx.save();
      ctx.translate(x, y);

      /* brázda těsně za zádí */
      ctx.fillStyle = "rgba(255,255,255,0.28)";
      ctx.beginPath();
      ctx.moveTo(-0.95 * m, 0);
      ctx.quadraticCurveTo(0, 1.5 * m, 0.95 * m, 0);
      ctx.quadraticCurveTo(0, 0.5 * m, -0.95 * m, 0);
      ctx.closePath();
      ctx.fill();

      ctx.rotate(nak);

      /* paluba: ubíhá dopředu, proto se nahoře zužuje */
      ctx.fillStyle = "#8A5C33";
      ctx.beginPath();
      ctx.moveTo(-0.9 * m, -0.62 * m);
      ctx.lineTo(0.9 * m, -0.62 * m);
      ctx.lineTo(0.52 * m, -1.34 * m);
      ctx.lineTo(-0.52 * m, -1.34 * m);
      ctx.closePath();
      ctx.fill();

      /* záď */
      ctx.fillStyle = TRUP;
      ctx.beginPath();
      ctx.moveTo(-0.9 * m, -0.62 * m);
      ctx.lineTo(0.9 * m, -0.62 * m);
      ctx.lineTo(0.78 * m, 0.02 * m);
      ctx.quadraticCurveTo(0, 0.22 * m, -0.78 * m, 0.02 * m);
      ctx.closePath();
      ctx.fill();

      /* kormidelník */
      ctx.fillStyle = "#3A2A1C";
      ctx.beginPath();
      ctx.ellipse(0, -1.06 * m, 0.2 * m, 0.28 * m, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(0, -1.42 * m, 0.15 * m, 0, Math.PI * 2);
      ctx.fill();

      /* kůly a krémová stříška */
      ctx.fillStyle = KUL;
      ctx.fillRect(-0.82 * m, -2.05 * m, 0.09 * m, 1.0 * m);
      ctx.fillRect(0.73 * m, -2.05 * m, 0.09 * m, 1.0 * m);
      ctx.fillRect(-0.5 * m, -2.28 * m, 0.07 * m, 0.95 * m);
      ctx.fillRect(0.43 * m, -2.28 * m, 0.07 * m, 0.95 * m);
      ctx.fillStyle = STRISKA;
      ctx.beginPath();
      ctx.moveTo(-0.95 * m, -2.02 * m);
      ctx.lineTo(0.95 * m, -2.02 * m);
      ctx.lineTo(0.6 * m, -2.3 * m);
      ctx.lineTo(-0.6 * m, -2.3 * m);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }

    /* Na konci plavby se na břehu vynoří kupixawa, ten samý kruhový dům
       jako v nakreslené vesnici: široká zvonová doška, čupřina na vrcholu
       a nízká stěna ze světlých kůlů. */
    function kresliVesnici(podil) {
      if (podil <= 0) return;
      var d = 40;
      var c = osaReky(ujeto + d) - osaReky(ujeto + KAM_Z);
      var p = naPlatno(d, c);
      if (!p) return;
      var m = p[2];
      var sirka = 9.5 * m, vysStreny = 6.2 * m, vysSteny = 1.5 * m;
      var cx = p[0], zem = p[1];
      var okap = zem - vysSteny, vrchol = okap - vysStreny;

      ctx.save();
      ctx.globalAlpha = Math.min(1, podil * 1.6);

      // stín na zemi
      ctx.fillStyle = "rgba(40,30,18,0.28)";
      ctx.beginPath();
      ctx.ellipse(cx, zem + 0.2 * m, sirka * 1.06, 0.5 * m, 0, 0, Math.PI * 2);
      ctx.fill();

      // nízká stěna ze světlých kůlů
      var sw = sirka * 0.8;
      ctx.fillStyle = "#BFA678";
      ctx.fillRect(cx - sw, okap - 0.1 * m, sw * 2, vysSteny + 0.1 * m);
      ctx.fillStyle = "rgba(80,60,35,0.35)";
      for (var kx = cx - sw + 0.22 * m; kx < cx + sw; kx += 0.42 * m) {
        ctx.fillRect(kx, okap, 0.1 * m, vysSteny);
      }
      // vchod
      ctx.fillStyle = "#3A2A1C";
      ctx.beginPath();
      ctx.moveTo(cx - 0.85 * m, zem);
      ctx.lineTo(cx - 0.85 * m, okap + 0.35 * m);
      ctx.quadraticCurveTo(cx, okap - 0.15 * m, cx + 0.85 * m, okap + 0.35 * m);
      ctx.lineTo(cx + 0.85 * m, zem);
      ctx.closePath();
      ctx.fill();

      // zvonová doška, hnědá jako doopravdy uschlá palma
      ctx.fillStyle = "#8B6B45";
      ctx.beginPath();
      ctx.moveTo(cx, vrchol);
      ctx.bezierCurveTo(cx + sirka * 0.42, vrchol + vysStreny * 0.16,
                        cx + sirka * 0.9, vrchol + vysStreny * 0.64,
                        cx + sirka, okap);
      ctx.lineTo(cx - sirka, okap);
      ctx.bezierCurveTo(cx - sirka * 0.9, vrchol + vysStreny * 0.64,
                        cx - sirka * 0.42, vrchol + vysStreny * 0.16,
                        cx, vrchol);
      ctx.closePath();
      ctx.fill();
      // levá polovina ve stínu
      ctx.fillStyle = "rgba(35,24,12,0.22)";
      ctx.beginPath();
      ctx.moveTo(cx, vrchol);
      ctx.bezierCurveTo(cx - sirka * 0.42, vrchol + vysStreny * 0.16,
                        cx - sirka * 0.9, vrchol + vysStreny * 0.64,
                        cx - sirka, okap);
      ctx.lineTo(cx, okap);
      ctx.closePath();
      ctx.fill();
      // doškové řady
      ctx.strokeStyle = "rgba(35,24,12,0.26)";
      ctx.lineWidth = Math.max(1, 0.12 * m);
      for (var f = 0.32; f < 0.85; f += 0.22) {
        var y = vrchol + vysStreny * f;
        var w = sirka * Math.pow(f, 0.72);
        ctx.beginPath();
        ctx.moveTo(cx - w, y);
        ctx.quadraticCurveTo(cx, y + w * 0.12, cx + w, y);
        ctx.stroke();
      }
      // čupřina na hřebeni
      ctx.fillStyle = "#8B6B45";
      ctx.beginPath();
      ctx.ellipse(cx, vrchol - 0.15 * m, sirka * 0.075, vysStreny * 0.1, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    /* ------------------------------------------------------------ stav */

    function pridej(s) {
      var u = (Math.random() - 0.5) * 2 * (MEZ * 0.82);
      if (Math.random() < 0.36) {
        darky.push({ s: s, u: u, druh: Math.random() < 0.7 ? "banan" : "kanystr" });
      } else {
        var r = Math.random();
        prekazky.push({ s: s, u: u,
                        druh: r < 0.45 ? "klada" : r < 0.78 ? "melcina" : "lod" });
      }
    }

    function krok(cas) {
      if (!bezi) return;
      if (!t0) { t0 = cas; zacatek = cas; }
      var dt = Math.min((cas - t0) / 1000, 0.05);
      t0 = cas;
      var sek = cas / 1000;

      if (faze === "globus") {
        kresliGlobus((cas - zacatek) / 1000);
        window.requestAnimationFrame(krok);
        return;
      }

      if (!dojel) {
        if (cil != null) mirim = Math.max(-1, Math.min(1, (cil - 0.5) * 3.2));
        lodU += mirim * dt * 11;
        lodU = Math.max(-MEZ, Math.min(MEZ, lodU));

        ujeto += rychlost * dt;
        km = ujeto / JEDNOTEK_NA_KM;
        rychlost = Math.min(42, rychlost + dt * 2.4);

        if (!dalsi) dalsi = ujeto + 60;
        while (dalsi < ujeto + 170) {
          pridej(dalsi);
          dalsi += 16 + Math.random() * 20;
        }

        /* náraz zpomalí, nikdy neukončí: tohle je příjezd, ne zkouška */
        var lodS = ujeto + KAM_Z;
        for (var i = prekazky.length - 1; i >= 0; i--) {
          var o = prekazky[i];
          if (Math.abs(o.s - lodS) < 2.2 && Math.abs(o.u - lodU) < 2.4) {
            prekazky.splice(i, 1);
            rychlost = Math.max(18, rychlost * 0.55);
            otres = 12;
            rekni(nahodna(HL_NARAZ), 1800);
          } else if (o.s < ujeto - 6) { prekazky.splice(i, 1); }
        }
        for (var j = darky.length - 1; j >= 0; j--) {
          var g = darky[j];
          if (Math.abs(g.s - lodS) < 2.2 && Math.abs(g.u - lodU) < 2.2) {
            darky.splice(j, 1);
            ujeto += (g.druh === "banan" ? 0.3 : 0.5) * JEDNOTEK_NA_KM;
            rychlost = Math.min(48, rychlost + 3);
            rekni(nahodna(HL_BANAN), 1500);
          } else if (g.s < ujeto - 6) { darky.splice(j, 1); }
        }

        if (km >= CIL) { dojel = true; konecT = cas; rekni(HL_BLIZKO, 2200); }
      }

      ctx.save();
      /* při zapnutém "omezit pohyb" se scéna netřese, ale nálet běží dál */
      if (otres > 0) {
        if (!klidnyRezim) {
          ctx.translate((Math.random() - 0.5) * otres, (Math.random() - 0.5) * otres);
        }
        otres -= dt * 60;
      }
      kresliVodu(sek);
      kresliBrehy();
      kresliVesnici(dojel ? Math.min(1, (cas - konecT) / 700) : 0);
      kresliPrekazky();
      kresliMlhu();
      kresliLod(sek);
      ctx.restore();

      if (citac) citac.textContent = Math.min(CIL, Math.floor(km)) + " / " + CIL;
      if (hlaska && hlaskaDo && cas > hlaskaDo) {
        hlaska.setAttribute("data-vidno", "0");
        hlaskaDo = 0;
      }

      if (dojel && cas - konecT > 2200) {
        bezi = false;
        pristav.style.transition = "opacity .5s ease";
        pristav.style.opacity = "0";
        window.setTimeout(function () { schovejPristav(true); }, 400);
        return;
      }
      window.requestAnimationFrame(krok);
    }

    /* --------------------------------------------------------- ovládání */

    function naDotek(e) {
      if (naklonZap) return;            /* naklánění má přednost, jakmile běží */
      var r = cv.getBoundingClientRect();
      var kx = e.touches && e.touches[0] ? e.touches[0].clientX : e.clientX;
      cil = Math.max(0, Math.min(1, (kx - r.left) / r.width));
    }
    cv.addEventListener("pointermove", naDotek);
    cv.addEventListener("pointerdown", naDotek);
    cv.addEventListener("touchmove", function (e) { naDotek(e); e.preventDefault(); },
      { passive: false });

    /* ---- kormidlování nakláněním telefonu -------------------------------
       iOS od verze 13 na to chce svolení, které jde vyžádat jen ze skutečného
       klepnutí, proto tlačítko. Android to dá rovnou. Prst funguje pořád. */
    var naklonTl = $("#pristav-naklon");
    var naklonZap = false;

    /* Na telefonu nemá smysl radit šipky, žádné tam nejsou. */
    var maDotyk = ("ontouchstart" in window) || navigator.maxTouchPoints > 0;
    if (navod && maDotyk) {
      navod.setAttribute("data-i18n", "pristav.navod.dotyk");
      navod.textContent = t("pristav.navod.dotyk");
    }

    function naNaklon(e) {
      if (e.gamma == null) return;
      naklonZap = true;
      var MEZ_UHLU = 22;                      /* pohodlný rozsah zápěstí */
      var podil = Math.max(-1, Math.min(1, e.gamma / MEZ_UHLU));
      cil = 0.5 + podil * 0.5;
    }

    function zapniNaklon() {
      window.addEventListener("deviceorientation", naNaklon);
      if (naklonTl) {
        var popisek = naklonTl.querySelector("span");
        if (popisek) {
          popisek.textContent = t("pristav.naklon.zap");
          popisek.setAttribute("data-i18n", "pristav.naklon.zap");
        }
        naklonTl.disabled = true;
      }
    }

    if (naklonTl && window.DeviceOrientationEvent) {
      if (maDotyk) {
        naklonTl.hidden = false;
        naklonTl.addEventListener("click", function (e) {
          e.stopPropagation();
          var zadost = window.DeviceOrientationEvent.requestPermission;
          if (typeof zadost === "function") {
            zadost().then(function (odpoved) {
              if (odpoved === "granted") zapniNaklon();
              else naklonTl.hidden = true;      /* odmítl, prst funguje dál */
            }).catch(function () { naklonTl.hidden = true; });
          } else {
            zapniNaklon();
          }
        });
      }
    }

    document.addEventListener("keydown", function (e) {
      if (pristav.hidden) return;
      if (e.key === "ArrowLeft") { cil = null; mirim = -1; }
      if (e.key === "ArrowRight") { cil = null; mirim = 1; }
      if (e.key === "Escape" || e.key === "Enter") schovejPristav(false);
    });
    document.addEventListener("keyup", function (e) {
      if (e.key === "ArrowLeft" || e.key === "ArrowRight") mirim = 0;
    });

    window.addEventListener("resize", zmer);
    zmer();
    document.documentElement.style.overflow = "hidden";

    /* Prohlížeč nepustí zvuk sám od sebe, proto se nálet rozjede až
       z klepnutí na Vyplout. To samé klepnutí zároveň spustí hudbu. */
    function vyraz() {
      var karta = $("#pristav-zacatek");
      if (karta) {
        karta.setAttribute("data-mizi", "1");
        window.setTimeout(function () { karta.hidden = true; }, 500);
      }
      if (stitek) stitek.setAttribute("data-vidno", "1");
      window.requestAnimationFrame(krok);
    }
    var tlVyplout = $("#pristav-vyplout");
    if (tlVyplout) {
      tlVyplout.addEventListener("click", function () {
        if (window.__spustHudbu) window.__spustHudbu();
        vyraz();
      });
    } else {
      vyraz();
    }
  }

  (function rozhodniOPristavu() {
    if (!pristav) return;
    /* Nálet se přehraje jen napoprvé, aby vracející se návštěvník
       nemusel pokaždé čekat. ?znovu ho vynutí a zapomene, že už doplul. */
    var chceZnovu = /[?&]znovu\b/.test(location.search);
    if (chceZnovu) {
      try { window.localStorage.removeItem("cdf-vivencia-doplul"); } catch (e) {}
    }
    var uzDoplul = !chceZnovu && pamet("cdf-vivencia-doplul") === "1";
    var chceRovnou = /[?&]rovnou\b/.test(location.search)
      || (!chceZnovu && location.hash.length > 1);
    /* Zapnuté "omezit pohyb" nálet normálně přeskočí, ale když si ho někdo
       vysloveně vyžádá odkazem, má přednost jeho volba. */
    if (uzDoplul || chceRovnou) return schovejPristav(false);
    var b = $("#pristav-preskoc");
    if (b) b.addEventListener("click", function () { schovejPristav(false); });
    spustPristav();
  })();

  /* ===============================================================
     3. ŘEKA JAKO OSA
     =============================================================== */

  (function osa() {
    var lod = $("#osa-lod");
    var ujeto = $("#osa-ujeto");
    var stitek = $("#osa-stitek");
    var hero = $("#hero");
    if (!lod) return;
    var sekce = $$("[data-usek]");
    var tik = false;

    function prekresli() {
      tik = false;
      var vyska = document.documentElement.scrollHeight - window.innerHeight;
      var podil = vyska > 0 ? Math.min(1, Math.max(0, window.scrollY / vyska)) : 0;
      var pct = (podil * 100).toFixed(2) + "%";
      /* loďka se nesmí seknout o horní a dolní hranu obrazovky */
      lod.style.top = (2 + podil * 96).toFixed(2) + "%";
      if (ujeto) ujeto.style.height = pct;

      if (!stitek) return;
      /* štítek se ukáže, až když hlavička odjede */
      var zaHlavickou = hero ? window.scrollY > hero.offsetHeight * 0.6 : true;
      var stred = window.scrollY + window.innerHeight * 0.42, jmeno = "";
      for (var i = 0; i < sekce.length; i++) {
        if (sekce[i].offsetTop <= stred) jmeno = sekce[i].getAttribute("data-usek");
      }
      if (jmeno && zaHlavickou) {
        stitek.textContent = t(jmeno);
        stitek.style.top = (2 + podil * 96).toFixed(2) + "%";
        stitek.style.opacity = "1";
      } else { stitek.style.opacity = "0"; }
    }

    window.addEventListener("scroll", function () {
      if (!tik) { tik = true; window.requestAnimationFrame(prekresli); }
    }, { passive: true });
    window.addEventListener("resize", prekresli);
    prekresli();
  })();

  /* ===============================================================
     4. LIŠTA
     =============================================================== */

  (function lista() {
    var l = $("#lista");
    var hero = $("#hero");
    if (!l || !hero) return;
    var tik = false;
    function zkontroluj() {
      tik = false;
      l.setAttribute("data-vidno", window.scrollY > hero.offsetHeight * 0.7 ? "1" : "0");
    }
    window.addEventListener("scroll", function () {
      if (!tik) { tik = true; window.requestAnimationFrame(zkontroluj); }
    }, { passive: true });
    zkontroluj();
  })();

  /* ===============================================================
     5. ROZKLIKÁVACÍ SKUPINY (vesnice a cesta)
     =============================================================== */

  function skupina(nastaveni) {
    var karta = $(nastaveni.karta);
    if (!karta) return;
    var spouste = $$(nastaveni.spouste);
    var polozky = $$(nastaveni.polozky);
    var zavrit = $(nastaveni.zavrit);
    var nulovat = nastaveni.nulovat ? $(nastaveni.nulovat) : null;
    var precteno = {};

    try {
      precteno = JSON.parse(pamet(nastaveni.klic) || "{}") || {};
    } catch (e) { precteno = {}; }

    function oznac() {
      var kolik = 0;
      spouste.forEach(function (s) {
        var c = s.getAttribute("data-cil");
        if (precteno[c]) { s.setAttribute("data-precteno", "true"); kolik++; }
        else s.removeAttribute("data-precteno");
      });
      if (nulovat) nulovat.hidden = kolik === 0;
    }

    function zavri() {
      karta.hidden = true;
      spouste.forEach(function (s) { s.setAttribute("aria-pressed", "false"); });
    }

    function otevri(c) {
      polozky.forEach(function (p) { p.hidden = p.getAttribute("data-klic") !== c; });
      karta.hidden = false;
      spouste.forEach(function (s) {
        s.setAttribute("aria-pressed", String(s.getAttribute("data-cil") === c));
      });
      precteno[c] = 1;
      pamet(nastaveni.klic, JSON.stringify(precteno));
      oznac();
      var y = karta.getBoundingClientRect();
      if (y.bottom > window.innerHeight || y.top < 0) {
        karta.scrollIntoView({ behavior: klidnyRezim ? "auto" : "smooth", block: "nearest" });
      }
    }

    spouste.forEach(function (s) {
      s.addEventListener("click", function () {
        var c = s.getAttribute("data-cil");
        if (s.getAttribute("aria-pressed") === "true") zavri();
        else otevri(c);
      });
    });
    if (zavrit) zavrit.addEventListener("click", zavri);
    if (nulovat) nulovat.addEventListener("click", function () {
      precteno = {};
      pamet(nastaveni.klic, "{}");
      oznac();
    });
    oznac();
  }

  skupina({
    karta: "#karta-vesnice",
    spouste: "[data-skupina='vesnice']",
    polozky: "#karta-vesnice [data-klic]",
    zavrit: "#zavrit-vesnice",
    nulovat: "#nulovat-vesnice",
    klic: "cdf-vivencia-vesnice"
  });

  skupina({
    karta: "#karta-cesta",
    spouste: "[data-skupina='cesta']",
    polozky: "#karta-cesta [data-klic]",
    zavrit: "#zavrit-cesta",
    klic: "cdf-vivencia-cesta"
  });

  /* ===============================================================
     6. PŘIHLÁŠKA
     =============================================================== */

  (function prihlaska() {
    var form = $("#f-prihlaska");
    if (!form) return;
    var hotovo = $("#f-hotovo");
    var hlaska = $("#f-hlaska");
    var MAIL = "hello@curadafloresta.org";
    var WA = "420734490078";

    function sesbirej() {
      return {
        jmeno: ($("#f-jmeno").value || "").trim(),
        mail: ($("#f-mail").value || "").trim(),
        tel: ($("#f-tel").value || "").trim(),
        zprava: ($("#f-zprava").value || "").trim(),
        hloubka: $("#f-hloubka").checked,
        past: ($("#f-firma").value || "").trim()
      };
    }

    function text(d) {
      return [
        (jazyk === "en"
          ? "Sign-up: Amazon, 27 December 2026 to 8 January 2027"
          : "Přihláška: Amazonie 27. 12. 2026 – 8. 1. 2027"),
        (jazyk === "en" ? "Name" : "Jméno") + ": " + d.jmeno,
        "E-mail: " + d.mail,
        (jazyk === "en" ? "Phone" : "Telefon") + ": "
          + (d.tel || (jazyk === "en" ? "not given" : "neuvedeno")),
        (jazyk === "en" ? "Hãpaya / Huni Meka" : "Hãpaya / Huni Meka") + ": "
          + (d.hloubka ? (jazyk === "en" ? "yes" : "ano") : (jazyk === "en" ? "no" : "ne")),
        (jazyk === "en" ? "Message" : "Zpráva") + ": "
          + (d.zprava || (jazyk === "en" ? "none" : "žádná"))
      ].join("\n");
    }

    function overit(d) {
      if (d.past) return false;                 /* past na roboty */
      if (!d.jmeno || !d.mail || d.mail.indexOf("@") < 0) {
        if (hlaska) { hlaska.textContent = t("prih.chyba"); hlaska.hidden = false; }
        return false;
      }
      if (hlaska) hlaska.hidden = true;
      return true;
    }

    function hotovoUkaz() {
      form.hidden = true;
      if (hotovo) { hotovo.hidden = false; hotovo.focus(); }
    }

    /* Záloha pro případ, že přihláška neodejde: otevře poštu s předvyplněnou
       zprávou, ať se vyplněný formulář neztratí. */
    function otevriPostu(d) {
      var predmet = encodeURIComponent(
        (jazyk === "en" ? "Sign-up Amazon Dec 2026: " : "Přihláška Amazonie prosinec 2026: ")
        + d.jmeno);
      window.location.href = "mailto:" + MAIL + "?subject=" + predmet
        + "&body=" + encodeURIComponent(text(d));
    }

    /* Přihláška jde na /api/prihlaska, odtud ji Pages Function pošle přes Brevo.
       Stejně jako na pobyt.curadafloresta.org. */
    var b1 = $("#poslat-mail");

    function vypadek(d, puvodni) {
      b1.disabled = false;
      b1.textContent = puvodni;
      if (hlaska) { hlaska.hidden = false; hlaska.textContent = t("prih.vypadek"); }
      otevriPostu(d);
    }

    if (b1) b1.addEventListener("click", function () {
      var d = sesbirej();
      if (!overit(d)) return;

      var puvodni = b1.textContent;
      b1.disabled = true;
      b1.textContent = t("prih.odesilam");

      window.fetch("/api/prihlaska", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          jmeno: d.jmeno, mail: d.mail, telefon: d.tel, vzkaz: d.zprava,
          hloubka: d.hloubka, jazyk: jazyk, firma: d.past
        })
      }).then(function (r) {
        return r.json().catch(function () { return {}; });
      }).then(function (odpoved) {
        if (odpoved.ok) {
          if (window.mer) window.mer("prihlaska_odeslana", { vysledek: "ok" });
          hotovoUkaz();
          return;
        }
        if (window.mer) {
          window.mer("prihlaska_odeslana", {
            vysledek: odpoved.configured === false ? "posta" : "chyba"
          });
        }
        /* configured:false není chyba, jen nenastavený klíč k Brevu. Otevře se
           pošta jako dřív a člověku není co hlásit. Cokoli jiného je výpadek,
           tam se hlásí, proč se místo odeslání otevírá pošta. */
        if (odpoved.configured === false) {
          b1.disabled = false;
          b1.textContent = puvodni;
          otevriPostu(d);
        } else {
          vypadek(d, puvodni);
        }
      }).catch(function () {
        if (window.mer) window.mer("prihlaska_odeslana", { vysledek: "chyba" });
        vypadek(d, puvodni);
      });
    });

    var b2 = $("#poslat-wa");
    if (b2) b2.addEventListener("click", function () {
      var d = sesbirej();
      if (!overit(d)) return;
      if (window.mer) window.mer("prihlaska_odeslana", { vysledek: "whatsapp" });
      window.open("https://wa.me/" + WA + "?text=" + encodeURIComponent(text(d)),
        "_blank", "noopener");
      hotovoUkaz();
    });

    form.addEventListener("submit", function (e) { e.preventDefault(); });
  })();

  /* ===============================================================
     7. HUDBA
     Prohlizece nepusti zvuk bez zasahu uzivatele, takze se o to
     pokusime a kdyz to odmitnou, cekame na prvni dotek nebo klavesu.
     Volbu si pamatujeme, kdo si to vypne, tomu uz to nehraje.
     =============================================================== */

  (function hudba() {
    /* pozor: ve scene vesnice je <g id="hudba">, proto jine jmeno */
    var zvuk = $("#hudba-prehravac");
    var tlacitka = $$(".zvuk");            /* jedno v hlavičce, jedno v liště */
    if (!zvuk || !tlacitka.length) return;

    var HLASITOST = 0.45, NABEH = 4.0, DOZNENI = 3.5;
    var hralo = false;

    /* Náběh a doznění řídíme za běhu, ne zapečené v souboru, aby se smyčka
       vracela plynule. Hlasitost se musí nastavit i když prohlížeč ještě
       nezná délku nahrávky, jinak by zůstala na nule a hrálo by to potichu. */
    function nastavHlasitost() {
      var t = zvuk.currentTime || 0;
      var d = zvuk.duration;
      var v = HLASITOST;
      /* Náběh je dlouhý a zrychlující, aby hudba nenaskočila rázem.
         Nezačíná ale úplně na nule, aby nešlo poznat, že hraje. */
      if (t < NABEH) {
        var k = t / NABEH;
        v = HLASITOST * (0.03 + 0.97 * k * k);
      }
      if (d && !isNaN(d) && t > d - DOZNENI) {
        v = Math.min(v, HLASITOST * Math.max(0, (d - t) / DOZNENI));
      }
      zvuk.volume = Math.max(0, Math.min(1, v));
    }
    zvuk.volume = HLASITOST * 0.03;
    zvuk.addEventListener("timeupdate", nastavHlasitost);
    zvuk.addEventListener("playing", nastavHlasitost);

    function stav(hraje) {
      var klic = hraje ? "zvuk.vypnout" : "zvuk.zapnout";
      tlacitka.forEach(function (b) {
        b.setAttribute("aria-pressed", String(hraje));
        b.setAttribute("aria-label", t(klic));
        var popis = b.querySelector(".zvuk__popis");
        if (popis) { popis.setAttribute("data-i18n", klic); popis.textContent = t(klic); }
      });
    }

    function spust() {
      var slib = zvuk.play();
      if (slib && slib.then) slib.catch(function () { /* prohlížeč odmítl */ });
    }
    /* aby hudbu mohlo rozjet i tlačítko Vyplout v náletu */
    window.__spustHudbu = function () {
      if (pamet("cdf-vivencia-zvuk") === "0") return;
      if (zvuk.paused) spust();
    };

    zvuk.addEventListener("play", function () {
      hralo = true;
      tlacitka.forEach(function (b) { b.removeAttribute("data-lakej"); });
      stav(true);
      odpoj();
    });
    zvuk.addEventListener("pause", function () { stav(false); });

    tlacitka.forEach(function (b) {
      b.addEventListener("click", function (e) {
        e.stopPropagation();
        if (zvuk.paused) { pamet("cdf-vivencia-zvuk", "1"); spust(); }
        else { zvuk.pause(); pamet("cdf-vivencia-zvuk", "0"); }
      });
    });

    if (pamet("cdf-vivencia-zvuk") === "0") { stav(false); return; }

    /* Prohlizec nepusti zvuk bez kliknuti a scrollovani se nepocita.
       Zkousime to proto pri KAZDEM doteku, dokud to jednou nevyjde,
       ne jen napoprve. */
    function priDoteku() {
      if (hralo || pamet("cdf-vivencia-zvuk") === "0") { odpoj(); return; }
      if (zvuk.paused) spust();
    }
    function odpoj() {
      document.removeEventListener("pointerdown", priDoteku, true);
      document.removeEventListener("keydown", priDoteku, true);
      document.removeEventListener("click", priDoteku, true);
    }
    document.addEventListener("pointerdown", priDoteku, true);
    document.addEventListener("keydown", priDoteku, true);
    document.addEventListener("click", priDoteku, true);

    /* Zadny pokus hned po nacteni. Prohlizec ho stejne odmitne (proto tu ten
       pokus driv byl oznaceny jako marny), ale samotne zavolani play() spusti
       stahovani nahravky, cimz obejde preload="none" - a tim se 950 kB stahlo
       i tomu, kdo hudbu nikdy nechtel. Prvni dotek ji vyzvedne stejne. */
    /* dokud hudba nezacala, tlacitko na sebe upozorni */
    window.setTimeout(function () {
      if (!hralo) tlacitka.forEach(function (b) { b.setAttribute("data-lakej", "1"); });
    }, 1200);
  })();

  /* ===============================================================
     SBĚR E-MAILŮ
     Uloží kontakt přes /api/zajem do Brevo listu. Když to neprojde,
     e-mail se schová do localStorage a zkusí se znovu, jakmile se
     vrátí signál – na festivalu je slabé připojení pravidlo, ne výjimka,
     a ztracený e-mail by nikdo nepoznal.
     =============================================================== */
  (function () {
    var form = $("#zajem-form");
    if (!form) return;
    var poleMail = $("#z-mail"), poleSouhlas = $("#z-souhlas"), poleFirma = $("#z-firma");
    var tlac = $("#z-odeslat"), hlaska = $("#z-hlaska"), hotovo = $("#z-hotovo");
    var FRONTA = "cdf-vivencia-fronta";

    function znacka() {
      try {
        var v = new URLSearchParams(location.search).get("od");
        return v ? String(v).slice(0, 32) : "";
      } catch (e) { return ""; }
    }

    function ctiFrontu() {
      try { return JSON.parse(window.localStorage.getItem(FRONTA) || "[]"); }
      catch (e) { return []; }
    }
    function zapisFrontu(f) {
      try { window.localStorage.setItem(FRONTA, JSON.stringify(f.slice(-20))); }
      catch (e) {}
    }

    function posli(d) {
      return window.fetch("/api/zajem", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(d)
      }).then(function (r) {
        return r.json().catch(function () { return {}; });
      });
    }

    /* Co leží ve frontě, zkusíme poslat znovu. Ticho: člověk už dávno odešel
       a hlásit mu úspěch nemá komu. */
    function dorovnej() {
      var f = ctiFrontu();
      if (!f.length) return;
      zapisFrontu([]);
      f.forEach(function (d) {
        posli(d).then(function (o) {
          if (!o || !o.ok) { var z = ctiFrontu(); z.push(d); zapisFrontu(z); }
        }).catch(function () {
          var z = ctiFrontu(); z.push(d); zapisFrontu(z);
        });
      });
    }
    window.addEventListener("online", dorovnej);
    dorovnej();

    function rekni(klic) {
      if (!hlaska) return;
      hlaska.hidden = false;
      hlaska.textContent = t(klic);
    }

    /* Odlozene se rika jinak nez ulozene. Tvrdit "jste na seznamu", kdyz zaznam
       jen leti do fronty, by byla lez: kdyz clovek zavre stranku a nevrati se,
       nikam se nedostane. */
    function ulozeno(odlozene) {
      form.hidden = true;
      if (hotovo) {
        hotovo.setAttribute("data-i18n", odlozene ? "zajem.odlozeno" : "zajem.hotovo");
        hotovo.textContent = t(odlozene ? "zajem.odlozeno" : "zajem.hotovo");
        hotovo.hidden = false;
        hotovo.focus();
      }
      if (window.mer) {
        window.mer("zajem_ulozen", { od: znacka() || "primo", odlozeno: !!odlozene });
      }
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var mail = (poleMail.value || "").trim();
      if (!mail || mail.indexOf("@") < 0 || !poleSouhlas.checked) {
        rekni("zajem.chyba");
        return;
      }
      if (hlaska) hlaska.hidden = true;

      var d = {
        mail: mail,
        souhlas: true,
        jazyk: jazyk,
        od: znacka(),
        firma: (poleFirma && poleFirma.value || "").trim()
      };

      var popis = tlac.textContent;
      tlac.disabled = true;

      posli(d).then(function (o) {
        if (o && o.ok) { ulozeno(false); return; }
        /* Nenastavený klíč i výpadek řešíme stejně: schovat a zkusit potom.
           Člověku se nemá co hlásit, jeho e-mail se neztratil. */
        var f = ctiFrontu(); f.push(d); zapisFrontu(f);
        ulozeno(true);
      }).catch(function () {
        var f = ctiFrontu(); f.push(d); zapisFrontu(f);
        ulozeno(true);
      }).then(function () {
        tlac.disabled = false;
        tlac.textContent = popis;
      });
    });
  })();
})();
