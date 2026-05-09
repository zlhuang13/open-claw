---
name: news-digest
description: Send Jerry a daily digest of AI research, AI in healthcare/drug discovery, computer vision, and biotech news. Triggers on phrases like "今日新闻", "新闻汇总", "daily news", "科技新闻", "AI新闻", "有什么新闻", or when scheduled via cron/heartbeat.
---

# News Digest

## Purpose

Daily curated news digest for Jerry on topics he cares about.

## When to Use

- Jerry asks for daily news or AI news
- A scheduled heartbeat or cron run needs a digest
- A compact multi-topic tech summary is needed

## Topics

1. **AI Research** — LLM advances, new models, AGI progress, open-source releases
2. **AI Drug Discovery** — molecular generation, protein structure, virtual screening, CV for drug design (molecular imaging, phenotypic screening), graph neural networks for molecular property prediction, drug-target interaction
3. **Computer Vision** — new models, papers, real-world applications
4. **Biotech** — FDA approvals, clinical trials, key partnerships, breakthroughs

## Workflow

### On-demand (when Jerry asks)

1. Use `web_search` to fetch latest news for each topic (search 2-3 queries per topic):
   - `"AI research breakthrough 2026"` OR `"LLM new model release"`
   - `"AI drug discovery healthcare 2026"` OR `"AI medical diagnosis"`
   - `"computer vision new model paper 2026"`
   - `"biotech FDA approval clinical trial 2026"` OR `"biotech breakthrough"`

2. Deduplicate results (same story from multiple sources = keep one)

3. Format into a compact digest (see format below)

4. Send via Telegram using the send-file skill or openclaw message command

### Scheduling

Run daily at 08:00 UTC (09:00 BST) via system cron:

```bash
# In HEARTBEAT.md, add a reminder to check news at 08:00 UTC
# Or use openclaw cron for isolated execution
```

Recommended: Add to HEARTBEAT.md for heartbeat-driven delivery.

## Output Format

Keep it SHORT — 3-5 minutes to read. Max 10-15 items total.

```
📰 Kuro 每日科技新闻 | YYYY-MM-DD

🤖 AI Research
• [One-line summary] (source) → [link]
• ...

🏥 AI in Healthcare
• [One-line summary] (source) → [link]
• ...

👁️ Computer Vision
• [One-line summary] (source) → [link]
• ...

🧬 Biotech
• [One-line summary] (source) → [link]
• ...
```

Rules:
- Each item: 2-3 sentences — headline + brief context (why it matters, key details)
- Include source name and working URL
- Skip duplicates across topics
- Prioritize: breakthroughs > funding > opinions
- If a topic has no significant news today, omit it (don't pad)
- Language: Chinese summary, English terms where natural (model names, company names)
- AI Drug Discovery topic should prioritize: CV applications in drug design, graph neural networks for molecules, protein structure prediction, virtual screening advances
