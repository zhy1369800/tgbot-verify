# 📡 Webhook 模式部署指南

本指南介绍如何使用 Webhook 模式部署 Telegram Bot，适用于 Hugging Face Spaces、Railway、Render 等云平台。

---

## 🆚 Webhook vs 轮询模式对比

| 特性 | 轮询模式 (Polling) | Webhook 模式 |
|------|-------------------|--------------|
| **工作原理** | Bot 主动向 Telegram 请求更新 | Telegram 主动推送更新到 Bot |
| **网络要求** | 需要出站连接 | 需要公网 URL |
| **资源消耗** | 持续轮询，消耗较高 | 按需处理，消耗较低 |
| **响应速度** | 有延迟（轮询间隔） | 实时响应 |
| **适用场景** | 本地开发、VPS | 云平台部署 |
| **成本** | 较高（持续运行） | 较低（按需唤醒） |

---

## 🚀 快速开始

### 1️⃣ 准备工作

#### 生成 Webhook 安全令牌

```bash
# 在本地运行生成随机令牌
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

复制生成的令牌，稍后配置时使用。

#### 配置环境变量

复制 `.env.webhook.example` 为 `.env`：

```bash
cp .env.webhook.example .env
```

编辑 `.env` 文件，填写以下配置：

```env
# Telegram Bot Token（从 @BotFather 获取）
BOT_TOKEN=123456:ABCdefGHIjklMNOpqrsTUVwxyz

# 管理员 Telegram ID
ADMIN_USER_ID=123456789

# MySQL 数据库配置
MYSQL_HOST=your-mysql-host.com
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=tgbot_verify

# Webhook 配置
WEBHOOK_URL=https://your-app.hf.space  # 稍后填写
WEBHOOK_SECRET=刚才生成的随机令牌

# 端口配置
PORT=7860  # Hugging Face 默认端口
```

---

## 🌐 部署到不同平台

### 方案 A：Hugging Face Spaces

#### 步骤 1：创建 Space

1. 访问 [Hugging Face Spaces](https://huggingface.co/spaces)
2. 点击 **Create new Space**
3. 选择 **Docker** SDK
4. 填写 Space 名称（如 `tgbot-verify`）

#### 步骤 2：配置文件

在 Space 根目录创建 `Dockerfile`（使用 Webhook 版本）：

```bash
# 复制 Webhook Dockerfile
cp Dockerfile.webhook Dockerfile
```

#### 步骤 3：配置环境变量

在 Space 的 **Settings** → **Variables and secrets** 中添加：

| 名称 | 值 | 类型 |
|------|-----|------|
| `BOT_TOKEN` | 你的 Bot Token | Secret |
| `ADMIN_USER_ID` | 你的 Telegram ID | Variable |
| `MYSQL_HOST` | MySQL 主机地址 | Variable |
| `MYSQL_USER` | MySQL 用户名 | Variable |
| `MYSQL_PASSWORD` | MySQL 密码 | Secret |
| `MYSQL_DATABASE` | 数据库名 | Variable |
| `WEBHOOK_URL` | `https://你的用户名-你的space名.hf.space` | Variable |
| `WEBHOOK_SECRET` | 刚才生成的令牌 | Secret |
| `PORT` | `7860` | Variable |

#### 步骤 4：推送代码

```bash
git add .
git commit -m "Deploy webhook version"
git push
```

#### 步骤 5：验证部署

访问 `https://你的用户名-你的space名.hf.space/health`，应该看到：

```json
{"status": "ok", "bot_running": true}
```

---

### 方案 B：Railway.app

#### 步骤 1：安装 Railway CLI

```bash
npm install -g @railway/cli
```

#### 步骤 2：登录并初始化

```bash
railway login
railway init
```

#### 步骤 3：配置环境变量

```bash
railway variables set BOT_TOKEN=你的token
railway variables set ADMIN_USER_ID=你的ID
railway variables set MYSQL_HOST=你的MySQL主机
railway variables set MYSQL_USER=你的用户名
railway variables set MYSQL_PASSWORD=你的密码
railway variables set MYSQL_DATABASE=tgbot_verify
railway variables set WEBHOOK_SECRET=你的令牌
```

#### 步骤 4：部署

```bash
# 使用 Webhook Dockerfile
cp Dockerfile.webhook Dockerfile

# 部署
railway up
```

#### 步骤 5：获取公网 URL

```bash
railway domain
```

复制生成的域名（如 `your-app.railway.app`），然后设置：

```bash
railway variables set WEBHOOK_URL=https://your-app.railway.app
```

重新部署：

```bash
railway up
```

---

### 方案 C：Render.com

#### 步骤 1：创建 Web Service

