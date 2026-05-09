---
name: market-analyst
description: 美股市场分析、投资建议、portfolio 管理、stock analysis。Use when the user asks for market analysis, stock commentary, portfolio review, US equities sentiment, or a daily market report.
---

# Market Analyst - 美股市场分析 Skill

## Purpose

美股市场分析、投资建议、portfolio 管理、stock analysis。当用户提到投资建议、股票分析、市场分析、portfolio、stock analysis、美股日报、持仓等关键词时触发。

## When to Use

- 用户要看美股市场日报
- 用户要分析持仓、单只股票或组合
- 用户要看市场情绪、新闻、技术面和操作建议

## Workflow

1. 读取当前持仓 `skills/market-analyst/data/portfolio.json`
2. 搜索以下信息源获取市场情绪（至少搜索 3-4 个来源）：
   - 财经新闻：Yahoo Finance, MarketWatch, Bloomberg
   - 论坛情绪：Reddit r/wallstreetbets, r/stocks, r/investing
   - 技术分析：TradingView, Seeking Alpha
3. 分析持仓股票的最新动态（财报、新闻、分析师评级）
4. 判断今天是否需要操作
5. 如果需要操作，给出具体建议（买入/卖出/持有，哪只股票，理由）
6. 如果不需要操作，说明原因
7. 通过 Telegram 发送给 Jerry (ID: 8791954608)

## Portfolio Context

- **本金:** £5,000（Trading212 练习账户）
- **市场:** 美股
- **目标:** 月度最大化收益
- **风险偏好:** 中等风险
- **持仓风格:** 5-7 只股票，跨板块分散，关注科技龙头 + 价值蓝筹 + 防御型配置

## Output Format

用中文输出，格式如下：

```
📊 美股日报 | YYYY-MM-DD

🏷️ 市场概况
- 标普500/纳斯达克最新动态
- 市场情绪：贪婪/恐惧/中性

📈 持仓分析
- 每只持仓股的最新动态
- 技术面简评

🎯 操作建议
- 买入/卖出/持有
- 具体股票和理由
- 或者"今日无需操作"及原因

💰 当前持仓概览
- 股票名称 | 买入价 | 现价 | 涨跌幅 | 仓位占比
```

## Rules

- 分析要具体，不要泛泛而谈
- 操作建议要给出明确理由
- 关注持仓股票的财报日期、重大事件
- 如果市场出现重大波动（如跌幅 > 2%），需要特别提示
