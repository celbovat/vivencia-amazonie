/* Měření návštěvnosti přes PostHog.

   Je to jediná výjimka z pravidla, že stránka nesahá nikam ven: knihovna se
   stahuje z PostHogu. Načítá se asynchronně, takže vykreslení nezdrží, a když
   se nestáhne, stránka funguje dál, jen se nic nezměří.

   Bez cookies a bez lišty se souhlasem. PostHog místo nich počítá lidi přes
   otisk, který si spočítá na serveru. Pozor na `defaults`: bez něj knihovna
   cookieless_mode potichu ignoruje a cookies zase nasadí.

   Stejný projekt jako cesta.curadafloresta.org a pobyt.curadafloresta.org
   (Cura da Floresta web, id 203731), rozliší se doménou. */
(function () {
  var KLIC = 'phc_xqtcSuookDCgPDDGm4NQ5b4GxGPF2RpeeD79Yi4pzCRq';
  var HOST = 'https://eu.i.posthog.com';

  // Náhledová nasazení a lokální zkoušení do statistik nepatří; na druhém
  // webu z toho byla skoro polovina prvních návštěv.
  function meritelnyHost() {
    if (location.protocol === 'file:') return false;
    var h = location.hostname || '';
    if (h === 'localhost' || h === '127.0.0.1' || h === '::1') return false;
    if (/\.pages\.dev$/.test(h)) return false;
    return true;
  }

  // Značka kampaně z adresy, ať jde poznat, odkud kdo přišel: ?od=letak
  function odkud() {
    try {
      var v = new URLSearchParams(location.search).get('od');
      return v ? String(v).slice(0, 40) : null;
    } catch (e) { return null; }
  }

  if (meritelnyHost()) {
    !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture register register_once unregister getFeatureFlag isFeatureEnabled reloadFeatureFlags identify setPersonProperties group reset get_distinct_id opt_in_capturing opt_out_capturing debug".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);

    window.posthog.init(KLIC, {
      api_host: HOST,
      defaults: '2026-05-30',
      cookieless_mode: 'always',
      persistence: 'memory',
      autocapture: false,
      capture_pageview: false,
      capture_pageleave: true,   /* kvuli scrollu a spolehlivemu odeslani pri odchodu */
      disable_session_recording: true,
      person_profiles: 'identified_only',
    });

    var od = odkud();
    if (od) window.posthog.register({ od: od });
    window.posthog.capture('$pageview');
  }

  // Pošle událost, když je co. Když ne, tiše nic, ať nikdy nespadne stránka
  // kvůli měření.
  window.mer = function (udalost, vlastnosti) {
    try {
      if (window.posthog && window.posthog.capture) {
        window.posthog.capture(udalost, vlastnosti || {});
      }
    } catch (e) {}
  };

  /* --- plavba -------------------------------------------------------------
     Příjezd na lodi je to, co se na stránce nejvíc ladilo, tak ať jde poznat,
     jestli ho lidi dokoukají. Dokončení si app.js pamatuje v localStorage;
     hodnotu si přečtu hned teď, abych dokončení téhle návštěvy nespletl
     s tím, že tu někdo byl už minule. */
  var pristav = document.getElementById('pristav');
  var preskocil = false;
  var preskoc = document.getElementById('pristav-preskoc');
  if (preskoc) {
    preskoc.addEventListener('click', function () { preskocil = true; }, { once: true });
  }

  /* Spoustě lidí se plavba vůbec nepustí: vracejícímu se návštěvníkovi, při
     ?rovnou a při odkazu s kotvou. app.js to řeší sám a #pristav rovnou skryje.
     Tu podmínku tady schválně neopisuju, aby se časem nerozešla se zdrojem –
     místo toho počkám jeden tik. Do té doby app.js (je na stránce níž, takže
     běží hned po tomhle skriptu) už rozhodl, a když je přístav pořád vidět,
     plavba opravdu běží. Jinak není co měřit. */
  if (pristav && window.MutationObserver) window.setTimeout(function () {
    if (pristav.hidden) return;
    var sledujPristav = new MutationObserver(function () {
      if (!pristav.hidden) return;
      sledujPristav.disconnect();
      var doplul = false;
      try {
        doplul = window.localStorage.getItem('cdf-vivencia-doplul') === '1';
      } catch (e) {}
      if (doplul) window.mer('plavba_dokoncena');
      else window.mer('plavba_preskocena', { jak: preskocil ? 'tlacitko' : 'klavesa' });
    });
    sledujPristav.observe(pristav, { attributes: true, attributeFilter: ['hidden'] });
  }, 0);

  /* --- kam až člověk došel -----------------------------------------------
     Procento scrollu samo o sobě na takhle dlouhé stránce nic neřekne. Proto
     se hlásí i jméno sekce, ke které se člověk dostal: "došel k ceně a odešel"
     je něco, s čím jde něco udělat, "41 %" ne. Čísla v názvu jsou kvůli tomu,
     aby šly sekce v přehledu seřadit tak, jak jdou na stránce.

     Odesílá se při schování stránky, ne při unload - na mobilu unload často
     vůbec nenastane (člověk přepne appku) a událost by se ztratila. */
  var sekce = [].slice.call(document.querySelectorAll("header, section"))
    .filter(function (e) { return (" " + e.className + " ").indexOf(" band ") >= 0; });

  if (sekce.length) {
    var jmena = sekce.map(function (e, i) {
      var j = e.id || String(e.className).trim().split(/\s+/)[0];
      return (i < 9 ? "0" : "") + (i + 1) + "-" + j;
    });
    var nejdal = 0, maxProcent = 0, zacatek = Date.now(), odeslano = false, ceka = false;

    function prepocti() {
      var h = document.documentElement;
      var lze = h.scrollHeight - h.clientHeight;
      var p = lze > 0 ? Math.round(100 * (window.pageYOffset || h.scrollTop) / lze) : 100;
      if (p > maxProcent) maxProcent = Math.min(100, Math.max(0, p));
      var stred = h.clientHeight * 0.5;
      for (var i = 0; i < sekce.length; i++) {
        if (sekce[i].getBoundingClientRect().top <= stred && i > nejdal) nejdal = i;
      }
    }

    function priScrollu() {
      if (ceka) return;
      ceka = true;
      window.requestAnimationFrame(function () { ceka = false; prepocti(); });
    }
    window.addEventListener("scroll", priScrollu, { passive: true });
    window.addEventListener("resize", priScrollu, { passive: true });
    prepocti();

    function posliOdchod() {
      if (odeslano) return;
      odeslano = true;
      prepocti();
      window.mer("odchod", {
        nejdal: jmena[nejdal] || "?",
        procent: maxProcent,
        vterin: Math.round((Date.now() - zacatek) / 1000)
      });
    }
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "hidden") posliOdchod();
    });
    window.addEventListener("pagehide", posliOdchod);
  }

  /* --- trychtýř -----------------------------------------------------------
     Kolik lidí přišlo, kolik z nich chtělo jet, a kolik nakonec opravdu
     odeslalo. Bez toho nejde poznat, kde se ztrácejí. */
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a.cta');
    if (!a) return;
    if (a.hasAttribute('data-hra-cs')) {
      window.mer('hra_otevrena');
    } else if ((a.getAttribute('href') || '') === '#prihlaska') {
      window.mer('chci_jet', { misto: a.closest('.lista') ? 'lišta' : 'hlavička' });
    }
  });

  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-jazyk]');
    if (b) window.mer('jazyk_prepnut', { na: b.getAttribute('data-jazyk') });
  });

  /* Odeslání přihlášky se měří přímo v app.js, kde je vidět, jak dopadlo:
     `vysledek` je ok / posta / chyba / whatsapp, stejně jako na
     pobyt.curadafloresta.org. Tady by se dalo poznat jen tolik, že se odkrylo
     poděkování, a odeslání přes poštu by se počítalo jako úspěch. */
})();
