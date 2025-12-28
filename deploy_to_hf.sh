#!/bin/bash
# -*- coding: utf-8 -*-
# Hugging Face Spaces 部署脚本

set -e  # 遇到错误立即退出

echo "🚀 开始准备 Hugging Face Spaces 部署..."

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 检查是否在项目根目录
if [ ! -f "bot_webhook.py" ]; then
    echo -e "${RED}❌ 错误：请在项目根目录运行此脚本！${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 项目目录检查通过${NC}"

# 2. 备份原始 Dockerfile
if [ -f "Dockerfile" ]; then
    echo -e "${YELLOW}⚠️  发现已存在的 Dockerfile，正在备份...${NC}"
    cp Dockerfile Dockerfile.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✅ 已备份到 Dockerfile.backup.*${NC}"
fi

# 3. 使用 Webhook 版本的 Dockerfile
echo "📦 准备 Dockerfile..."
cp Dockerfile.webhook Dockerfile
echo -e "${GREEN}✅ Dockerfile 已准备就绪${NC}"

# 4. 创建 Hugging Face Space 的 README
echo "📝 准备 README..."
if [ -f "README_HF.md" ]; then
    cp README_HF.md README_SPACE.md
    echo -e "${GREEN}✅ README 已准备就绪${NC}"
else
    echo -e "${RED}❌ 未找到 README_HF.md 文件${NC}"
    exit 1
fi

# 5. 生成 Webhook Secret（如果需要）
echo ""
echo "🔐 生成 Webhook Secret Token..."
WEBHOOK_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
echo -e "${GREEN}✅ Webhook Secret: ${WEBHOOK_SECRET}${NC}"
echo -e "${YELLOW}⚠️  请保存此 Secret，稍后需要在 Hugging Face Space 中配置！${NC}"

# 6. 提示用户配置信息
echo ""
echo "============================================"
echo "📋 部署前配置清单"
echo "============================================"
echo ""
echo "请准备以下信息，稍后需要在 Hugging Face Space Settings 中配置："
echo ""
echo -e "${YELLOW}【必需的 Secrets】${NC}"
echo "1. BOT_TOKEN          = <你的 Telegram Bot Token>"
echo "2. WEBHOOK_SECRET     = ${WEBHOOK_SECRET}"
echo "3. MYSQL_PASSWORD     = <你的 MySQL 密码>"
echo ""
echo -e "${YELLOW}【必需的 Variables】${NC}"
echo "4. ADMIN_USER_ID      = <你的 Telegram ID>"
echo "5. MYSQL_HOST         = <你的 MySQL 主机地址>"
echo "6. MYSQL_USER         = <你的 MySQL 用户名>"
echo "7. MYSQL_DATABASE     = tgbot_verify"
echo "8. WEBHOOK_URL        = https://<你的用户名>-<Space名称>.hf.space"
echo "9. PORT               = 7860"
echo ""
echo "============================================"
echo ""

# 7. 检查 Git 状态
echo "🔍 检查 Git 状态..."
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ 错误：当前目录不是 Git 仓库${NC}"
    echo "请先初始化 Git 仓库："
    echo "  git init"
    echo "  git add ."
    echo "  git commit -m 'Initial commit'"
    exit 1
fi

echo -e "${GREEN}✅ Git 仓库检查通过${NC}"

# 8. 提示下一步操作
echo ""
echo "============================================"
echo "🎯 下一步操作指南"
echo "============================================"
echo ""
echo "1️⃣  创建 Hugging Face Space："
echo "   访问: https://huggingface.co/new-space"
echo "   - Name: 输入你的 Space 名称（如：tgbot-verify）"
echo "   - SDK: 选择 'Docker'"
echo "   - Hardware: 选择 'CPU basic - Free'"
echo ""
echo "2️⃣  获取 Space 的 Git 地址："
echo "   创建后会显示类似："
echo "   https://huggingface.co/spaces/<你的用户名>/<Space名称>"
echo ""
echo "3️⃣  添加远程仓库并推送："
read -p "   请输入你的 Hugging Face Space Git URL: " HF_REPO_URL

