#!/usr/bin/env node
/**
 * bin_reminder.js
 * 每周四运行，查询 26 Oak Hill Lane OX11 6AP 的垃圾收集安排
 * 通过 OpenClaw 发送 Telegram 通知给 Jerry
 */

const { chromium } = require('playwright');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const POSTCODE = 'OX11 6AP';
const HOUSE_NUMBER = '26';
const TELEGRAM_TARGET = '8791954608';

// 垃圾桶类型说明
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
      currentWeekType = null; // reset after attaching
    } else if (sections.length > 0 && /bin|textiles|electrical|food|garden|glass|cardboard/i.test(trimmed)) {
      sections[sections.length - 1].bins = (sections[sections.length - 1].bins || '') + ' ' + trimmed;
    }
  }

  return { isSpecial, sections };
}

function buildMessage(parsed) {
  const { isSpecial, sections } = parsed;

  let msg = `🗑️ 每周垃圾收集提醒\n`;
  msg += `📍 ${HOUSE_NUMBER} Oak Hill Lane, Didcot ${POSTCODE}\n\n`;

  if (sections.length === 0) {
    msg += `⚠️ 无法解析收集时间，请手动查询。`;
    return msg;
  }

  const now = new Date();
  for (const s of sections) {
    // Extract date from line like "Friday 1 May -"
    const dateMatch = s.line.match(/(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d{1,2})\s+(\w+)/i);
    let label = s.section === 'this' ? '📅 本周' : '📅 下周';
    if (dateMatch) {
      const day = parseInt(dateMatch[2]);
      const monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];
      const month = monthNames.indexOf(dateMatch[3]);
      if (month >= 0) {
        const collectDate = new Date(now.getFullYear(), month, day);
        const diffDays = Math.ceil((collectDate - now) / (1000 * 60 * 60 * 24));
        if (diffDays >= 0 && diffDays <= 7) {
          label = '📅 本周';
        } else if (diffDays > 7 && diffDays <= 14) {
          label = '📅 下周';
        }
      }
    }
    const weekTag = s.weekType === 'recycling' ? ' ♻️ 回收周' : s.weekType === 'rubbish' ? ' 🗑️ 垃圾周' : '';
    msg += `${label}${weekTag}：${s.line}\n`;
    if (s.bins) {
      msg += `   ${translateBins(s.bins.trim())}\n`;
    }
    msg += '\n';
  }

  if (isSpecial) msg += `⚠️ 注意：本周收集日期有调整，请留意！`;

  return msg.trim();
}

function sendTelegram(message) {
  // 写入临时文件避免 shell 转义问题
  const fs = require('fs');
  const tmpFile = '/tmp/bin_msg.txt';
  fs.writeFileSync(tmpFile, message, 'utf8');
  try {
    execSync(`PATH=/home/ubuntu/.nvm/versions/node/v24.14.1/bin:$PATH /home/ubuntu/.nvm/versions/node/v24.14.1/bin/openclaw message send --channel telegram --target ${TELEGRAM_TARGET} --message "$(cat ${tmpFile})"`, { stdio: 'inherit', shell: '/bin/bash' });
    console.log('消息已发送');
  } catch (e) {
    console.error('发送失败:', e.message);
    process.exit(1);
  }
}

function buildShortReminder(parsed) {
  const { sections } = parsed;
  if (!sections.length) return '🗑️ 查询失败，请手动查看垃圾收集安排';

  // 找最近一次收集（距今天最近且 >= 0天的）
  const now = new Date();
  const monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  let best = null;
  let bestDiff = Infinity;
  for (const s of sections) {
    const dateMatch = s.line.match(/(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d{1,2})\s+(\w+)/i);
    if (dateMatch) {
      const day = parseInt(dateMatch[2]);
      const month = monthNames.indexOf(dateMatch[3]);
      if (month >= 0) {
        const collectDate = new Date(now.getFullYear(), month, day);
        const diffDays = Math.ceil((collectDate - now) / (1000 * 60 * 60 * 24));
        if (diffDays >= 0 && diffDays < bestDiff) {
          bestDiff = diffDays;
          best = s;
        }
      }
    }
  }
  if (!best) best = sections[0];

  const weekTag = best.weekType === 'recycling' ? '♻️ 回收周' : best.weekType === 'rubbish' ? '🗑️ 垃圾周' : '';
  const bins = best.bins ? translateBins(best.bins.trim()) : '';
  return `🗑️ 别忘了把桶推出去！${weekTag}：${bins || best.line}`;
}

(async () => {
  try {
    const mode = process.argv[2];
    console.log('开始查询垃圾收集信息...');
    const raw = await getBinInfo();
    const parsed = parseResult(raw);
    console.log('\n生成消息:\n', raw.substring(0, 200));

    if (mode === '--short') {
      const message = buildShortReminder(parsed);
      console.log('简短提醒:', message);
      sendTelegram(message);
    } else {
      const message = buildMessage(parsed);
      console.log('\n详细消息:\n', message);
      // 保存缓存
      const cachePath = path.join(__dirname, '..', 'skills', 'garden-tracker', 'data', 'bin_cache.txt');
      try { fs.writeFileSync(cachePath, message, 'utf8'); console.log('缓存已保存'); } catch(e) { console.log('缓存保存失败:', e.message); }
      sendTelegram(message);
    }
  } catch (err) {
    console.error('查询出错:', err.message);
    process.exit(1);
  }
})();
