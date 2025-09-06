#!/usr/bin/env python3
"""
简单测试话题添加功能
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

async def test_simple_topic():
    """测试简单的话题添加"""
    logger.info("\n" + "="*60)
    logger.info("🧪 测试话题添加功能")
    logger.info("="*60)
    
    config = XHSConfig()
    client = XHSClient(config)
    
    # 强制关闭无头模式
    client.browser_manager.headless = False
    
    # 获取测试图片
    test_images_dir = Path(__file__).parent / "test_images"
    test_images = [str(test_images_dir / "tesla-optimus-next-gen-reveal.jpg")]
    
    # 创建测试笔记 - 只测试话题
    note = XHSNote(
        title=f"话题测试 {datetime.now().strftime('%H:%M')}",
        content="测试话题功能",
        images=test_images[:1],
        topics=["测试", "自动化"],  # 只用2个话题测试
        dry_run=True
    )
    
    try:
        logger.info("📋 测试配置：")
        logger.info(f"   - 话题: {note.topics}")
        logger.info(f"   - DRY-RUN模式: {note.dry_run}")
        
        result = await client.publish_note(note)
        
        if result.success:
            logger.info("✅ 测试成功！")
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
    success = await test_simple_topic()
    
    if success:
        logger.info("\n🎉 话题测试通过！")
    else:
        logger.error("\n❌ 话题测试失败")

if __name__ == "__main__":
    asyncio.run(main())