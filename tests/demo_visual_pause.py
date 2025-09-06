#!/usr/bin/env python3
"""
可视化演示发布流程，在最终发布前暂停
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

async def demo_publish_with_pause():
    """演示发布流程，在点击发布按钮前暂停"""
    logger.info("\n" + "="*60)
    logger.info("🎬 开始可视化演示发布流程")
    logger.info("="*60)
    
    config = XHSConfig()
    client = XHSClient(config)
    
    # 强制关闭无头模式，显示浏览器
    client.browser_manager.headless = False
    logger.info("✅ 已设置为可视化模式（关闭无头）")
    
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
    
    logger.info(f"📸 使用测试图片: {valid_images}")
    
    # 创建演示笔记
    note = XHSNote(
        title=f"演示 {datetime.now().strftime('%H:%M')}",
        content=f"""
🎬 这是一个可视化演示
📝 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

演示功能：
• 📸 多图片上传
• 🏷️ 话题标签
• 🔒 可见范围设置
• ⏸️ 发布前暂停

#演示 #测试 #自动化
        """.strip(),
        images=valid_images[:2],  # 使用2张图片
        topics=["演示", "自动化测试", "小红书工具"],
        visibility="private",  # 设置为仅自己可见
        dry_run=True  # 使用dry_run模式，不会真正点击发布
    )
    
    try:
        logger.info("🚀 开始执行发布流程...")
        logger.info("📌 设置为仅自己可见")
        logger.info("📌 DRY-RUN模式：将在发布前停止")
        
        # 在发布前添加暂停提示
        logger.info("\n" + "="*60)
        logger.info("⏸️  脚本将在点击发布按钮前暂停")
        logger.info("📌 你可以检查页面上的所有内容")
        logger.info("📌 由于启用了dry_run，不会真正发布")
        logger.info("="*60 + "\n")
        
        result = await client.publish_note(note)
        
        if result.success:
            logger.info("\n" + "="*60)
            logger.info("✅ 演示成功完成！")
            logger.info(f"📝 消息: {result.message}")
            # 等待时间已经在client.py的dry_run模式中处理了
            return True
        else:
            logger.error(f"❌ 演示失败: {result.message}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 演示出错: {e}")
        import traceback
        logger.error(f"错误详情:\n{traceback.format_exc()}")
        
        # 出错时也保持浏览器打开让你查看
        logger.info("⏰ 出错了，保持浏览器打开20秒供检查...")
        await asyncio.sleep(20)
        return False
    finally:
        # 浏览器关闭已经在client.py的finally块中处理
        pass

async def main():
    """主函数"""
    logger.info("🎭 小红书发布流程可视化演示")
    logger.info("📌 功能：关闭无头模式，发布前暂停")
    
    # 检查cookies
    config = XHSConfig()
    from src.auth.cookie_manager import CookieManager
    cookie_manager = CookieManager(config)
    cookies = cookie_manager.load_cookies()
    
    if not cookies:
        logger.error("❌ 未找到有效的cookies，请先登录")
        logger.info("💡 提示：运行 python tests/test_login.py 进行登录")
        return
    
    logger.info("✅ 找到有效的cookies")
    
    # 运行演示
    success = await demo_publish_with_pause()
    
    if success:
        logger.info("\n🎉 演示成功！")
        logger.info("📌 由于启用了dry_run模式，笔记未实际发布")
        logger.info("📌 你可以在dry_run_preview.png查看截图")
    else:
        logger.error("\n❌ 演示失败")

if __name__ == "__main__":
    asyncio.run(main())