1. 访问 [Render Dashboard](https://dashboard.render.com/)
2. 点击 **New** → **Web Service**
3. 连接你的 GitHub 仓库

#### 步骤 2：配置服务

- **Name**: `tgbot-verify`
- **Environment**: `Docker`
- **Dockerfile Path**: `Dockerfile.webhook`
- **Plan**: Free

#### 步骤 3：添加环境变量

在 **Environment** 标签页添加所有环境变量（同上）

#### 步骤 4：部署

点击 **Create Web Service**，等待部署完成。

---

## 🔧 本地测试 Webhook

### 使用 ngrok 创建临时公网 URL

```bash
# 安装 ngrok
# Windows: choco install ngrok
# Mac: brew install ngrok

# 启动 Bot
python bot_webhook.py

# 在另一个终端启动 ngrok
ngrok http 7860
```

复制 ngrok 提供的 HTTPS URL（如 `https://abc123.ngrok.io`），设置环境变量：

```bash
export WEBHOOK_URL=https://abc123.ngrok.io
export WEBHOOK_SECRET=your-secret-token
```

重启 Bot，访问 `https://abc123.ngrok.io/webhook_info` 查看 Webhook 状态。

---

## 📊 管理 Webhook

### 查看 Webhook 信息

访问：`https://your-app-url.com/webhook_info`

返回示例：

```json
{
  "url": "https://your-app-url.com/webhook/your-secret",
  "pending_update_count": 0,
  "last_error_message": null,
  "max_connections": 40,
  "allowed_updates": ["message", "callback_query", ...]
}
```

### 手动设置 Webhook

```bash
curl -X POST https://your-app-url.com/set_webhook \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": 你的管理员ID,
    "webhook_url": "https://your-new-url.com"
  }'
```

### 删除 Webhook

```bash
curl -X DELETE "https://your-app-url.com/webhook?admin_id=你的管理员ID"
```

---

## 🐛 故障排查

### 问题 1：Bot 没有响应

**检查步骤**：

1. 访问 `/health` 端点确认服务运行
2. 访问 `/webhook_info` 查看 Webhook 状态
3. 检查 `pending_update_count` 是否增加
4. 查看日志中是否有错误

**解决方案**：

```bash
# 检查 Webhook URL 是否正确
curl https://your-app-url.com/webhook_info

# 重新设置 Webhook
curl -X POST https://your-app-url.com/set_webhook \
  -H "Content-Type: application/json" \
  -d '{"admin_id": 你的ID, "webhook_url": "https://your-app-url.com"}'
```

### 问题 2：数据库连接失败

**检查**：

- MySQL 主机是否可从云平台访问
- 防火墙是否允许云平台 IP
- 数据库用户权限是否正确

**解决方案**：

```bash
# 在云平台容器中测试连接
mysql -h your-mysql-host.com -u your_user -p
```

### 问题 3：Webhook 验证失败

**错误信息**：`403 Invalid webhook token`

**原因**：URL 中的 token 与 `WEBHOOK_SECRET` 不匹配

**解决方案**：

确保 Telegram Webhook URL 格式正确：
```
https://your-app-url.com/webhook/{WEBHOOK_SECRET}
```

---

## 🔐 安全建议

1. **使用强随机令牌**：
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **定期轮换密钥**：
   - 每 3-6 个月更换 `WEBHOOK_SECRET`
   - 更新后重新设置 Webhook

3. **限制访问**：
   - 仅管理员可调用 `/set_webhook` 和 `/webhook` 删除接口
   - 使用环境变量存储敏感信息

4. **监控日志**：
   - 定期检查无效 token 尝试
   - 设置告警通知

---

## 📈 性能优化

### 1. 启用持久化存储（可选）

Hugging Face Spaces 默认存储是临时的，重启后数据丢失。如需持久化：

- 升级到付费存储层
- 或使用外部 MySQL 数据库（推荐）

### 2. 调整并发设置

在 `bot_webhook.py` 中调整：

```python
application = (
    Application.builder()
    .token(BOT_TOKEN)
    .concurrent_updates(True)  # 启用并发
    .build()
)
```

### 3. 优化 Webhook 连接数

```python
await application.bot.set_webhook(
    url=webhook_path,
    max_connections=40,  # 默认 40，可调整为 1-100
    drop_pending_updates=True
)
```

---

## 📚 相关资源

- [Telegram Bot API - Webhook 文档](https://core.telegram.org/bots/api#setwebhook)
- [Hugging Face Spaces 文档](https://huggingface.co/docs/hub/spaces)
- [Railway 部署指南](https://docs.railway.app/)
- [Render 部署指南](https://render.com/docs)

---

## ❓ 常见问题

### Q: Webhook 和轮询模式可以同时使用吗？

**A**: 不可以！同一个 Bot Token 只能使用一种模式。如果设置了 Webhook，轮询模式会失败。

### Q: 如何切换回轮询模式？

**A**: 删除 Webhook 即可：

```bash
curl -X DELETE "https://your-app-url.com/webhook?admin_id=你的ID"
```

然后使用 `python bot.py` 启动轮询模式。

### Q: Webhook URL 必须是 HTTPS 吗？

**A**: 是的！Telegram 只接受 HTTPS Webhook URL（本地测试可用 ngrok）。

### Q: 部署后如何验证 Webhook 是否工作？

**A**:

1. 访问 `/webhook_info` 查看状态
2. 给 Bot 发送消息测试
3. 检查 `pending_update_count` 是否为 0

---

## 🎉 完成！

现在你的 Telegram Bot 已经成功部署在云平台上了！

如有问题，请访问 [GitHub Issues](https://github.com/PastKing/tgbot-verify/issues) 反馈。
