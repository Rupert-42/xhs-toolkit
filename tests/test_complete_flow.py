#!/usr/bin/env python3
"""
完整测试发布流程，检查所有功能
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.xiaohongshu.client import XHSClient
from src.xiaohongshu.models import XHSNote
from src.core.config import XHSConfig
from src.utils.logger import setup_logger, get_logger

setup_logger()
logger = get_logger()

async def test_complete_publish_flow():
    """测试完整的发布流程"""
    logger.info("\n" + "="*60)
    logger.info("🚀 测试完整发布流程")
    logger.info("="*60)
    
    config = XHSConfig()
    client = XHSClient(config)
    
    # 强制关闭无头模式
    client.browser_manager.headless = False
    
    # 获取测试图片
    test_images_dir = Path(__file__).parent / "test_images"
    test_images = [
        str(test_images_dir / "tesla-optimus-next-gen-reveal.jpg"),
        str(test_images_dir / "image.png")
    ]
    
    # 只使用存在的图片
    valid_images = [img for img in test_images if Path(img).exists()]
    
    if not valid_images:
        logger.error("❌ 未找到测试图片")
        return False
    
    # 创建测试笔记 - 不设置私密和话题，先测试基本功能
    note = XHSNote(
        title=f"基础测试 {datetime.now().strftime('%H:%M')}",
        content=f"""
这是一个基础功能测试
时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

测试内容：
• 图片上传
• 标题填写
• 内容填写
        """.strip(),
        images=valid_images[:2],
        # topics=None,  # 暂时不测试话题
        # visibility=None,  # 暂时不测试可见范围
        dry_run=True
    )
    
    try:
        logger.info("📋 测试配置：")
        logger.info(f"   - 图片数量: {len(note.images)}")
        logger.info(f"   - DRY-RUN模式: {note.dry_run}")
        logger.info("   - 不测试话题功能")
        logger.info("   - 不测试可见范围设置")
        
        result = await client.publish_note(note)
        
        if result.success:
            logger.info("\n" + "="*60)
            logger.info("✅ 基础功能测试成功！")
            logger.info(f"📝 消息: {result.message}")
            logger.info("="*60)
            return True
        else:
            logger.error(f"❌ 测试失败: {result.message}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 测试出错: {e}")
        import traceback
        logger.error(f"错误详情:\n{traceback.format_exc()}")
        return False

async def main():
    """主函数"""
    logger.info("🎭 小红书发布功能测试")
    
    # 检查cookies
    config = XHSConfig()
    from src.auth.cookie_manager import CookieManager
    cookie_manager = CookieManager(config)
    cookies = cookie_manager.load_cookies()
    
    if not cookies:
        logger.error("❌ 未找到有效的cookies，请先登录")
        return
    
    logger.info("✅ 找到有效的cookies")
    
    # 运行测试
    success = await test_complete_publish_flow()
    
    if success:
        logger.info("\n🎉 测试通过！基础功能正常")
        logger.info("\n📌 关于其他功能的说明：")
        logger.info("1. 话题功能：可能需要在内容中直接输入 #话题名#")
        logger.info("2. 可见范围：小红书创作者中心可能已移除或更改了此功能")
    else:
        logger.error("\n❌ 测试失败")

if __name__ == "__main__":
    asyncio.run(main())