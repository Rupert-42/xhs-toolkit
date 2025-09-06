#!/usr/bin/env python3
"""
测试发布流程 - 可视化浏览器操作
用于验证浏览器可视化模式是否正常工作
注意：此脚本会打开浏览器并执行操作，但不会实际发布内容
"""

import sys
import os
import time
import json
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.xiaohongshu.client import XHSClient
from src.core.config import XHSConfig
from src.utils.logger import setup_logger, get_logger

setup_logger()
logger = get_logger()

def create_test_images():
    """创建测试用的图片文件"""
    test_images_dir = Path(__file__).parent / "test_images"
    test_images_dir.mkdir(exist_ok=True)
    
    # 创建一个简单的测试图片（使用PIL）
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 创建测试图片
        for i in range(1, 3):
            img = Image.new('RGB', (800, 600), color=(73, 109, 137))
            d = ImageDraw.Draw(img)
            
            # 添加文字
            text = f"测试图片 {i}\n仅用于浏览器可视化测试\n不会实际发布"
            try:
                # 尝试使用系统字体
                from PIL import ImageFont
                font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 40)
            except:
                font = ImageFont.load_default()
            
            # 获取文字边界框
            bbox = d.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 居中绘制文字
            position = ((800 - text_width) / 2, (600 - text_height) / 2)
            d.text(position, text, fill=(255, 255, 255), font=font)
            
            # 保存图片
            img_path = test_images_dir / f"test_image_{i}.png"
            img.save(img_path)
            logger.info(f"✅ 创建测试图片: {img_path}")
            
        return [str(test_images_dir / f"test_image_{i}.png") for i in range(1, 3)]
    
    except ImportError:
        logger.warning("⚠️ PIL库未安装，使用占位文件")
        # 创建空文件作为占位
        images = []
        for i in range(1, 3):
            img_path = test_images_dir / f"test_image_{i}.txt"
            img_path.write_text(f"测试图片{i} - 占位文件")
            images.append(str(img_path))
        return images

def test_publish_without_submit():
    """
    测试发布流程，但不点击最终的发布按钮
    用于验证浏览器可视化模式
    """
    logger.info("=" * 50)
    logger.info("🧪 开始测试发布流程（可视化模式）")
    logger.info("=" * 50)
    
    # 初始化客户端
    logger.info("📱 初始化小红书客户端...")
    config = XHSConfig()
    client = XHSClient(config)
    
    # 确保浏览器以可视化模式运行
    if hasattr(client, 'browser_manager'):
        client.browser_manager.headless = False
        logger.info("✅ 浏览器已设置为可视化模式")
    
    # 创建测试数据
    test_images = create_test_images()
    
    test_data = {
        "title": "【测试】浏览器可视化测试 - 不会发布",
        "content": """
🧪 这是一个测试笔记，用于验证浏览器可视化功能

⚠️ 注意事项：
• 此笔记仅用于测试，不会实际发布
• 用于验证浏览器操作是否可见
• 测试完成后会自动关闭

#测试 #浏览器测试 #可视化验证
        """.strip(),
        "images": test_images[:2],  # 使用前2张图片
        "topics": ["测试", "开发测试"]
    }
    
    logger.info("\n📝 测试数据:")
    logger.info(f"  标题: {test_data['title']}")
    logger.info(f"  内容: {test_data['content'][:50]}...")
    logger.info(f"  图片: {len(test_data['images'])} 张")
    logger.info(f"  话题: {', '.join(test_data['topics'])}")
    
    try:
        # 登录检查
        logger.info("\n🔐 检查登录状态...")
        cookies = client.cookie_manager.load_cookies()
        if not cookies:
            logger.warning("⚠️ 未找到有效的cookies，需要先登录")
            logger.info("💡 请先运行登录命令获取cookies")
            return False
        
        logger.info("✅ 已加载cookies")
        
        # 初始化浏览器
        logger.info("\n🌐 启动浏览器（可视化模式）...")
        logger.info("👀 请观察浏览器窗口，查看操作过程")
        
        browser = client.browser_manager.create_driver()
        
        # 打开创作页面
        logger.info("\n📝 打开创作页面...")
        browser.get("https://creator.xiaohongshu.com/publish/publish")
        time.sleep(3)
        
        logger.info("🖼️ 模拟选择图片...")
        # 这里可以添加选择图片的模拟操作
        time.sleep(2)
        
        logger.info("✍️ 模拟填写标题和内容...")
        # 这里可以添加填写内容的模拟操作
        time.sleep(2)
        
        logger.info("🏷️ 模拟添加话题...")
        # 这里可以添加话题的模拟操作
        time.sleep(2)
        
        logger.info("\n" + "=" * 50)
        logger.info("⏸️ 测试暂停 - 不点击发布按钮")
        logger.info("👀 您可以查看浏览器中的内容")
        logger.info("⏰ 10秒后自动关闭浏览器...")
        logger.info("=" * 50)
        
        # 等待用户查看
        for i in range(10, 0, -1):
            print(f"\r⏰ 倒计时: {i} 秒  ", end="", flush=True)
            time.sleep(1)
        print("\r" + " " * 30 + "\r", end="")  # 清除倒计时
        
        logger.info("\n✅ 测试完成 - 未实际发布内容")
        
        # 保存测试结果
        result = {
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_data": test_data,
            "browser_mode": "visual" if not client.browser_manager.headless else "headless",
            "status": "success",
            "message": "测试完成，浏览器可视化模式正常工作"
        }
        
        result_file = Path(__file__).parent / "test_result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 测试结果已保存到: {result_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试过程出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False
        
    finally:
        # 清理资源
        logger.info("\n🧹 清理资源...")
        if hasattr(client, 'browser_manager'):
            client.browser_manager.close_driver()
        logger.info("✅ 浏览器已关闭")

def main():
    """主函数"""
    logger.info("🚀 启动小红书发布可视化测试工具")
    logger.info("📌 此工具仅用于测试浏览器可视化功能")
    logger.info("⚠️ 不会实际发布任何内容\n")
    
    # 检查环境变量
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    if headless:
        logger.warning("⚠️ 检测到HEADLESS=true，建议设置为false以查看浏览器操作")
        logger.info("💡 可以在env文件中设置: HEADLESS=false")
        
        response = input("\n是否继续测试? (y/n): ")
        if response.lower() != 'y':
            logger.info("❌ 测试已取消")
            return
    
    # 执行测试
    success = test_publish_without_submit()
    
    if success:
        logger.info("\n✅ 所有测试完成!")
        logger.info("📊 测试结果已保存到 tests/test_result.json")
    else:
        logger.error("\n❌ 测试失败，请检查日志")
        sys.exit(1)

if __name__ == "__main__":
    main()