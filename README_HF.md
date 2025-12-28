---
title: Telegram SheerID Bot
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# Telegram SheerID 自动认证机器人

🤖 自动完成 SheerID 学生/教师认证的 Telegram 机器人（Webhook 模式）

## 功能特性

- ✅ Gemini One Pro 教师认证
- ✅ ChatGPT Teacher K12 认证
- ✅ Spotify Student 学生认证
- ✅ Bolt.new Teacher 认证
- ✅ YouTube Premium Student 认证

## 部署状态

访问以下端点检查服务状态：

- `/` - 服务信息
- `/health` - 健康检查
- `/webhook_info` - Webhook 状态

## 配置说明

请在 Space Settings 中配置以下环境变量：

### 必需配置

- `BOT_TOKEN` - Telegram Bot Token（Secret）
- `ADMIN_USER_ID` - 管理员 Telegram ID
- `WEBHOOK_URL` - 你的 Space URL（如：https://your-username-your-space.hf.space）
- `WEBHOOK_SECRET` - Webhook 安全令牌（Secret）

### 数据库配置

- `MYSQL_HOST` - MySQL 主机地址
- `MYSQL_USER` - MySQL 用户名
- `MYSQL_PASSWORD` - MySQL 密码（Secret）
- `MYSQL_DATABASE` - 数据库名称

## 使用方法

1. 在 Telegram 中搜索你的 Bot
2. 发送 `/start` 开始使用
3. 发送 `/help` 查看帮助

## 项目地址

GitHub: [PastKing/tgbot-verify](https://github.com/PastKing/tgbot-verify)
