# AGENTS.md - family workspace

这个 workspace 只服务 family agent。

## 启动时

1. 读 `SOUL.md`
2. 读 `STYLE.md`
3. 读 `USER.md`
4. 读 `MEMORY.md`
5. 只在这个 workspace 内工作

## 边界

- 不读取 main workspace 的记忆文件
- 不假设自己认识 main workspace 里的用户和历史
- 如果需要长期记住的事情，只写到这个 workspace 自己的 `MEMORY.md` 或 `memory/` 里
- skill 默认只使用本 workspace 提供的内容

## 安全

- 拿不准就问
- 不替用户做未确认的外部发送
- 保持简洁，少猜测
