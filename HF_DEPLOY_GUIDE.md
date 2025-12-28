# 🚀 Hugging Face Spaces 部署完整指南

本指南将手把手教你如何在 Hugging Face Spaces 上部署 Telegram Bot（Webhook 模式）。

---

## 📋 前置准备

### ✅ 必需条件

- [x] Hugging Face 账号（[注册地址](https://huggingface.co/join)）
- [x] Telegram Bot Token（从 [@BotFather](https://t.me/BotFather) 获取）
- [x] MySQL 数据库（可从公网访问）
- [x] 你的 Telegram User ID（可通过 [@userinfobot](https://t.me/userinfobot) 获取）

### 📦 准备工作

1. **获取 Telegram Bot Token**
   ```
   在 Telegram 中搜索 @BotFather
   发送 /newbot
   按提示创建 Bot
   保存返回的 Token（格式：123456:ABCdefGHIjklMNOpqrsTUVwxyz）
   ```

2. **获取你的 Telegram User ID**
   ```
   在 Telegram 中搜索 @userinfobot
   发送 /start
   保存返回的 ID（纯数字）
   ```

3. **准备 MySQL 数据库**
   - 确保数据库可以从公网访问
   - 记录：主机地址、端口、用户名、密码、数据库名

---

## 🎯 部署步骤

### 方式 A：使用自动化脚本（推荐）

#### Windows 用户

1. **打开 Git Bash**（如果没有，请安装 [Git for Windows](https://git-scm.com/download/win)）

2. **进入项目目录**
   ```bash
   cd C:\Users\zhy93\Desktop\tgbot-verify
   ```

3. **运行部署脚本**
   ```bash
   bash deploy_to_hf.sh
   ```

4. **按照脚本提示操作**
   - 脚本会自动生成 Webhook Secret
   - 准备好所有配置信息
   - 按提示输入 Hugging Face Space URL

#### Linux/Mac 用户

```bash
cd /path/to/tgbot-verify
chmod +x deploy_to_hf.sh
./deploy_to_hf.sh
```

---

### 方式 B：手动部署（详细步骤）

#### 第 1 步：创建 Hugging Face Space

1. **访问创建页面**

   打开：https://huggingface.co/new-space

2. **填写 Space 信息**
   - **Owner**: 选择你的账号
   - **Space name**: 输入名称（如：`tgbot-verify`）
   - **License**: 选择 `MIT`
   - **Select the Space SDK**: 选择 `Docker`
   - **Space hardware**: 选择 `CPU basic - Free`
   - **Visibility**: 选择 `Public` 或 `Private`

3. **点击 "Create Space"**

4. **记录 Space URL**

   格式：`https://huggingface.co/spaces/<你的用户名>/<Space名称>`

---

#### 第 2 步：准备部署文件

1. **复制 Webhook Dockerfile**
   ```bash
   cd C:\Users\zhy93\Desktop\tgbot-verify
   copy Dockerfile.webhook Dockerfile
   ```

2. **生成 Webhook Secret**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   复制输出的字符串，这是你的 `WEBHOOK_SECRET`

---

#### 第 3 步：推送代码到 Hugging Face

1. **获取 Space 的 Git URL**

   在 Space 页面点击 "Clone repository"，复制 HTTPS URL

   格式：`https://huggingface.co/spaces/<你的用户名>/<Space名称>`

2. **添加远程仓库**
   ```bash
   git remote add hf https://huggingface.co/spaces/<你的用户名>/<Space名称>
   ```

3. **提交更改**
   ```bash
   git add Dockerfile .dockerignore README_HF.md
   git commit -m "Deploy webhook version to Hugging Face Spaces"
   ```

4. **推送到 Hugging Face**
   ```bash
   git push hf main
   ```

   **注意**：
   - 用户名：你的 Hugging Face 用户名
   - 密码：使用 **Access Token**（不是账号密码！）

   **创建 Access Token**：
   1. 访问：https://huggingface.co/settings/tokens
   2. 点击 "New token"
   3. Name: `tgbot-deploy`
   4. Role: `write`
   5. 点击 "Generate"
   6. 复制 Token（只显示一次！）

---

#### 第 4 步：配置环境变量

1. **进入 Space Settings**

   访问：`https://huggingface.co/spaces/<你的用户名>/<Space名称>/settings`

2. **点击 "Variables and secrets" 标签**

3. **添加 Secrets**（敏感信息）

   点击 "New secret"，逐个添加：

   | Name | Value | 说明 |
   |------|-------|------|
   | `BOT_TOKEN` | `123456:ABCdef...` | 你的 Telegram Bot Token |
   | `WEBHOOK_SECRET` | 刚才生成的随机字符串 | Webhook 安全令牌 |
   | `MYSQL_PASSWORD` | 你的数据库密码 | MySQL 密码 |

4. **添加 Variables**（非敏感配置）

   点击 "New variable"，逐个添加：

   | Name | Value | 说明 |
   |------|-------|------|
   | `ADMIN_USER_ID` | `123456789` | 你的 Telegram User ID |
   | `MYSQL_HOST` | `your-db.com` | MySQL 主机地址 |
   | `MYSQL_USER` | `your_user` | MySQL 用户名 |
   | `MYSQL_DATABASE` | `tgbot_verify` | 数据库名称 |
   | `WEBHOOK_URL` | `https://<你的用户名>-<Space名称>.hf.space` | Space 的公网 URL |
   | `PORT` | `7860` | 端口号（Hugging Face 默认） |
   | `CHANNEL_USERNAME` | `pk_oa` | 频道用户名（可选） |
   | `CHANNEL_URL` | `https://t.me/pk_oa` | 频道链接（可选） |

5. **保存配置**

---

#### 第 5 步：等待部署完成

1. **查看构建日志**

   在 Space 页面会自动开始构建，可以看到实时日志

2. **构建时间**

   首次构建约需 **5-10 分钟**（安装依赖、Playwright 浏览器等）

3. **部署成功标志**

   日志中出现：
   ```
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:7860
   ```

---

#### 第 6 步：验证部署

1. **访问健康检查端点**

   打开浏览器访问：
   ```
   https://<你的用户名>-<Space名称>.hf.space/health
   ```

   应该看到：
   ```json
   {
     "status": "ok",
     "bot_running": true
   }
   ```

2. **查看 Webhook 信息**

   访问：
   ```
   https://<你的用户名>-<Space名称>.hf.space/webhook_info
   ```

   应该看到：
   ```json
   {
     "url": "https://<你的用户名>-<Space名称>.hf.space/webhook/<你的secret>",
     "pending_update_count": 0,
     "last_error_message": null
   }
   ```

3. **测试 Bot**

   在 Telegram 中：
   - 搜索你的 Bot（使用创建时的用户名）
   - 发送 `/start`
   - 应该收到欢迎消息

---

## 🐛 常见问题排查

### 问题 1：推送代码时提示 "Authentication failed"

**原因**：使用了账号密码而不是 Access Token

**解决方案**：
1. 创建 Access Token（见上文）
2. 使用 Token 作为密码
3. 或者使用 SSH 方式推送

### 问题 2：部署后访问 `/health` 返回 404

**原因**：
- 构建失败
- 端口配置错误

**解决方案**：
1. 查看 Space 的 Logs 标签
2. 检查是否有错误信息
3. 确认 `PORT=7860` 已配置

### 问题 3：Bot 没有响应

**检查清单**：

1. **Webhook 是否设置成功**
   ```
   访问 /webhook_info
   检查 url 字段是否正确
   ```

2. **环境变量是否配置正确**
   ```
   检查 BOT_TOKEN 是否正确
   检查 WEBHOOK_URL 是否正确
   检查 WEBHOOK_SECRET 是否正确
   ```

3. **数据库是否连接成功**
   ```
   查看 Space Logs
   搜索 "数据库" 或 "MySQL"
   检查是否有连接错误
   ```

4. **手动重新设置 Webhook**
   ```bash
   curl -X POST https://<你的Space URL>/set_webhook \
     -H "Content-Type: application/json" \
     -d '{
       "admin_id": 你的管理员ID,
       "webhook_url": "https://<你的Space URL>"
     }'
   ```

### 问题 4：数据库连接失败

**错误信息**：`Can't connect to MySQL server`

**解决方案**：
1. 确认 MySQL 允许外网访问
2. 检查防火墙规则
3. 确认用户权限：
   ```sql
   GRANT ALL PRIVILEGES ON tgbot_verify.* TO 'your_user'@'%';
   FLUSH PRIVILEGES;
   ```

### 问题 5：构建超时或失败

**原因**：
- 网络问题
- 依赖安装失败

**解决方案**：
1. 在 Space Settings 中点击 "Factory reboot"
2. 等待重新构建
3. 如果仍然失败，检查 Dockerfile.webhook 是否正确

---

## 📊 监控和维护

### 查看运行日志

1. **进入 Space 页面**
2. **点击 "Logs" 标签**
3. **查看实时日志**

### 重启 Space

1. **进入 Settings**
2. **点击 "Factory reboot"**
3. **等待重启完成**

### 更新代码

```bash
# 修改代码后
git add .
git commit -m "Update: 描述你的更改"
git push hf main

# Space 会自动重新构建
```

---

## 🎯 性能优化建议

### 1. 升级硬件（可选）

免费的 CPU Basic 足够大多数场景，如果需要更好性能：

- 进入 Settings → Hardware
- 选择更高配置（需付费）

### 2. 启用持久化存储（可选）

如果需要保存文件：

- 进入 Settings → Storage
- 选择存储层级（需付费）

### 3. 优化数据库查询

- 为常用字段添加索引
- 定期清理过期数据

---

## 📚 相关资源

- [Hugging Face Spaces 文档](https://huggingface.co/docs/hub/spaces)
- [Telegram Bot API 文档](https://core.telegram.org/bots/api)
- [项目 GitHub 仓库](https://github.com/PastKing/tgbot-verify)
- [Webhook 部署文档](./WEBHOOK_DEPLOY.md)

---

## ✅ 部署检查清单

部署完成后，请确认以下所有项目：

- [ ] Space 已创建并运行
- [ ] 所有环境变量已配置
- [ ] `/health` 返回正常
- [ ] `/webhook_info` 显示正确的 URL
- [ ] Bot 在 Telegram 中可以搜索到
- [ ] `/start` 命令有响应
- [ ] 数据库连接正常
- [ ] 认证功能可以正常使用

---

## 🎉 恭喜！

如果所有检查项都通过，你的 Telegram Bot 已经成功部署在 Hugging Face Spaces 上了！

**下一步**：
- 邀请用户使用你的 Bot
- 监控运行状态
- 根据需要调整配置

有问题？欢迎在 [GitHub Issues](https://github.com/PastKing/tgbot-verify/issues) 提问！
