// E2E : widget V2 avec loven-booking.js patché (injecté), booking-create intercepté (aucune réservation créée).
// Usage : node e2e_consentement_v2.js <chemin js patché> <handle> <cocher:0|1>
const { chromium } = require('playwright');
const [, , JS, HANDLE, COCHER] = process.argv;

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  let corps = null;
  await p.route(/loven-booking\.js/, (r) => r.fulfill({ path: JS, contentType: 'application/javascript' }));
  await p.route(/\/booking-create/, async (r) => {
    corps = JSON.parse(r.request().postData());
    await r.fulfill({ status: 500, contentType: 'application/json', body: '{"error":"e2e"}' });
  });
  await p.goto(`https://lovenspa.fr/products/${HANDLE}`, { waitUntil: 'domcontentloaded' });
  await p.waitForSelector('[data-act="calendar"]', { timeout: 30000 });
  await p.click('[data-act="calendar"]');
  const libre = '[data-act="day"]:not([disabled]):not([aria-disabled])';
  await p.waitForSelector(libre, { timeout: 30000 });
  for (let essai = 0; essai < 4 && !(await p.$('[data-act="book"]:not([disabled])')); essai++) {
    const jours = await p.$$(libre);
    if (jours.length >= 2) {
      await jours[0].click();
      await p.waitForTimeout(400);
      const j2 = await p.$$(libre);
      await j2[1].click();
      await p.waitForTimeout(1500);
    }
    if (!(await p.$('[data-act="book"]:not([disabled])'))) {
      const n = await p.$('[data-act="next"]');
      if (n) await n.click();
      await p.waitForTimeout(800);
    }
  }
  await p.click('[data-act="book"]:not([disabled])');
  await p.waitForSelector('#lb-marketing-optout', { state: 'attached', timeout: 15000 });
  const etatInitial = await p.$eval('#lb-marketing-optout', (e) => e.checked);
  const texte = await p.$eval('.lb-marketing', (e) => e.innerText);
  await p.fill('#lb-first', 'Test');
  await p.fill('#lb-last', 'Recette');
  await p.fill('#lb-email', 'test-e2e+widget@lovenspa.fr');
  await p.fill('#lb-phone', '0600000000');
  if (COCHER === '1') await p.click('label:has(#lb-marketing-optout)');
  await p.click('[data-lb-submit]');
  await p.waitForSelector('#lb-street', { timeout: 15000 });
  await p.fill('#lb-street', '1 rue du Test');
  await p.fill('#lb-zip', '75001');
  await p.fill('#lb-city', 'Paris');
  for (const c of await p.$$('[data-lb-consent]')) await c.evaluate((e) => e.closest('label').click());
  await p.click('[data-lb-submit]:not([disabled])', { timeout: 15000 });
  for (let i = 0; i < 30 && !corps; i++) await p.waitForTimeout(500);
  console.log(JSON.stringify({
    cocher: COCHER, etatInitial, texte,
    consent_text_version: corps && corps.consent_text_version,
    marketing_opt_out: corps && corps.marketing_opt_out,
    marketing_consent_legacy: corps && corps.marketing_consent,
  }));
  await b.close();
})().catch((e) => { console.error('ECHEC', e.message); process.exit(1); });
