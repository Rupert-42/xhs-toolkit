#!/usr/bin/env python3
"""
专门测试emoji话题输入功能的脚本
"""

import asyncio
import sys
from pathlib import Path
import os

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.xiaohongshu.refactored_client import RefactoredXHSClient
from src.core.browser import ChromeDriverManager
from src.core.config import XHSConfig
from src.utils.logger import get_logger
from selenium.webdriver.common.by import By

logger = get_logger(__name__)


class EmojiTopicTester:
    """Emoji话题测试器"""
    
    def __init__(self):
        self.browser_manager = None
        self.client = None
        self.publisher = None
        self.driver = None
        
    async def setup(self):
        """初始化测试环境"""
        logger.info("🚀 初始化测试环境...")
        
        # 初始化配置和浏览器管理器
        config = XHSConfig()
        self.browser_manager = ChromeDriverManager(config)
        self.browser_manager.create_driver()
        self.driver = self.browser_manager.driver
        
        # 初始化客户端和发布器
        self.client = RefactoredXHSClient(self.browser_manager)
        self.publisher = self.client.get_publisher()
        
        logger.info("✅ 测试环境初始化完成")
        
    async def teardown(self):
        """清理测试环境"""
        if self.browser_manager:
            self.browser_manager.close_driver()
        logger.info("✅ 测试环境清理完成")
    
    async def prepare_page_for_input(self):
        """准备页面以显示输入框"""
        logger.info("🔧 准备页面以显示输入框...")
        
        try:
            # 导航到发布页面
            logger.info("📍 导航到发布页面...")
            await self.publisher._navigate_to_publish_page()
            await asyncio.sleep(5)  # 等待页面完全加载
            
            # 点击图文发布选项
            try:
                logger.info("🖼️ 点击图文发布选项...")
                image_tabs = self.driver.find_elements(By.CSS_SELECTOR, ".creator-tab")
                for tab in image_tabs:
                    if "图文" in tab.text or "上传图文" in tab.text:
                        tab.click()
                        logger.info("✅ 成功点击图文发布选项")
                        await asyncio.sleep(2)
                        break
            except Exception as e:
                logger.debug(f"点击图文发布选项失败: {e}")
            
            # 上传临时图片
            try:
                logger.info("📷 上传临时图片...")
                temp_image_path = "/tmp/test_image.jpg"
                
                from PIL import Image
                img = Image.new('RGB', (1, 1), color='white')
                img.save(temp_image_path)
                
                file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                if file_inputs:
                    file_inputs[0].send_keys(temp_image_path)
                    await asyncio.sleep(5)  # 等待上传完成
                    
                    if os.path.exists(temp_image_path):
                        os.remove(temp_image_path)
                else:
                    logger.warning("❌ 未找到文件上传框")
                    
            except Exception as e:
                logger.error(f"上传图片失败: {e}")
            
            logger.info("✅ 页面准备完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 页面准备失败: {e}")
            return False
    
    async def test_emoji_topics(self):
        """测试emoji话题输入功能"""
        logger.info("\n" + "="*80)
        logger.info("🏷️ 开始 Emoji 话题输入功能测试")
        logger.info("="*80)
        
        try:
            # 准备页面
            if not await self.prepare_page_for_input():
                logger.error("❌ 页面准备失败，无法继续测试")
                return False
            
            # 再次等待页面稳定
            await asyncio.sleep(3)
            
            # 测试emoji话题
            logger.info("\n🧪 测试包含emoji的话题...")
            topics = ["测试😊", "美食🍔", "旅行✈️"]
            logger.info(f"   输入话题: {topics}")
            
            try:
                # 使用content_filler的话题填写功能
                success = await self.publisher.content_filler.fill_topics(topics)
                
                if success:
                    logger.info("   ✅ 话题输入成功")
                else:
                    logger.error("   ❌ 话题输入失败")
                
                # 等待处理完成
                await asyncio.sleep(5)
                
                # 验证话题是否成功添加
                logger.info("\n🔍 验证话题添加结果...")
                current_topics = await self.publisher.content_filler.get_current_topics()
                logger.info(f"   检测到的话题: {current_topics}")
                
                # 检查页面上的话题元素
                logger.info("\n📊 检查页面上的话题元素...")
                topic_elements = self.driver.find_elements(By.CSS_SELECTOR, "a.mention, .mention, [class*='mention']")
                if topic_elements:
                    logger.info(f"   找到 {len(topic_elements)} 个话题元素:")
                    for i, elem in enumerate(topic_elements[:5]):  # 只显示前5个
                        try:
                            text = elem.text
                            class_attr = elem.get_attribute("class")
                            logger.info(f"     话题{i+1}: '{text}' (class: {class_attr})")
                        except:
                            logger.debug(f"     话题{i+1}: 获取属性失败")
                else:
                    logger.warning("   ❌ 未找到话题元素")
                
                # 最终等待，让用户观察结果
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"   ❌ 话题测试过程出错: {e}")
                import traceback
                logger.error(traceback.format_exc())
            
            logger.info("\n" + "="*80)
            logger.info("📊 话题测试完成")
            logger.info("="*80)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 测试过程出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False


async def main():
    """主函数"""
    tester = EmojiTopicTester()
    
    try:
        # 初始化
        await tester.setup()
        
        # 运行测试
        success = await tester.test_emoji_topics()
        
        if success:
            logger.info("\n🎉 Emoji话题测试完成！")
        else:
            logger.info("\n⚠️ Emoji话题测试遇到问题，请检查日志")
    
    except KeyboardInterrupt:
        logger.info("\n⚠️ 用户中断测试")
    except Exception as e:
        logger.error(f"❌ 测试过程出错: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # 清理
        await tester.teardown()
        logger.info("\n👋 测试结束")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())