if [ -z "$HF_REPO_URL" ]; then
    echo -e "${YELLOW}⚠️  未输入 URL，跳过自动推送${NC}"
    echo ""
    echo "手动推送命令："
    echo "  git remote add hf <你的 Space Git URL>"
    echo "  git add ."
    echo "  git commit -m 'Deploy webhook version to Hugging Face'"
    echo "  git push hf main"
else
    echo ""
    echo "🚀 准备推送到 Hugging Face..."

    # 检查是否已存在 hf remote
    if git remote | grep -q "^hf$"; then
        echo -e "${YELLOW}⚠️  已存在 hf remote，正在更新...${NC}"
        git remote set-url hf "$HF_REPO_URL"
    else
        git remote add hf "$HF_REPO_URL"
    fi

    # 添加并提交更改
    git add Dockerfile README_SPACE.md .dockerignore
    git commit -m "Deploy webhook version to Hugging Face Spaces" || true

    # 推送到 Hugging Face
    echo "📤 推送代码到 Hugging Face..."
    echo -e "${YELLOW}⚠️  如果提示输入用户名和密码：${NC}"
    echo "   用户名: 你的 Hugging Face 用户名"
    echo "   密码: 使用 Access Token（在 https://huggingface.co/settings/tokens 创建）"
    echo ""

    if git push hf main; then
        echo -e "${GREEN}✅ 代码推送成功！${NC}"
    else
        echo -e "${RED}❌ 推送失败，请检查凭据或手动推送${NC}"
        exit 1
    fi
fi

echo ""
echo "============================================"
echo "⚙️  配置环境变量"
echo "============================================"
echo ""
echo "4️⃣  在 Hugging Face Space 中配置环境变量："
echo "   访问: https://huggingface.co/spaces/<你的用户名>/<Space名称>/settings"
echo ""
echo "   点击 'Variables and secrets' 标签，添加："
echo ""
echo "   【Secrets】（点击 'New secret'）"
echo "   - Name: BOT_TOKEN"
echo "     Value: <你的 Telegram Bot Token>"
echo ""
echo "   - Name: WEBHOOK_SECRET"
echo "     Value: ${WEBHOOK_SECRET}"
echo ""
echo "   - Name: MYSQL_PASSWORD"
echo "     Value: <你的 MySQL 密码>"
echo ""
echo "   【Variables】（点击 'New variable'）"
echo "   - Name: ADMIN_USER_ID"
echo "     Value: <你的 Telegram ID>"
echo ""
echo "   - Name: MYSQL_HOST"
echo "     Value: <你的 MySQL 主机>"
echo ""
echo "   - Name: MYSQL_USER"
echo "     Value: <你的 MySQL 用户名>"
echo ""
echo "   - Name: MYSQL_DATABASE"
echo "     Value: tgbot_verify"
echo ""
echo "   - Name: WEBHOOK_URL"
echo "     Value: https://<你的用户名>-<Space名称>.hf.space"
echo ""
echo "   - Name: PORT"
echo "     Value: 7860"
echo ""
echo "============================================"
echo "🎉 部署准备完成！"
echo "============================================"
echo ""
echo "5️⃣  等待部署完成（约 5-10 分钟）"
echo "   在 Space 页面可以看到构建日志"
echo ""
echo "6️⃣  验证部署："
echo "   访问: https://<你的用户名>-<Space名称>.hf.space/health"
echo "   应该看到: {\"status\": \"ok\", \"bot_running\": true}"
echo ""
echo "7️⃣  测试 Bot："
echo "   在 Telegram 中搜索你的 Bot，发送 /start"
echo ""
echo -e "${GREEN}✅ 全部完成！祝使用愉快！${NC}"
echo ""
