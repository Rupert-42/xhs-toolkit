#!/usr/bin/env python3
"""
测试新功能：dry-run、话题标签、可见范围
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

def get_test_images():
    """获取测试图片"""
    test_images_dir = Path(__file__).parent / "test_images"
    
    # 使用真实图片
    real_images = [
        test_images_dir / "tesla-optimus-next-gen-reveal.jpg",
        test_images_dir / "image.png"
    ]
    
    valid_images = []
    for img_path in real_images:
        if img_path.exists():
            valid_images.append(str(img_path))
    
    return valid_images[:1]  # 只用一张图片，加快测试

async def test_dry_run():
    """测试dry-run功能：不实际发布"""
    logger.info("\n" + "="*60)
    logger.info("🧪 测试1: DRY-RUN功能测试")
    logger.info("="*60)
    
    config = XHSConfig()
    client = XHSClient(config)
    
    # 确保可视化模式
    client.browser_manager.headless = False
    
    test_images = get_test_images()
    
    # 创建测试笔记，启用dry_run
    note = XHSNote(
        title=f"DryRun测试 {datetime.now().strftime('%H:%M')}",
        content=f"""
🧪 这是一个DRY-RUN测试
📝 测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

功能验证：
• ✅ 完成所有编辑操作
• ❌ 不点击发布按钮
• 📸 保存预览截图

#测试 #DryRun
        """.strip(),
        images=test_images,
        topics=["测试", "开发"],
        dry_run=True  # 启用dry-run模式
    )
    
    try:
        logger.info("📌 DRY-RUN模式已启用")
        result = await client.publish_note(note)
        
        if result.success:
            logger.info("✅ DRY-RUN测试成功！")
            logger.info(f"   消息: {result.message}")
            return True
        else:
            logger.error(f"❌ DRY-RUN测试失败: {result.message}")
            return False
            
    except Exception as e:
        logger.error(f"❌ DRY-RUN测试出错: {e}")
        return False
    finally:
        client.browser_manager.close_driver()

async def test_private_visibility():
    """测试仅自己可见功能"""
    logger.info("\n" + "="*60)
    logger.info("🧪 测试2: 仅自己可见功能测试")
    logger.info("="*60)
    
    config = XHSConfig()
    client = XHSClient(config)
    
    # 确保可视化模式
    client.browser_manager.headless = False
    
    test_images = get_test_images()
    
    # 创建测试笔记，设置为仅自己可见，并启用dry-run
    note = XHSNote(
        title=f"私密测试 {datetime.now().strftime('%H:%M')}",
        content=f"""
🔒 这是一个私密笔记测试
📝 测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

功能验证：
• 设置为仅自己可见
• 验证可见范围设置

#私密 #测试
        """.strip(),
        images=test_images,
        topics=["私密", "测试"],
        visibility="private",  # 设置为仅自己可见
        dry_run=True  # 同时启用dry-run，避免实际发布
    )
    
    try:
        logger.info("🔒 设置为仅自己可见")
        result = await client.publish_note(note)
        
        if result.success:
            logger.info("✅ 私密笔记测试成功！")
            return True
        else:
            logger.error(f"❌ 私密笔记测试失败: {result.message}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 私密笔记测试出错: {e}")
        return False
    finally:
        client.browser_manager.close_driver()

async def test_topics():
    """测试话题标签功能"""
    logger.info("\n" + "="*60)
    logger.info("🧪 测试3: 话题标签功能测试")
    logger.info("="*60)
    
    config = XHSConfig()
    client = XHSClient(config)
    
    # 确保可视化模式
    client.browser_manager.headless = False
    
    test_images = get_test_images()
    
    # 创建测试笔记，添加多个话题
    note = XHSNote(
        title=f"话题测试 {datetime.now().strftime('%H:%M')}",
        content=f"""
🏷️ 这是一个话题标签测试
📝 测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

测试多个话题标签：
• 自动化测试
• 开发工具
• 小红书API
        """.strip(),
        images=test_images,
        topics=["自动化测试", "开发工具", "小红书"],  # 多个话题
        dry_run=True  # 启用dry-run
    )
    
    try:
        logger.info(f"🏷️ 添加话题: {note.topics}")
        result = await client.publish_note(note)
        
        if result.success:
            logger.info("✅ 话题标签测试成功！")
            return True
        else:
            logger.error(f"❌ 话题标签测试失败: {result.message}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 话题标签测试出错: {e}")
        return False
    finally:
        client.browser_manager.close_driver()

async def main():
    """主测试函数"""
    logger.info("🚀 开始测试新功能")
    logger.info("📌 包含: dry-run、可见范围、话题标签")
    
    # 检查cookies
    config = XHSConfig()
    from src.auth.cookie_manager import CookieManager
    cookie_manager = CookieManager(config)
    cookies = cookie_manager.load_cookies()
    
    if not cookies:
        logger.error("❌ 未找到有效的cookies，请先登录")
        return
    
    # 执行测试
    tests = [
        ("DRY-RUN功能", test_dry_run),
        ("仅自己可见功能", test_private_visibility),
        ("话题标签功能", test_topics)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            logger.info(f"\n🔄 运行测试: {test_name}")
            success = await test_func()
            results.append((test_name, success))
            
            # 测试间隔
            await asyncio.sleep(3)
            
        except Exception as e:
            logger.error(f"❌ 测试 {test_name} 失败: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    logger.info("\n" + "="*60)
    logger.info("📊 测试结果汇总")
    logger.info("="*60)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        logger.info(f"{status} - {test_name}")
    
    # 统计
    passed = sum(1 for _, success in results if success)
    total = len(results)
    logger.info(f"\n🎯 通过率: {passed}/{total} ({passed*100//total}%)")
    
    if passed == total:
        logger.info("🎉 所有测试通过！")
    else:
        logger.warning(f"⚠️ 有 {total-passed} 个测试失败")

if __name__ == "__main__":
    asyncio.run(main())