# TOOLS.md - 本地备注

Skills 负责定义“怎么做”，这个文件记录“你这里具体是什么情况”。

## 这里适合放什么

比如：

- 摄像头名字和位置
- SSH 主机和别名
- 偏好的 TTS 声音
- 音箱、房间名字
- 设备昵称
- 任何和当前环境强相关的内容

## 示例

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## 为什么单独放这里

Skill 是可共享的，你的环境不是。把这些内容分开，更新 skill 时不容易把本地信息冲掉，也不会在分享 skill 时顺手把自己的环境细节泄出去。

以后这里新增内容，默认直接用中文写。路径、命令、配置键名保留英文。

---

### 自定义 Skills

- `skills/bin-collection/`，垃圾收集查询（Playwright）
- `skills/movie-finder/`，电影片源搜索
- `skills/send-file/`，Telegram 发文件

### 关键路径

- Playwright：`./node_modules/playwright`
- Chromium：`~/.cache/ms-playwright/chromium_headless_shell-1217/`
- Node：`/home/ubuntu/.nvm/versions/node/v24.14.1/bin/node`
- OpenClaw 配置：`~/.openclaw/openclaw.json`

### Dashboard（Garden DB）

- Service：`umi-dashboard.service`（systemd，enabled）
- Port：80，bind：`100.86.143.43`（仅 Tailscale）
- URL：`http://kuro-app.tail4dc7fc.ts.net/`
- Path：`/home/ubuntu/.openclaw/workspace/skills/garden-tracker/scripts/dashboard/`

### OpenClaw Gateway

- Port：18789，bind：loopback
- Tailscale serve：未启用（port 80 给 Garden DB 用）
- 默认模型：`zai/glm-5.1`（fallback：`claude-sonnet`）

有用的本地细节都可以往这里加。这就是你的环境速查表。
