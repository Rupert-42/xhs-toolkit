#!/usr/bin/env python
"""
直接测试发布功能，不通过MCP服务器
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# 导入所需模块
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.xiaohongshu.models import XHSNote
from src.xiaohongshu.client import XHSClient
from src.core.config import XHSConfig


async def test_direct_publish():
    """直接测试发布功能"""
    logger.info("="*60)
    logger.info("🚀 直接发布测试（不通过MCP）")
    logger.info("="*60)
    
    try:
        # 创建配置和客户端
        config = XHSConfig()
        client = XHSClient(config)
        
        # 准备测试笔记
        current_time = datetime.now().strftime('%m月%d日 %H:%M')
        
        logger.info("📝 创建测试笔记...")
        note = await XHSNote.async_smart_create(
            title=f"🧪 工具测试 - {current_time}",
            content=f"""这是xhs-toolkit的功能测试笔记

📅 发布时间: {current_time}
🔧 版本: 1.3.0

✨ 新功能亮点:
1️⃣ 支持网络图片URL
2️⃣ 智能路径解析
3️⃣ 增强日志输出

🎯 本次测试验证:
- 网络图片自动下载 ✅
- 图片处理流程 ✅
- 发布功能正常 ✅

使用的测试图片来自Lorem Picsum随机图片服务

#小红书工具 #自动化测试 #技术分享""",
            images=[
                "https://picsum.photos/seed/test1/600/400",
                "https://picsum.photos/seed/test2/600/400",
                "https://picsum.photos/seed/test3/600/400"
            ],
            topics=["技术分享", "自动化测试", "开发工具"],
            location="测试环境"
        )
        
        logger.info(f"✅ 笔记创建成功")
        logger.info(f"  标题: {note.title}")
        logger.info(f"  图片数: {len(note.images) if note.images else 0}")
        logger.info(f"  话题: {note.topics}")
        
        # 检查是否有cookies
        cookies = client.cookie_manager.load_cookies()
        if not cookies:
            logger.warning("⚠️ 未找到cookies，需要先登录")
            logger.info("请运行: ./xhs login 进行登录")
            return
        
        logger.info(f"✅ 找到 {len(cookies)} 个cookies")
        
        # 发布笔记
        logger.info("\n📤 开始发布笔记...")
        result = await client.publish_note(note)
        
        # 显示结果
        if result.success:
            logger.info(f"🎉 发布成功!")
            logger.info(f"  消息: {result.message}")
            if result.final_url:
                logger.info(f"  笔记链接: {result.final_url}")
        else:
            logger.error(f"❌ 发布失败: {result.message}")
            if result.error_type:
                logger.error(f"  错误类型: {result.error_type}")
    
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    logger.info("\n" + "="*60)
    logger.info("测试结束")
    logger.info("="*60)


async def main():
    """主函数"""
    logger.info("🌺 小红书直接发布测试")
    logger.info(f"⏰ 开始时间: {datetime.now()}")
    
    logger.info("\n⚠️ 注意:")
    logger.info("1. 请确保已经登录小红书")
    logger.info("2. 本测试将直接发布笔记到小红书")
    logger.info("3. 发布过程需要1-2分钟\n")
    
    await test_direct_publish()
    
    logger.info(f"\n✨ 结束时间: {datetime.now()}")


if __name__ == "__main__":
    asyncio.run(main())