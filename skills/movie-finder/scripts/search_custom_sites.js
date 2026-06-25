#!/usr/bin/env node
/**
 * search_custom_sites.js
 * Search Jerry's preferred streaming sites and return verified movie links
 * Usage: node search_custom_sites.js <movie_name>
 */

const { chromium } = require('playwright');

const SITES = [
  {
    name: '欧乐影院',
    searchUrl: (q) => `https://www.olehdtv.com/index.php/vod/search.html?wd=${encodeURIComponent(q)}`,
    resultSelector: 'a[href*="/vod/detail"], a[href*="/vod/play"]',
    base: 'https://www.olehdtv.com',
  },
  {
    name: '小宝影院',
    // 搜索结果页链接是 JS 动态渲染，需等待 networkidle
    searchUrl: (q) => `https://www.xiaobaotv.com/search.html?wd=${encodeURIComponent(q)}`,
    resultSelector: 'a[href*="/vod/detail"], a[href*="/play/"], .module-item-pic a, .video-info-title a',
    base: 'https://www.xiaobaotv.com',
    waitForNetworkIdle: true,
  },
  {
    name: '卓楼影院',
    // SPA：需要模拟搜索表单提交才能跨到正确的搜索结果页
    searchUrl: (q) => `https://www.zhuoloufs.com/vod/search/${encodeURIComponent(q)}`,
    resultSelector: 'a[href*="/detail/"]',
    base: 'https://www.zhuoloufs.com',
    waitForNetworkIdle: true,
  },
];

const VIDEO_SELECTORS = [
  'video', 'iframe[src*="player"]', 'iframe[src*="embed"]',
  '.video-js', '.jw-video', '#player', '[class*="player"]',
  'div[class*="video"]', '.art-video-player',
];

async function searchSite(page, site, query) {
  try {
    const waitMode = site.waitForNetworkIdle ? 'networkidle' : 'domcontentloaded';
    await page.goto(site.searchUrl(query), { waitUntil: waitMode, timeout: 20000 });
    await page.waitForTimeout(2000);

    // Get result links and find best match by title
    const links = await page.$$(site.resultSelector);
    if (links.length === 0) return null;

    // Build list of search terms to try (split by space/punctuation)
    const aliases = Array.isArray(query) ? query : [query];
    // Each alias becomes a set of terms; also keep the full collapsed version for fuzzy match
    const termSets = aliases.map(q => {
      const terms = q.toLowerCase()
        .replace(/[·•·\-_:.()（）]/g, ' ')
        .split(/\s+/)
        .filter(t => t.length > 1);
      const collapsed = q.toLowerCase().replace(/[\s·•·\-_:.()（）]/g, ''); // e.g. "哈利波特死亡圣器"
      return { terms, collapsed };
    });

    let href = null;
    for (const link of links.slice(0, 15)) {
      const rawText = (await link.innerText().catch(() => '')).toLowerCase();
      // Collapse text too (remove all whitespace and punctuation) for fuzzy match
      const collapsedText = rawText.replace(/[\s·•·\-_:.()（）与]/g, '');
      const h = await link.getAttribute('href').catch(() => null);
      if (!h) continue;

      const matched = termSets.some(({ terms, collapsed }) => {
        // Method 1: all terms present in raw text (handles spaces between chars)
        const allTermsMatch = terms.length > 0 && terms.every(t => rawText.replace(/[\s·•·]/g, '').includes(t));
        // Method 2: collapsed query is substring of collapsed text
        const collapsedMatch = collapsed.length > 2 && collapsedText.includes(collapsed);
        return allTermsMatch || collapsedMatch;
      });
      if (matched) {
        href = h;
        break;
      }
    }

    // Strict: no match = no result (don't fallback to random link)
    if (!href) return { site: site.name, url: null, hasVideo: false, reason: 'no title match' };
    if (!href.startsWith('http')) href = site.base + href;

    // Navigate to movie page
    await page.goto(href, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(3000);

    const title = await page.title().catch(() => '');
    const bodyText = await page.locator('body').innerText().catch(() => '');
    const blocked = /not available|geo.?blocked|content unavailable|currently unavailable/i.test(bodyText);

    // Check for video player
    let hasVideo = false;
    for (const sel of VIDEO_SELECTORS) {
      const el = await page.$(sel).catch(() => null);
      if (el) { hasVideo = true; break; }
    }

    // Try to find a play link if no direct player
    if (!hasVideo) {
      const playLink = await page.$('a[href*="/play/"], .play-btn a, .module-play a').catch(() => null);
      if (playLink) {
        let playHref = await playLink.getAttribute('href').catch(() => null);
        if (playHref) {
          if (!playHref.startsWith('http')) playHref = site.base + playHref;
          await page.goto(playHref, { waitUntil: 'domcontentloaded', timeout: 15000 });
          await page.waitForTimeout(3000);
          for (const sel of VIDEO_SELECTORS) {
            const el = await page.$(sel).catch(() => null);
            if (el) { hasVideo = true; href = playHref; break; }
          }
        }
      }
    }

    return {
      site: site.name,
      url: href,
      title: title.substring(0, 80),
      hasVideo,
      geoBlocked: blocked,
    };
  } catch (e) {
    return { site: site.name, url: null, hasVideo: false, error: e.message.substring(0, 80) };
  }
}

(async () => {
  const query = process.argv.slice(2).join(' ');
  if (!query) {
    console.error('Usage: node search_custom_sites.js <movie_name>');
    process.exit(1);
  }

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-blink-features=AutomationControlled'],
  });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    locale: 'zh-CN',
    extraHTTPHeaders: { 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8' },
  });
  const page = await context.newPage();
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  });

  const results = [];
  for (const site of SITES) {
    process.stderr.write(`搜索 ${site.name}...\n`);
    const result = await searchSite(page, site, query);
    if (result) results.push(result);
  }

  await browser.close();

  // Output
  const valid = results.filter(r => r.hasVideo && !r.geoBlocked && r.url);
  const invalid = results.filter(r => !r.hasVideo || r.geoBlocked || !r.url);

  console.log('\n✅ 有效链接:');
  for (const r of valid) {
    console.log(`  [${r.site}] ${r.url}`);
  }

  if (invalid.length > 0) {
    console.log('\n❌ 无效/未找到:');
    for (const r of invalid) {
      console.log(`  [${r.site}] ${r.error || (r.geoBlocked ? 'geo-blocked' : '无播放器')}`);
    }
  }

  // JSON for programmatic use
  process.stdout.write('\nJSON:\n' + JSON.stringify(results, null, 2) + '\n');
})();
