#!/usr/bin/env node
/**
 * query_bins.js
 * Query South Oxfordshire bin collection schedule for a given address.
 * Usage: node query_bins.js <postcode> <house_number>
 * Output: JSON with parsed collection info
 */

const { chromium } = require('playwright');

const POSTCODE = process.argv[2] || 'OX11 6AP';
const HOUSE_NUMBER = process.argv[3] || '26';

const BIN_TYPES = {
  'grey bin': '🩶 灰桶（一般垃圾）',
  'green bin': '💚 绿桶（回收物）',
  'food bin': '🍂 厨余桶',
  'garden waste bin': '🌿 花园废物桶',
  'textiles': '👕 纺织品',
  'small electrical items': '🔌 小型电器',
  'glass': '🪟 玻璃',
  'cardboard': '📦 纸板',
};

function translateBins(text) {
  let result = text.toLowerCase();
  for (const [en, zh] of Object.entries(BIN_TYPES)) {
    result = result.replace(new RegExp(en, 'gi'), zh);
  }
  return result;
}

async function getBinInfo() {
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

  await page.goto('https://eform.southoxon.gov.uk/ebase/BINZONE_DESKTOP.eb?SOVA_TAG=SOUTH&ebd=0&ebz=1_1775764044624', {
    waitUntil: 'networkidle',
    timeout: 30000
  });

  await page.locator('#PostcodeField').fill(POSTCODE);
  await page.locator('#PostcodeBtn').click();
  await page.waitForTimeout(3000);

  const addressLink = page.locator(`a:has-text("${HOUSE_NUMBER} Oak")`).first();
  await addressLink.waitFor({ timeout: 10000 });
  await addressLink.click();
  await page.waitForTimeout(4000);

  const bodyText = await page.locator('body').innerText();
  await browser.close();
  return bodyText;
}

function parseResult(text) {
  const binzoneStart = text.indexOf('BINZONE');
  const keepInTouchStart = text.indexOf('Keep in touch');
  const relevant = binzoneStart >= 0 && keepInTouchStart >= 0
    ? text.substring(binzoneStart, keepInTouchStart)
    : text.substring(0, 1000);

  const isSpecial = /your usual collection day is different/i.test(relevant);
  const lines = relevant.split('\n').filter(l => l.trim());
  const sections = [];
  let currentSection = null;
  let currentWeekType = null;

  for (const line of lines) {
    const trimmed = line.trim();
    if (/it'?s recycling week/i.test(trimmed)) currentWeekType = 'recycling';
    else if (/it'?s rubbish week/i.test(trimmed)) currentWeekType = 'rubbish';
    else if (/this week/i.test(trimmed)) currentSection = 'this';
    else if (/next week/i.test(trimmed)) currentSection = 'next';
    else if (/^(Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday)\s+\d+/i.test(trimmed)) {
      sections.push({ section: currentSection, weekType: currentWeekType, line: trimmed });
      currentWeekType = null;
    } else if (sections.length > 0 && /bin|textiles|electrical|food|garden|glass|cardboard/i.test(trimmed)) {
      sections[sections.length - 1].bins = (sections[sections.length - 1].bins || '') + ' ' + trimmed;
    }
  }

  // Build human-readable summary
  let summary = `🗑️ 垃圾收集查询结果\n📍 ${HOUSE_NUMBER} Oak Hill Lane, Didcot ${POSTCODE}\n\n`;

  if (sections.length === 0) {
    summary += '⚠️ 无法解析收集时间，请手动查询。';
  } else {
    for (const s of sections) {
      const label = s.section === 'this' ? '📅 本周' : '📅 下周';
      const weekTag = s.weekType === 'recycling' ? ' ♻️ 回收周' : s.weekType === 'rubbish' ? ' 🗑️ 垃圾周' : '';
      summary += `${label}${weekTag}：${s.line}\n`;
      if (s.bins) summary += `   ${translateBins(s.bins.trim())}\n`;
      summary += '\n';
    }
    if (isSpecial) summary += '⚠️ 注意：本周收集日期有调整，请留意！';
  }

  return { sections, isSpecial, summary };
}

(async () => {
  try {
    const raw = await getBinInfo();
    const result = parseResult(raw);
    // Print summary to stdout for the agent to read
    console.log(result.summary);
  } catch (err) {
    console.error('查询失败:', err.message);
    process.exit(1);
  }
})();
