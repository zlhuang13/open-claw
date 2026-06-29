---
name: prompt-engineer
description: Design, optimize, test, and evaluate prompts for large language models. Use when crafting system prompts, improving prompt accuracy or consistency, reducing token usage and cost, building few-shot or chain-of-thought patterns, A/B testing prompt variations, or setting up prompt evaluation and version management. 触发词如"优化prompt"、"改提示词"、"prompt不稳定"、"帮我写system prompt"、"降低token"。
---

# Prompt Engineer

资深 prompt 工程能力：设计 prompt 模式、做评估、A/B 测试、生产环境 prompt 管理。重点是稳定可靠的输出，同时压低 token 和成本。

## 何时用

- 要设计或重构 system prompt / 模板
- prompt 输出不稳定、不一致，要提鲁棒性
- 要降 token、降成本
- 要建评估框架、A/B 测试、版本管理

## 工作流程

1. 先搞清需求：用例、性能目标、成本约束、安全要求、成功指标
2. 设计 prompt 与模板，准备 few-shot 示例
3. 测多个变体，量化 accuracy / token / latency / cost
4. 选最优方案，加监控和文档

## Prompt 模式

- Zero-shot / Few-shot
- Chain-of-thought / Tree-of-thought
- ReAct
- Constitutional AI
- Role-based prompting

## 优化手段

- Token 压缩、context 裁剪、输出格式约束
- 缓存策略、批处理
- 动态 few-shot 选择
- 重试与 fallback 链

## 评估

- Accuracy / 一致性 / 边界用例覆盖
- A/B 测试设计与统计显著性
- 成本收益分析

## 自检清单

- accuracy 是否达标
- token 是否最优
- 成本是否可控
- 安全过滤是否就位
- 是否有版本管理和文档
