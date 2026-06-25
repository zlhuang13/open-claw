const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-blink-features=AutomationControlled']
  });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    locale: 'en-GB',
    extraHTTPHeaders: { 'Accept-Language': 'en-GB,en;q=0.9' }
  });
  const page = await context.newPage();
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  });

  const postcode = process.argv[2] || 'OX11 6AP';
  const houseNumber = process.argv[3] || '26';
  console.log(`查询: ${houseNumber} Oak Hill Lane, ${postcode}`);

  await page.goto('https://eform.southoxon.gov.uk/ebase/BINZONE_DESKTOP.eb?SOVA_TAG=SOUTH&ebd=0&ebz=1_1775764044624', {
    waitUntil: 'networkidle',
    timeout: 30000
  });

  // 输入邮编
  await page.locator('#PostcodeField').fill(postcode);
  await page.locator('#PostcodeBtn').click();
  console.log('搜索中...');
  await page.waitForTimeout(3000);

  // 点击对应门牌号的链接
  const addressLink = page.locator(`a:has-text("${houseNumber} Oak")`).first();
  await addressLink.waitFor({ timeout: 10000 });
  const linkText = await addressLink.innerText();
  console.log(`点击地址: ${linkText.trim()}`);
  await addressLink.click();

  await page.waitForTimeout(4000);
  await page.screenshot({ path: '/home/ubuntu/.openclaw/workspace/bin_result.png', fullPage: true });

  const finalText = await page.locator('body').innerText();
  console.log('\n========= 收集结果 =========');
  console.log(finalText.substring(0, 4000));

  await browser.close();
})();
