#!/usr/bin/env node
/**
 * verify_links.js - Check if URLs contain a working video player
 * Usage: node verify_links.js <url1> [url2] [url3] ...
 * Output: JSON array with { url, hasVideo, title, status }
 */

const { chromium } = require('playwright');

// Known video player selectors across streaming sites
const VIDEO_SELECTORS = [
  'video',
  'iframe[src*="player"]',
  'iframe[src*="embed"]',
  'iframe[src*="video"]',
  '.video-js',
  '.jw-video',
  '.plyr',
  '#player',
  '.player-container',
  '[class*="player"]',
  '[id*="player"]',
  'div[class*="video"]',
];

async function checkUrl(page, url) {
  try {
    const resp = await page.goto(url, {
      waitUntil: 'domcontentloaded',
      timeout: 20000,
    });

    const status = resp ? resp.status() : 0;
    if (status === 403 || status === 404 || status === 451) {
      return { url, hasVideo: false, title: null, status, reason: `HTTP ${status}` };
    }

    const title = await page.title().catch(() => '');

    // Wait a bit for JS to render
    await page.waitForTimeout(3000);

    // Check for video player elements
    let hasVideo = false;
    let matchedSelector = null;
    for (const sel of VIDEO_SELECTORS) {
      const el = await page.$(sel).catch(() => null);
      if (el) {
        hasVideo = true;
        matchedSelector = sel;
        break;
      }
    }

    // Also check page text for "geo" / "not available" signals
    const bodyText = await page.locator('body').innerText().catch(() => '');
    const blocked = /not available in your (country|region)|geo.?blocked|vpn required|access denied|content unavailable|not available in|currently unavailable|available in your area|region restricted|not supported in/i.test(bodyText);

    return {
      url,
      hasVideo: hasVideo && !blocked,
      title: title.substring(0, 80),
      status,
      matchedSelector,
      geoBlocked: blocked,
      reason: blocked ? 'geo-blocked' : hasVideo ? 'video player found' : 'no video player detected',
    };
  } catch (e) {
    return { url, hasVideo: false, title: null, status: 0, reason: e.message.substring(0, 100) };
  }
}

(async () => {
  const urls = process.argv.slice(2);
  if (urls.length === 0) {
    console.error('Usage: node verify_links.js <url1> [url2] ...');
    process.exit(1);
  }

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-blink-features=AutomationControlled'],
  });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    locale: 'en-GB',
    extraHTTPHeaders: { 'Accept-Language': 'en-GB,en;q=0.9' },
  });
  const page = await context.newPage();
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  });

  const results = [];
  for (const url of urls) {
    process.stderr.write(`Checking: ${url}\n`);
    const result = await checkUrl(page, url);
    results.push(result);
  }

  await browser.close();
  console.log(JSON.stringify(results, null, 2));
})();
