#!/usr/bin/env python3
"""
查找并测试可见范围设置按钮
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
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time

setup_logger()
logger = get_logger()

async def find_visibility_settings():
    """查找可见范围设置"""
    logger.info("\n" + "="*60)
    logger.info("🔍 查找可见范围设置按钮")
    logger.info("="*60)
    
    config = XHSConfig()
    client = XHSClient(config)
    
    # 强制关闭无头模式
    client.browser_manager.headless = False
    
    # 获取测试图片
    test_images_dir = Path(__file__).parent / "test_images"
    test_images = [str(test_images_dir / "tesla-optimus-next-gen-reveal.jpg")]
    
    # 创建测试笔记
    note = XHSNote(
        title=f"测试 {datetime.now().strftime('%H:%M')}",
        content="测试可见范围设置",
        images=test_images[:1],
        visibility="private",
        dry_run=True
    )
    
    try:
        # 使用现有的发布流程
        result = await client.publish_note(note)
        
        # 发布流程会自动处理可见范围设置
        if result.success:
            logger.info("✅ 发布流程完成")
        
    except Exception as e:
        logger.error(f"❌ 测试出错: {e}")
        import traceback
        logger.error(f"错误详情:\n{traceback.format_exc()}")
    finally:
        # 浏览器会在client.publish_note的finally块中自动关闭
        pass

async def main():
    """主函数"""
    await find_visibility_settings()

if __name__ == "__main__":
    asyncio.run(main())