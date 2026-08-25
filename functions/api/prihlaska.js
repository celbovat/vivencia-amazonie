// Cloudflare Pages Function: přihláška z formuláře odejde rovnou jako e-mail
// na hello@curadafloresta.org, aby si člověk nemusel otevírat vlastní poštu.
//
// Posílá se přes Brevo, stejně jako na pobyt.curadafloresta.org
// (functions/api/prihlaska.js) a cesta.curadafloresta.org (lead.js), jen bez
// ukládání do seznamu kontaktů: tady jde o jednu zprávu s obsahem formuláře,
// ne o sběr leadů.
//
// Chce proměnnou BREVO_API_KEY v nastavení Pages projektu. Dokud není,
// funkce vrátí { configured: false } a stránka se vrátí k mailto odkazu,
// takže se přihláška neztratí ani při špatném nastavení.

// Odesílatel musí být v Brevu ověřená adresa, jinak Brevo zprávu odmítne.
// Odpovídá se na adresu přihlášeného, ta se nastavuje jako replyTo.
const ODESILATEL = { email: 'hello@curadafloresta.org', name: 'Přihláška z pozvánky' };
const KOMU = { email: 'hello@curadafloresta.org', name: 'Cura da Floresta' };
const PREDMET = 'Přihláška: Amazonie 27. 12. 2026 – 8. 1. 2027';

const orez = (v, max) => String(v == null ? '' : v).trim().slice(0, max);

const escapeHtml = (s) =>
  String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');

// Vrátí název vadného pole, nebo null když je vše v pořádku. Povinné je jméno
// a e-mail, na ten se odepisuje. Telefon a vzkaz jsou nepovinné.
export function zkontroluj(telo) {
  if (!telo || typeof telo !== 'object') return 'invalid';
  if (!orez(telo.jmeno, 120)) return 'jmeno';
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(orez(telo.mail, 200))) return 'mail';
  return null;
}

// Text i HTML zprávy z vyplněných polí. Prázdné řádky se vynechávají, ať
// v e-mailu nesvítí „Telefon:" bez čísla.
//
// Zpráva je česky i pro anglickou přihlášku, protože ji čtou pořadatelé.
// Jazyk formuláře se ale připisuje: podle něj se pozná, čím odepsat.
export function sestavZpravu(telo) {
  const jmeno = orez(telo.jmeno, 120);
  const mail = orez(telo.mail, 200);
  const telefon = orez(telo.telefon, 60);
  const vzkaz = orez(telo.vzkaz, 4000);
  const anglicky = orez(telo.jazyk, 5) === 'en';

  const radky = [['Jméno', jmeno], ['E-mail', mail]];
  if (telefon) radky.push(['Telefon', telefon]);
  radky.push(['Hãpaya / Huni Meka', telo.hloubka ? 'ano' : 'ne']);
  radky.push(['Přihláška vyplněna', anglicky ? 'anglicky' : 'česky']);

  const text = radky.map(([k, v]) => `${k}: ${v}`).join('\n')
    + (vzkaz ? `\n\nVzkaz:\n${vzkaz}` : '');

  const html = `<!DOCTYPE html>
<html lang="cs">
<head><meta charset="utf-8"></head>
<body style="margin:0; padding:24px; background:#FFF2D9; color:#1F3C36; font-family:Helvetica,Arial,sans-serif; line-height:1.6;">
  <div style="max-width:560px; margin:0 auto;">
    <p style="font-size:13px; letter-spacing:0.14em; text-transform:uppercase; color:#ED6E2C; margin:0 0 16px;">Přihláška na výpravu do Amazonie</p>
    <table cellpadding="0" cellspacing="0" style="border-collapse:collapse; font-size:16px;">
${radky.map(([k, v]) => `      <tr><td style="padding:4px 16px 4px 0; color:#528E82;">${escapeHtml(k)}</td><td style="padding:4px 0; font-weight:bold;">${escapeHtml(v)}</td></tr>`).join('\n')}
    </table>
${vzkaz ? `    <p style="margin:20px 0 0; color:#528E82;">Vzkaz</p>\n    <p style="margin:4px 0 0; white-space:pre-wrap;">${escapeHtml(vzkaz)}</p>` : ''}
    <p style="font-size:13px; color:#528E82; margin:24px 0 0;">Odesláno z journey.curadafloresta.org. Odpověď půjde rovnou přihlášenému.</p>
  </div>
</body>
</html>`;

  return { textContent: text, htmlContent: html, jmeno, mail };
}

export async function onRequestPost({ request, env }) {
  const json = (obj, status = 200) =>
    new Response(JSON.stringify(obj), {
      status,
      headers: { 'Content-Type': 'application/json' },
    });

  // Klíč nenastavený → stránka ukáže mailto fallback a přihláška se neztratí.
  // Pozor i na prázdný řetězec: `wrangler pages secret put` uloží i prázdné
  // zadání, protože při psaní nic nevypisuje a nevložený klíč se nepozná.
  if (!env.BREVO_API_KEY) return json({ configured: false });

  let telo;
  try { telo = await request.json(); } catch { return json({ error: 'bad-json' }, 400); }

  // Honeypot: pole, které člověk nevidí a nevyplní. Botovi odpovíme „hotovo".
  if (orez(telo.firma, 200)) return json({ ok: true });

  const vadne = zkontroluj(telo);
  if (vadne) return json({ error: vadne }, 400);

  const { textContent, htmlContent, jmeno, mail } = sestavZpravu(telo);

  let res;
  try {
    res = await fetch('https://api.brevo.com/v3/smtp/email', {
      method: 'POST',
      headers: {
        'api-key': env.BREVO_API_KEY,
        'Content-Type': 'application/json',
        accept: 'application/json',
      },
      body: JSON.stringify({
        sender: ODESILATEL,
        to: [KOMU],
        replyTo: { email: mail, name: jmeno },
        subject: `${PREDMET}: ${jmeno}`,
        textContent,
        htmlContent,
        tags: ['prihlaska-amazonie'],
      }),
    });
  } catch {
    return json({ error: 'network' }, 502);
  }

  // fetch nevyhodí chybu na 4xx/5xx, tak se to musí hlídat ručně, jinak by
  // formulář hlásil úspěch i když Brevo zprávu nepřijalo.
  if (!res.ok) {
    let detail = '';
    try { detail = (await res.text()).slice(0, 300); } catch {}
    console.error(`Brevo odmítlo přihlášku: ${res.status} ${detail}`);
    return json({ error: 'upstream' }, 502);
  }

  return json({ ok: true });
}
