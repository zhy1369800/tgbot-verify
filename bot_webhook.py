# -*- coding: utf-8 -*-
"""Telegram 机器人 - Webhook 模式
适用于 Hugging Face Spaces、Railway、Render 等云平台部署
"""
import logging
import os
from functools import partial
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, HTTPException
from telegram import Update
from telegram.ext import Application, CommandHandler

from config import BOT_TOKEN, ADMIN_USER_ID
from database_mysql import Database
from handlers.user_commands import (
    start_command,
    about_command,
    help_command,
    balance_command,
    checkin_command,
    invite_command,
    use_command,
)
from handlers.verify_commands import (
    verify_command,
    verify2_command,
    verify3_command,
    verify4_command,
    getV4Code_command,
)
from handlers.admin_commands import (
    addbalance_command,
    block_command,
    white_command,
    blacklist_command,
    genkey_command,
    listkeys_command,
    broadcast_command,
)

# 配置日志
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# 从环境变量获取配置
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")  # 你的公网 URL，如: https://your-app.hf.space
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your-secret-token-here")  # Webhook 安全令牌
PORT = int(os.getenv("PORT", "7860"))  # Hugging Face 默认端口是 7860

# 全局变量
db = None
application = None


async def error_handler(update: object, context) -> None:
    """全局错误处理"""
    logger.exception("处理更新时发生异常: %s", context.error, exc_info=context.error)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global db, application

    # 启动时初始化
    logger.info("🚀 初始化数据库...")
    db = Database()

    logger.info("🤖 初始化 Telegram Bot...")
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    # 注册用户命令
    application.add_handler(CommandHandler("start", partial(start_command, db=db)))
    application.add_handler(CommandHandler("about", partial(about_command, db=db)))
    application.add_handler(CommandHandler("help", partial(help_command, db=db)))
    application.add_handler(CommandHandler("balance", partial(balance_command, db=db)))
    application.add_handler(CommandHandler("qd", partial(checkin_command, db=db)))
    application.add_handler(CommandHandler("invite", partial(invite_command, db=db)))
    application.add_handler(CommandHandler("use", partial(use_command, db=db)))

    # 注册验证命令
    application.add_handler(CommandHandler("verify", partial(verify_command, db=db)))
    application.add_handler(CommandHandler("verify2", partial(verify2_command, db=db)))
    application.add_handler(CommandHandler("verify3", partial(verify3_command, db=db)))
    application.add_handler(CommandHandler("verify4", partial(verify4_command, db=db)))
    application.add_handler(CommandHandler("getV4Code", partial(getV4Code_command, db=db)))

    # 注册管理员命令
    application.add_handler(CommandHandler("addbalance", partial(addbalance_command, db=db)))
    application.add_handler(CommandHandler("block", partial(block_command, db=db)))
    application.add_handler(CommandHandler("white", partial(white_command, db=db)))
    application.add_handler(CommandHandler("blacklist", partial(blacklist_command, db=db)))
    application.add_handler(CommandHandler("genkey", partial(genkey_command, db=db)))
    application.add_handler(CommandHandler("listkeys", partial(listkeys_command, db=db)))
    application.add_handler(CommandHandler("broadcast", partial(broadcast_command, db=db)))

    # 注册错误处理器
    application.add_error_handler(error_handler)

    # 初始化 Bot
    await application.initialize()
    await application.start()

    # 设置 Webhook
    if WEBHOOK_URL:
        webhook_path = f"{WEBHOOK_URL}/webhook/{WEBHOOK_SECRET}"
        logger.info(f"🌐 设置 Webhook: {webhook_path}")
        await application.bot.set_webhook(
            url=webhook_path,
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        logger.info("✅ Webhook 设置成功！")
    else:
        logger.warning("⚠️ 未设置 WEBHOOK_URL 环境变量，Webhook 未启用！")

    logger.info("🎉 机器人启动完成！")

    yield

    # 关闭时清理
    logger.info("🛑 正在关闭机器人...")
    await application.stop()
    await application.shutdown()
    logger.info("👋 机器人已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="Telegram SheerID Bot - Webhook",
    description="自动完成 SheerID 学生/教师认证的 Telegram 机器人",
    version="2.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """健康检查端点"""
    return {
        "status": "running",
        "mode": "webhook",
        "bot": "SheerID Auto Verify Bot",
        "version": "2.0.0"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "bot_running": application is not None}


@app.post("/webhook/{token}")
async def webhook(token: str, request: Request):
    """
    处理 Telegram Webhook 请求

    URL 格式: https://your-domain.com/webhook/{WEBHOOK_SECRET}
    """
    # 验证 token
    if token != WEBHOOK_SECRET:
        logger.warning(f"⚠️ 收到无效的 webhook token: {token}")
        raise HTTPException(status_code=403, detail="Invalid webhook token")

    # 检查 Bot 是否已初始化
    if application is None:
        logger.error("❌ Bot 未初始化！")
        raise HTTPException(status_code=503, detail="Bot not initialized")

    try:
        # 解析 Telegram 更新
        json_data = await request.json()
        update = Update.de_json(json_data, application.bot)

        # 处理更新
        await application.process_update(update)

        return Response(status_code=200)

    except Exception as e:
        logger.exception(f"❌ 处理 webhook 时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/set_webhook")
async def set_webhook_manually(request: Request):
    """
    手动设置 Webhook（仅管理员可用）

    请求体:
    {
        "admin_id": 123456789,
        "webhook_url": "https://your-domain.com"
    }
    """
    try:
        data = await request.json()
        admin_id = data.get("admin_id")
        webhook_url = data.get("webhook_url")

        # 验证管理员
        if admin_id != ADMIN_USER_ID:
            raise HTTPException(status_code=403, detail="Unauthorized")

        if not webhook_url:
            raise HTTPException(status_code=400, detail="webhook_url is required")

        # 设置 Webhook
        webhook_path = f"{webhook_url}/webhook/{WEBHOOK_SECRET}"
        await application.bot.set_webhook(
            url=webhook_path,
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )

        return {
            "status": "success",
            "webhook_url": webhook_path,
            "message": "Webhook 设置成功！"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ 设置 webhook 时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/webhook_info")
async def webhook_info():
    """获取当前 Webhook 信息"""
    try:
        if application is None:
            raise HTTPException(status_code=503, detail="Bot not initialized")

        webhook = await application.bot.get_webhook_info()

        return {
            "url": webhook.url,
            "has_custom_certificate": webhook.has_custom_certificate,
            "pending_update_count": webhook.pending_update_count,
            "last_error_date": webhook.last_error_date,
            "last_error_message": webhook.last_error_message,
            "max_connections": webhook.max_connections,
            "allowed_updates": webhook.allowed_updates,
        }

    except Exception as e:
        logger.exception(f"❌ 获取 webhook 信息时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/webhook")
async def delete_webhook(admin_id: int):
    """删除 Webhook（仅管理员可用）"""
    try:
        # 验证管理员
        if admin_id != ADMIN_USER_ID:
            raise HTTPException(status_code=403, detail="Unauthorized")

        if application is None:
            raise HTTPException(status_code=503, detail="Bot not initialized")

        await application.bot.delete_webhook(drop_pending_updates=True)

        return {
            "status": "success",
            "message": "Webhook 已删除！"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ 删除 webhook 时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 启动 Webhook 服务器，端口: {PORT}")
    uvicorn.run(
        "bot_webhook:app",
        host="0.0.0.0",
        port=PORT,
        log_level="info",
        access_log=True
    )
