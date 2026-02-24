# MEMORY.md - 长期记忆

## ⚠️ Mattermost 消息送达问题 (2026-02-20)

### 问题表现
- OpenClaw 发送消息成功（低延迟），但用户端收不到
- 日志显示 `chat.send` 返回 9ms/14ms，无报错

### 诊断发现
- **03:22-03:32 UTC**: Mattermost channel 频繁崩溃（`fetch failed`）
- 重启 8/9/10 次后 03:32:03 才恢复 (`mattermost connected as @x26`)
- **根因**: OpenClaw 配置中的旧令牌过期 → "无法找到账户" 错误 → 消息队列卡死 → 无限重试 → WebSocket 资源耗尽 → 掉线

### 🔑 最终根因 (04:15-04:26 UTC 确认)
| 配置项 | 值 | 状态 |
|--------|-----|------|
| OpenClaw 配置中的令牌 | `enh3upsce7gxtez7gbpqjonnha` | ❌ 已过期/被撤销 |
| Mattermost 服务器有效令牌 | `g8w3epsmxpf9mj7dk54bbs9zow` | ✅ 正确 |
| 配置路径 | `channels.mattermost.botToken` | - |

### 解决方案
1. **04:26 UTC**: 执行 `openclaw config.patch` 更新令牌
2. **04:27 UTC**: 网关自动重启 (SIGUSR1)
3. **待测试**: 等待用户确认新令牌生效

### ⚡ 实时检查机制（重要！）
**每次回复前必须检查**：
- 查看 `gateway log --tail` 中的 Mattermost 连接状态
- 确认 `mattermost connected as @x26` 存在
- 如果 `fetch failed`、`websocket` 错误或连接断开：
  - ⚠️ 提示用户可能无法收到消息
  - 建议重启网关：`openclaw gateway restart`
- **用户反馈收不到消息时**，优先检查网关日志而非重发

### 预防措施
- **令牌管理**: 定期检查 Mattermost bot 令牌有效性，服务器端令牌更新后立即同步到 OpenClaw 配置
- **队列监控**: 发现 `chat.send` 长时间无响应（>5s）时主动告警，检查是否有卡住的消息
- **定期检查**: RSS/cron 任务报错时优先检查网关状态和 Mattermost 连接
- **配置验证**: 使用 `openclaw config get` 确认当前使用的令牌 ID

---

## ✅ OpenClaw 最佳配置 (2026-02-20 05:52 UTC 确认)

### Mattermost Channel 配置
| 配置项 | 值 |
|--------|-----|
| botToken | `nsycfxdt4jr3xb1nofh631d4zh` |
| botUsername | `x26` |
| baseUrl | `http://192.168.32.220:8065` |
| defaultChannel | `town-square` |
| skipWsConnect | `true` |
| useWebhookOnly | `true` |

### 关键要点
- **禁用 WebSocket** (`skipWsConnect: true`) 解决消息无法送达问题
- **使用 webhook 模式** (`useWebhookOnly: true`) 简化连接
- 令牌 ID（18td4xdg4jn6u8a5o49xpt1oir）对应访问令牌 `nsycfxdt4jr3xb1nofh631d4zh`

---

## 🎯 Jarvis Skills 安装完成 (2026-02-22 23:43 UTC)

### ✅ 已安装 (6/6, 100%)
| Skill | 功能 | 状态 |
|-------|------|------|
| **code** (v1.0.4) | 代码工作流（规划/执行/验证） | ✅ 已安装 |
| **tdd-guide** | 测试驱动开发指南 | ✅ 已安装 |
| **exa-web-search-free** | Exa 免费网页搜索 | ✅ 已安装（需配置 mcporter） |
| **voice-reply** | 本地语音合成（TTS） | ✅ 已安装（需安装依赖） |
| **cognitive-memory** | 多存储记忆系统 | ✅ 已安装（需初始化） |
| **self-improving-agent** | 自我提升代理 | ✅ 已安装 |

### 替代方案
- `coding-agent` 未找到 → 使用 **code** (v1.0.4, ⭐ 0.911) 替代

### 配置状态
| Skill | 依赖/配置 |
|-------|-----------|
| exa-web-search-free | `mcporter config add exa https://mcp.exa.ai/mcp` |
| voice-reply | `scripts/install.sh` 安装 sherpa-onnx + piper voices |
| cognitive-memory | `scripts/init_memory.sh` 初始化记忆目录 |

