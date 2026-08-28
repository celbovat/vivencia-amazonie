// Cloudflare Pages Function: „nech nám e-mail" z pozvánky.
//
// Uloží kontakt do Brevo listu „Amazonie 2026/27 (journey)" a pošle uvítací
// e-mail. Stejná stavba jako functions/api/lead.js na cesta.curadafloresta.org,
// jen bez kvízu a bez zvířat - tady jde o jeden kontakt a jednu zprávu.
//
// Od functions/api/prihlaska.js se liší účelem: přihláška je zpráva pořadatelům
// o konkrétním člověku, tohle je zápis do seznamu, kterému se pak píše.
//
// Chce BREVO_API_KEY v nastavení Pages projektu; BREVO_LIST_ID je nepovinné
// (bez něj se použije list 4). Dokud klíč není, vrací { configured: false }
// a stránka to řekne narovinu, místo aby předstírala, že se uložilo.

const ODESILATEL = { email: 'hello@curadafloresta.org', name: 'Cura da Floresta' };
const LIST_ZALOHA = 4;
const ADRESA = 'https://journey.curadafloresta.org/';

const orez = (v, max) => String(v == null ? '' : v).trim().slice(0, max);

const escapeHtml = (s) =>
  String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');

// Vrátí název vadného pole, nebo null. E-mail je povinný, jméno ne - každé
// pole navíc stojí konverzi, a bez jména se dá napsat taky.
// Souhlas je povinný: bez něj se kontakt nikam neukládá.
export function zkontroluj(telo) {
  if (!telo || typeof telo !== 'object') return 'invalid';
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(orez(telo.mail, 200))) return 'mail';
  if (telo.souhlas !== true) return 'souhlas';
  return null;
}

// Značka odkud člověk přišel. Bere se z ?od= v adrese, takže QR na letáku
// (?od=letak) a stánek (?od=festival) jdou v Brevu rozlišit stejným filtrem
// SOURCE, jaký už používá losovani-festival.html.
export function zdroj(telo) {
  const od = orez(telo.od, 32).toLowerCase().replace(/[^a-z0-9_-]/g, '');
  return od || 'journey';
}

export function kontakt(telo, listId, kdy) {
  return {
    email: orez(telo.mail, 200).toLowerCase(),
    attributes: {
      JMENO: orez(telo.jmeno, 80),
      SOURCE: zdroj(telo),
      CONSENT_AT: kdy,
    },
    listIds: [Number(listId)],
    updateEnabled: true,
  };
}

// Uvítací e-mail. Skládá se v kódu, ne ze šablony v Brevu, aby ho řídil
// git push - stejně jako to dělá cesta.curadafloresta.org.
export function uvitaci(jmeno, anglicky) {
  const osloveni = jmeno ? (anglicky ? `Hi ${jmeno},` : `Ahoj ${jmeno},`) : (anglicky ? 'Hi,' : 'Ahoj,');
  const predmet = anglicky
    ? 'You are on the list - New Year in the Amazon'
    : 'Jsi na seznamu – Nový rok v Amazonii';
  const radky = anglicky ? [
    'thank you for leaving us your e-mail.',
    'We will write when there is something worth writing about: when the programme firms up, '
      + 'how many places are left, and what the journey will cost.',
    'No newsletters, no marketing. You can unsubscribe from any e-mail with one click.',
  ] : [
    'díky, že jsi nám nechal(a) e-mail.',
    'Ozveme se, až bude o čem psát: až se ustálí program, kolik zbývá míst a co cesta stojí.',
    'Žádné newslettery, žádný marketing. Odhlásit se dá z každého e-mailu jedním kliknutím.',
  ];
  const odkaz = anglicky ? 'The invitation' : 'Pozvánka';

  const htmlContent = `<!DOCTYPE html>
<html lang="${anglicky ? 'en' : 'cs'}">
<head><meta charset="utf-8"></head>
<body style="margin:0; padding:24px; background:#FFF2D9; color:#1F3C36; font-family:Helvetica,Arial,sans-serif; line-height:1.6;">
  <div style="max-width:560px; margin:0 auto;">
    <p style="font-size:13px; letter-spacing:0.14em; text-transform:uppercase; color:#ED6E2C; margin:0 0 16px;">Cura da Floresta</p>
    <p style="margin:0 0 12px;">${escapeHtml(osloveni)}</p>
${radky.map((r) => `    <p style="margin:0 0 12px;">${escapeHtml(r)}</p>`).join('\n')}
    <p style="margin:20px 0 0;"><a href="${ADRESA}" style="color:#ED6E2C;">${odkaz} &rarr;</a></p>
  </div>
</body>
</html>`;

  return { subject: predmet, htmlContent,
           textContent: `${osloveni}\n\n${radky.join('\n\n')}\n\n${ADRESA}` };
}

export async function onRequestPost({ request, env }) {
  const json = (obj, status = 200) =>
    new Response(JSON.stringify(obj), {
      status, headers: { 'Content-Type': 'application/json' },
    });

  if (!env.BREVO_API_KEY) return json({ configured: false });

  let telo;
  try { telo = await request.json(); } catch { return json({ error: 'bad-json' }, 400); }

  // Past na roboty: pole, které člověk nevidí. Botovi odpovíme „hotovo".
  if (orez(telo.firma, 200)) return json({ ok: true });

  const vadne = zkontroluj(telo);
  if (vadne) return json({ error: vadne }, 400);

  const telo_kontaktu = kontakt(telo, env.BREVO_LIST_ID || LIST_ZALOHA,
                                new Date().toISOString());

  let res;
  try {
    res = await fetch('https://api.brevo.com/v3/contacts', {
      method: 'POST',
      headers: {
        'api-key': env.BREVO_API_KEY,
        'Content-Type': 'application/json',
        accept: 'application/json',
      },
      body: JSON.stringify(telo_kontaktu),
    });
  } catch {
    return json({ error: 'network' }, 502);
  }

  // 201 = novy kontakt, 204 = existujici se aktualizoval. Brevo vraci 400
  // s kodem duplicate_parameter, kdyz uz kontakt je - to neni chyba.
  let novy = res.status === 201;
  if (!res.ok && res.status !== 204) {
    let detail = '';
    try { detail = await res.text(); } catch {}
    if (!detail.includes('duplicate_parameter')) {
      console.error(`Brevo odmítlo kontakt: ${res.status} ${detail.slice(0, 300)}`);
      return json({ error: 'upstream' }, 502);
    }
    novy = false;
  }

  // Uvitaci e-mail jen novemu kontaktu, at ho ten, kdo se prihlasi podruhe,
  // nedostane znovu. Posila se best-effort: kdyz neodejde, kontakt uz ulozeny
  // je a clovek se o tom nema proc dozvidat.
  if (novy) {
    const zprava = uvitaci(orez(telo.jmeno, 80), orez(telo.jazyk, 5) === 'en');
    try {
      await fetch('https://api.brevo.com/v3/smtp/email', {
        method: 'POST',
        headers: {
          'api-key': env.BREVO_API_KEY,
          'Content-Type': 'application/json',
          accept: 'application/json',
        },
        body: JSON.stringify({
          sender: ODESILATEL,
          to: [{ email: telo_kontaktu.email, name: telo_kontaktu.attributes.JMENO || undefined }],
          subject: zprava.subject,
          htmlContent: zprava.htmlContent,
          textContent: zprava.textContent,
          tags: ['uvitaci', `zdroj:${telo_kontaktu.attributes.SOURCE}`],
        }),
      });
    } catch { /* kontakt je ulozeny, to je to hlavni */ }
  }

  return json({ ok: true, novy });
}
