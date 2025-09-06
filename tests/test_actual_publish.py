#!/usr/bin/env python3
"""
实际发布测试工具 - 完整执行发布流程
警告：此脚本会实际发布内容到小红书
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.xiaohongshu.client import XHSClient
from src.xiaohongshu.models import XHSNote
from src.core.config import XHSConfig
from src.utils.logger import setup_logger, get_logger
import asyncio

setup_logger()
logger = get_logger()

def get_test_images():
    """获取测试图片"""
    test_images_dir = Path(__file__).parent / "test_images"
    
    # 使用你准备的真实图片
    real_images = [
        test_images_dir / "tesla-optimus-next-gen-reveal.jpg",
        test_images_dir / "image.png"
    ]
    
    # 验证文件存在
    valid_images = []
    for img_path in real_images:
        if img_path.exists():
            logger.info(f"✅ 找到测试图片: {img_path.name}")
            valid_images.append(str(img_path))
        else:
            logger.error(f"❌ 图片不存在: {img_path}")
    
    if not valid_images:
        raise FileNotFoundError("没有找到有效的测试图片")
    
    logger.info(f"📸 准备使用 {len(valid_images)} 张测试图片")
    return valid_images

async def test_actual_publish():
    """
    执行实际的发布测试
    会真正发布内容到小红书
    """
    logger.info("=" * 60)
    logger.info("🚀 开始实际发布测试")
    logger.info("⚠️ 警告：此测试会实际发布内容到小红书！")
    logger.info("=" * 60)
    
    # 初始化客户端
    logger.info("\n📱 初始化小红书客户端...")
    config = XHSConfig()
    client = XHSClient(config)
    
    # 确保浏览器以可视化模式运行
    if hasattr(client, 'browser_manager'):
        client.browser_manager.headless = False
        logger.info("✅ 浏览器已设置为可视化模式")
    
    # 获取测试图片
    test_images = get_test_images()
    
    # 准备发布内容
    test_data = {
        "title": f"测试发布 {datetime.now().strftime('%H:%M')}",
        "content": f"""
📌 这是一条自动化测试笔记
🤖 发布时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🧪 测试目的：验证自动发布功能

测试内容包括：
• 图片上传功能
• 标题填写功能  
• 内容编辑功能
• 话题添加功能
• 自动发布功能

#自动化测试 #开发测试 #小红书工具
        """.strip(),
        "images": test_images,  # 使用多张图片
        "topics": ["测试", "自动化"]
    }
    
    logger.info("\n📝 发布内容:")
    logger.info(f"  标题: {test_data['title']}")
    logger.info(f"  内容长度: {len(test_data['content'])} 字符")
    logger.info(f"  图片数量: {len(test_data['images'])}")
    logger.info(f"  话题: {', '.join(test_data['topics'])}")
    
    try:
        # 检查登录状态
        logger.info("\n🔐 检查登录状态...")
        cookies = client.cookie_manager.load_cookies()
        if not cookies:
            logger.error("❌ 未找到有效的cookies，请先登录")
            return False
        
        logger.info("✅ 已加载cookies")
        
        # 执行发布
        logger.info("\n🚀 开始执行发布...")
        logger.info("👀 请观察浏览器窗口，查看发布过程")
        
        # 创建XHSNote对象
        note = XHSNote(
            title=test_data['title'],
            content=test_data['content'],
            images=test_data['images'],
            topics=test_data['topics']
        )
        
        # 调用客户端的发布方法
        result = await client.publish_note(note)
        
        if result and result.success:
            logger.info("\n" + "=" * 60)
            logger.info("✅ 发布成功！")
            logger.info(f"📝 笔记标题: {result.note_title}")
            logger.info(f"🔗 笔记链接: {result.final_url}")
            logger.info("=" * 60)
            
            # 保存发布结果
            result_data = {
                "test_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "success",
                "note_title": result.note_title,
                "final_url": result.final_url,
                "title": test_data['title'],
                "message": "发布成功"
            }
        else:
            logger.error(f"❌ 发布失败: {result.error_msg if result else '未知错误'}")
            result_data = {
                "test_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "failed",
                "error": result.error_msg if result else "未知错误"
            }
        
        # 保存测试结果
        result_file = Path(__file__).parent / "actual_publish_result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n📊 测试结果已保存到: {result_file}")
        
        return result_data.get("status") == "success"
        
    except Exception as e:
        logger.error(f"❌ 发布过程出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False
        
    finally:
        # 清理资源
        logger.info("\n🧹 清理资源...")
        if hasattr(client, 'browser_manager'):
            try:
                client.browser_manager.close_driver()
                logger.info("✅ 浏览器已关闭")
            except:
                pass

async def main():
    """主函数"""
    logger.info("🎯 小红书实际发布测试工具")
    logger.info("⚠️ 注意：此工具会实际发布内容到小红书平台")
    logger.info("=" * 60)
    
    # 确认执行
    logger.info("\n请确认是否要执行实际发布测试？")
    logger.info("此操作会在你的小红书账号上发布一条测试笔记")
    
    response = input("\n输入 'yes' 继续，其他任意键取消: ").strip().lower()
    
    if response != 'yes':
        logger.info("❌ 测试已取消")
        return
    
    # 执行测试
    success = await test_actual_publish()
    
    if success:
        logger.info("\n🎉 测试完成！笔记已成功发布到小红书")
        logger.info("📱 请打开小红书APP查看发布的内容")
    else:
        logger.error("\n❌ 测试失败，请查看日志了解详情")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())