---

## 🎯 已安装 Skills 完整清单 (2026-02-23 更新)

| # | Skill | 路径 | 状态 |
|---|-------|------|------|
| 1 | **code** | `/root/.openclaw/workspace/skills/code/` | ✅ 即用型 |
| 2 | **tdd-guide** | `/root/.openclaw/workspace/skills/tdd-guide/` | ✅ 7个脚本 |
| 3 | **exa-web-search-free** | `/root/.openclaw/workspace/skills/exa-web-search-free/` | ⚠️ 需配置 mcporter |
| 4 | **voice-reply** | `/root/.openclaw/workspace/skills/voice-reply/` | ⚠️ 需安装 TTS 依赖 |
| 5 | **cognitive-memory** | `/root/.openclaw/workspace/skills/cognitive-memory/` | ⚠️ 需初始化 |
| 6 | **self-improving-agent** | `/root/.openclaw/skills/self-improving-agent/` | ✅ 即用型 |
| 7 | **tavily-search** | `/root/.openclaw/workspace/skills/tavily-search/` | ✅ MCP 模式 |
| 8 | **telnyx-stt** | `/root/.openclaw/workspace/skills/telnyx-stt/` | ❓ 待检查 |
| 9 | **memory-system** | `/root/.openclaw/workspace/memory-system/` | ❓ 旧版/实验性 |

**配置状态汇总**：
- ✅ 即用型：code, self-improving-agent, tdd-guide, tavily-search (MCP)
- ⚠️ 需配置：exa-web-search-free (mcporter), voice-reply (TTS), cognitive-memory (初始化)
- ❓ 待检查：telnyx-stt, memory-system

---

## 🔑 GitHub 凭证管理 (待补充)

### ⚠️ 重要提示
- **凭证存储**: GitHub Token 未保存在当前上下文中
- **建议**: 首次使用后保存到 `~/.netrc` 或环境变量
- **安全提醒**: 不要在聊天中直接发送 Token

### 当前状态
- GitHub 用户名: ____________ (待补充)
- Personal Access Token: ____________ (待补充)
- 存储位置建议: `~/.netrc` 或 `~/.bashrc`

---

## 📊 Jarvis Dashboard v2.0 控制面板 (2026-02-24)

### 部署信息
| 配置项 | 值 |
|--------|-----|
| 位置 | `/root/.openclaw/workspace/jarvis-dashboard/` |
| 服务端口 | 8080 |
| 访问地址 | http://192.168.32.26:8080/ |

### 功能模块 (11 个)
| 模块 | 功能 |
|------|------|
| 📊 仪表盘 | 系统概览、CPU/内存/磁盘、容器统计 |
| 📈 系统监控 | 内存环图、磁盘条、进程列表 |
| 🐳 容器管理 | Docker 容器启停 |
| 📁 文件管理 | 文件浏览、目录导航 |
| 🔧 终端 | 命令执行、CWD 跟踪 |
| 📝 日志查看 | 系统日志/OpenClaw 日志 |
| 🌐 网络工具 | Ping/端口/DNS 查询 |
| 🤖 AI 配置 | 模型信息、API 配置 |
| 🧩 Skills | Skills 列表管理 |
| ⚡ 快捷命令 | 预设常用操作 |
| ⚙️ 设置 | 主题、搜索等配置 |

### 待实现
- [ ] 对接后端 API 服务（当前静态页面可用）
- [ ] 参考 192.168.32.23:2380 实现完善功能

---

## 🖥️ TrendRadar 服务管理 (2026-02-24)

### 服务配置
| 端口 | 服务 | 状态 | 管理方式 |
|------|------|------|----------|
| 2680 | TrendRadar 静态文件 | ✅ 运行中 | systemd service |
| 4173 | 局势监控预览 | ✅ 运行中 | npm preview |
| 8080 | Jarvis Dashboard | ✅ 运行中 | python http.server |

### systemd service 配置
```ini
[Unit]
Description=TrendRadar HTTP Server (port 2680)
After=network.target

[Service]
Type=simple
WorkingDirectory=/root/.openclaw/workspace/trendradar/output
ExecStart=/usr/bin/python3 -m http.server 2680
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 服务管理命令
```bash
# 查看状态
systemctl status trendradar-2680

# 重启服务
systemctl restart trendradar-2680

# 查看日志
tail -f /tmp/2680.log
```
