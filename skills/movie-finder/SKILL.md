---
name: movie-finder
description: Find free movie streaming links and torrent magnet links. Use when Jerry or Hannah asks to find a movie, watch a film online for free, find a torrent, find the highest quality source for a movie, or any request like "帮我找电影", "找片源", "找这个电影的免费链接", "有没有[电影名]", "哪里可以看[电影名]", "[电影名]在哪看", "我想看[电影名]", "find movie", "watch [movie name] free", "torrent for [movie]", "do you have [movie]", "where can I watch [movie]".
---

# Movie Finder

> ⚠️ **MANDATORY**: For EVERY movie search request, you MUST run `search_custom_sites.js` first (Step 2). Do NOT skip to web_search. Do NOT use web_search as the first step. The script is the primary search method.

## Purpose

Find free streaming links and torrents for a movie using real-time web search.

## When to Use

- User asks where to watch a movie
- User asks for 片源, torrent, 在线观看, or free streaming
- User names a movie and clearly wants a source

## Workflow

### Step 1: Expand the title

Before searching, resolve the user's input to:
- Primary Chinese title (most descriptive, e.g. "哈利波特与凤凰社")
- English title (e.g. "Harry Potter and the Order of the Phoenix")
- Common aliases (e.g. "哈利波特 凤凰社", "哈利波甩5")

Examples:
- 战狼2 → Wolf Warrior 2 (2017)
- 盗梦空间 → Inception (2010)
- 流浪地球 → The Wandering Earth (2019)
- 哈利波甩7 → 哈利波特与死亡圣器 (2011)

### Step 2: Search Jerry's preferred sites (ALWAYS do this first)

This is **mandatory** for every movie search. Call the script with the primary Chinese title:

```bash
node /home/ubuntu/.openclaw/workspace/skills/movie-finder/scripts/search_custom_sites.js "主标题"
```

If 0 results on any site, retry once with the English title or alternate alias. After 2 attempts per site, report not found — do not guess.

Sites searched:
- **欧乐影院** (olehdtv.com) — 海外华人平台，高清
- **小宝影院** (xiaobaotv.com) — 国语电影全
- **卓楼影院** (zhuoloufs.com) — SPA站，蓝光资源多

### Step 3: Check Netflix first (priority)

Before searching free sites, check if the movie is on Netflix UK:

```
web_search: "[movie name] Netflix UK" OR "[movie name] site:netflix.com"
```

If Netflix has it, return the Netflix link immediately and skip free site search:

```
✅ Netflix 上有！（你们有会员）
🎬 [Movie Title]
🔗 https://www.netflix.com/title/...
```

Only continue to free sites if Netflix does NOT have it.

### Step 4: Search for additional streaming links (if needed)

Run **two parallel searches** — one in English, one in Chinese:

**English:**
```
"[English title] [year] watch online free 1080p"
"[English title] free full movie HD streaming"
```

**Chinese (for Chinese movies especially):**
```
"[中文片名] 免费在线观看 1080p"
"[中文片名] 高清免费播放"
"[中文片名] 在线播放 全集"
```

For Chinese movies, also check:
- iqiyi.com, youku.com, bilibili.com (may have free with ads)
- dytt8.net, dygang.cc (download sites)
- xunlei.com search

For English movies, filter for:
- soap2day, fmovies, lookmovie2, 123movies, gomovies, yesmovies, solarmovie, putlocker

Rank by quality indicators in URL/title (4K > 1080p > 720p > unknown).

### Step 3: Search for torrents

Search with **both English and Chinese titles**:

```
"[English title] [year] torrent 2160p OR 1080p magnet site:1337x.to OR site:thepiratebay.org"
"[中文片名] [year] 1080p torrent magnet 种子"
```

Also try fetching the 1337x search page directly:
```
https://www.1337xxx.to/search/[movie+name]/1/
```

Extract magnet links or page URLs. Prefer results with high seeder counts.

### Step 5: Verify links have working video players

After collecting candidate URLs, run the verifier script:

```bash
node skills/movie-finder/scripts/verify_links.js <url1> <url2> ...
```

Only include links where `hasVideo: true` and `geoBlocked: false` in the final results.
Discard any link where `hasVideo: false` or `reason` indicates a block/error.

### Step 6: Format and return results

Return both sections clearly:

```
🎬 [Movie Title] ([Year])

📺 在线播放链接：
1. [SITE] [quality] - [url]
2. ...

🧲 Torrent 磁力链接：
1. [quality] [size] [seeders]s - magnet:?xt=...
2. ...

⚠️ 提示：流媒体站建议用 uBlock Origin 屏蔽广告
```

## Notes

- Always return the highest quality options first (4K > 1080p > 720p)
- If streaming search fails, focus on torrents and vice versa
- If both fail, suggest the user try JustWatch (https://www.justwatch.com) for legal options
- Reply to Jerry and Hannah in Chinese
