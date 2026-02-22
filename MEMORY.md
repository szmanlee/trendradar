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
