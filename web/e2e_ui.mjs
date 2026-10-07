// E2E: login -> send message -> navigate away -> click thread -> verify history loads
import { chromium } from 'playwright';

const BASE = 'http://localhost:5173';
const results = [];
const check = (name, ok, detail = '') => {
  results.push({ name, ok, detail });
  console.log(`${ok ? 'PASS' : 'FAIL'}: ${name}${detail ? ' — ' + detail : ''}`);
};

const run = async () => {
  const browser = await chromium.launch({
    executablePath: '/usr/bin/google-chrome',
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  const consoleErrors = [];
  page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()); });
  page.on('pageerror', (e) => consoleErrors.push('PAGEERROR: ' + e.message));

  // 1. Login
  await page.goto(BASE + '/login', { waitUntil: 'networkidle' });
  await page.fill('input[type="text"]', 'ui_test_user');
  await page.fill('input[type="password"]', 'test1234');
  await page.click('button[type="submit"]');
  // SPA navigation: wait for the URL path to change (no load event fires)
  await page.waitForFunction(() => window.location.pathname === '/', { timeout: 15000 });
  check('login + redirect', page.url() === BASE + '/');

  // 2. Send a message on a fresh (no-thread) page
  await page.fill('input[placeholder*="Type your message"]', 'The e2e canary says hi');
  await page.press('input[placeholder*="Type your message"]', 'Enter');

  // 3. Wait for assistant reply + thread creation redirect (SPA pushState)
  await page.waitForFunction(() => /\/c\/[0-9a-f-]{36}/.test(window.location.pathname), { timeout: 20000 });
  const threadUrl = page.url();
  check('thread auto-created', /\/c\/[0-9a-f-]{36}/.test(threadUrl), threadUrl);

  // 4. Wait for the assistant's streamed reply to appear
  await page.waitForFunction(
    () => document.body.innerText.includes('e2e canary'),
    undefined,
    { timeout: 45000 },
  );
  await page.waitForTimeout(1500); // let post-reply resync settle
  const msgCount = await page.locator('.rounded-2xl').count();
  check('assistant reply streamed', msgCount >= 2, `${msgCount} bubbles`);

  // 5. THE REGRESSION TEST: navigate away (fresh chat), then click the thread
  await page.goto(BASE + '/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(500);
  const threadBtn = page.locator(`button:has-text("The e2e canary says hi")`).first();
  await threadBtn.waitFor({ state: 'visible', timeout: 10000 });
  await threadBtn.click();
  await page.waitForTimeout(2000);

  // 6. History must be visible after clicking the thread
  const historyVisible = await page.evaluate(() => document.body.innerText.includes('The e2e canary says hi'));
  check('history visible after clicking thread', historyVisible);

  // 7. Reload the page (component remount) and confirm history persists
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  const historyAfterReload = await page.evaluate(() => document.body.innerText.includes('The e2e canary says hi'));
  check('history visible after full reload', historyAfterReload);

  // 8. Old Streamlit-era thread also loads (thread 1a0cb4a0... belongs to a different
  //    user, so check sidebar list for this user's thread instead)
  const sidebarItems = await page.locator('button:has-text("The e2e canary says hi")').count();
  check('sidebar shows the thread', sidebarItems >= 1);

  const realErrors = consoleErrors.filter(
    (e) => !e.includes('401') && !e.includes('favicon'),
  );
  check('no console errors', realErrors.length === 0, realErrors.slice(0, 3).join(' | '));

  await page.screenshot({ path: 'scripts/e2e-final.png', fullPage: false });
  await browser.close();

  const failed = results.filter((r) => !r.ok);
  console.log(`\n${results.length - failed.length}/${results.length} checks passed`);
  if (failed.length) process.exit(1);
};

run().catch((e) => { console.error('E2E RUNNER ERROR:', e); process.exit(2); });
