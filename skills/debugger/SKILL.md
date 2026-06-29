---
name: debugger
description: Diagnose and fix bugs, find root causes of failures, analyze error logs and stack traces. Use when debugging crashes, exceptions, memory leaks, race conditions, performance issues, or production incidents that need systematic root-cause analysis. 触发词如"帮我debug"、"找bug"、"为什么报错"、"崩溃了"、"内存泄漏"、"线上故障"、"stack trace"。
---

# Debugger

资深调试能力：系统化定位复杂软件问题，分析系统行为，找根因。重点是高效解决问题并沉淀防复发的经验。

## 何时用

- 崩溃、异常、报错要查根因
- 内存泄漏、资源泄漏
- 竞态、死锁等并发问题
- 性能瓶颈
- 线上故障排查

## 故障定位决策树（按顺序走）

1. **复现** — 写一个能稳定触发问题的最小用例。复现不了就先查复现差距，别急着改。
2. **确认现象 vs 预期** — 精确描述："在 X 条件下，系统做了 Y，但应该做 Z。"
3. **列排序假设** — 给 2~3 个候选根因，按可能性排序，结合最近改动和症状。
4. **证伪最可能的假设** — 设计最便宜的实验（一行日志 / 一次 grep / 一句断言），先证伪再改代码。
5. **修复 + 回归测试** — 改完加一个能在修复前就抓到这个 bug 的测试当哨兵。
6. **记录根因** — 根因、诱因、证伪过程、一条预防措施。

## 可观测性优先（线上故障）

读代码前先看三大支柱：

1. **分布式 trace** — 找第一个失败 span，定位出错的服务和操作
2. **关联日志** — 收窄到第一个 trace 错误时间 ±2 分钟，按服务名和 trace ID 过滤
3. **变更关联** — 看错误前 30 分钟内有没有部署、配置变更、feature flag、流量突增（`git log --since`）

三支柱走完再进静态代码分析。

## 常见 bug 模式

off-by-one、空指针、资源泄漏、竞态、整型溢出、类型不匹配、逻辑错误、配置问题。

## 自检清单

- 问题稳定复现了吗
- 根因明确吗
- 修复验证了吗
- 副作用查了吗
- 回归测试加了吗
- 根因记录了吗
