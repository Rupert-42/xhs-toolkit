#!/usr/bin/env python3
"""
交互式 Emoji 输入功能测试脚本

先与页面交互以显示输入框，然后测试emoji输入功能
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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = get_logger(__name__)


class InteractiveEmojiTester:
    """交互式Emoji输入测试器"""
    
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
            
            # 尝试点击图文发布选项（如果存在）
            try:
                logger.info("🖼️ 尝试点击图文发布选项...")
                image_tabs = self.driver.find_elements(By.CSS_SELECTOR, ".creator-tab")
                for tab in image_tabs:
                    if "图文" in tab.text or "上传图文" in tab.text:
                        tab.click()
                        logger.info("✅ 成功点击图文发布选项")
                        await asyncio.sleep(2)
                        break
            except Exception as e:
                logger.debug(f"点击图文发布选项失败: {e}")
            
            # 尝试创建一个临时图片文件以触发上传界面
            try:
                logger.info("📷 创建临时图片文件以触发界面...")
                # 创建一个简单的1x1像素图片
                temp_image_path = "/tmp/test_image.jpg"
                
                from PIL import Image
                img = Image.new('RGB', (1, 1), color='white')
                img.save(temp_image_path)
                
                # 查找文件上传输入框
                file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                if file_inputs:
                    logger.info("📁 找到文件上传框，上传临时图片...")
                    file_inputs[0].send_keys(temp_image_path)
                    await asyncio.sleep(5)  # 等待上传完成
                    logger.info("✅ 图片上传完成")
                    
                    # 清理临时文件
                    if os.path.exists(temp_image_path):
                        os.remove(temp_image_path)
                else:
                    logger.warning("❌ 未找到文件上传框")
                    
            except Exception as e:
                logger.error(f"创建临时图片或上传失败: {e}")
            
            logger.info("✅ 页面准备完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 页面准备失败: {e}")
            return False
    
    async def test_emoji_inputs(self):
        """测试emoji输入功能"""
        logger.info("\n" + "="*80)
        logger.info("🎯 开始 Emoji 输入功能测试")
        logger.info("="*80)
        
        try:
            # 准备页面
            if not await self.prepare_page_for_input():
                logger.error("❌ 页面准备失败，无法继续测试")
                return False
            
            # 再次等待页面稳定
            await asyncio.sleep(3)
            
            # 测试1: 标题输入框调试
            logger.info("\n🔍 调试标题输入框...")
            title_selectors = [
                ".d-text",
                "[placeholder*='标题']", 
                ".title-wrap input",
                ".editable-textarea",
                ".textarea-container input",
                "input[type='text']",
                "textarea",
                "[contenteditable='true']"
            ]
            
            title_input = None
            for selector in title_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        for elem in elements:
                            if elem.is_displayed() and elem.is_enabled():
                                logger.info(f"   ✅ 找到可用的标题输入框: {selector}")
                                title_input = elem
                                break
                        if title_input:
                            break
                except Exception as e:
                    logger.debug(f"   选择器 {selector} 失败: {e}")
            
            if title_input:
                # 测试emoji标题输入
                logger.info("\n🧪 测试1: 包含emoji的标题")
                title = "测试 😊 标题"
                logger.info(f"   输入内容: {title}")
                
                try:
                    title_input.clear()
                    await asyncio.sleep(0.5)
                    
                    # 使用emoji处理器
                    from src.utils.emoji_handler import EmojiHandler
                    success = await EmojiHandler.smart_send_keys(self.driver, title_input, title)
                    
                    if success:
                        logger.info("   ✅ 标题输入成功")
                        await asyncio.sleep(2)
                    else:
                        logger.error("   ❌ 标题输入失败")
                        
                except Exception as e:
                    logger.error(f"   ❌ 标题输入过程出错: {e}")
            else:
                logger.error("   ❌ 未找到可用的标题输入框")
            
            # 测试2: 内容编辑器调试
            logger.info("\n🔍 调试内容编辑器...")
            content_selectors = [
                ".ql-editor",
                ".editable-textarea",
                ".textarea-container textarea",
                "textarea",
                "[contenteditable='true']"
            ]
            
            content_editor = None
            for selector in content_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        for elem in elements:
                            if elem.is_displayed() and elem.is_enabled():
                                logger.info(f"   ✅ 找到可用的内容编辑器: {selector}")
                                content_editor = elem
                                break
                        if content_editor:
                            break
                except Exception as e:
                    logger.debug(f"   选择器 {selector} 失败: {e}")
            
            if content_editor:
                # 测试emoji内容输入
                logger.info("\n🧪 测试2: 包含emoji的内容")
                content = "第一行 🎉\n第二行普通文本\n第三行 ❤️"
                logger.info(f"   输入内容: {content}")
                
                try:
                    content_editor.click()
                    await asyncio.sleep(0.5)
                    
                    # 清空现有内容
                    content_editor.clear()
                    
                    # 使用emoji处理器
                    from src.utils.emoji_handler import EmojiHandler
                    success = await EmojiHandler.smart_send_keys(self.driver, content_editor, content)
                    
                    if success:
                        logger.info("   ✅ 内容输入成功")
                        await asyncio.sleep(2)
                    else:
                        logger.error("   ❌ 内容输入失败")
                        
                except Exception as e:
                    logger.error(f"   ❌ 内容输入过程出错: {e}")
            else:
                logger.error("   ❌ 未找到可用的内容编辑器")
            
            # 最终等待，让用户观察结果
            await asyncio.sleep(10)
            
            logger.info("\n" + "="*80)
            logger.info("📊 测试完成")
            logger.info("="*80)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 测试过程出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False


async def main():
    """主函数"""
    tester = InteractiveEmojiTester()
    
    try:
        # 初始化
        await tester.setup()
        
        # 运行测试
        success = await tester.test_emoji_inputs()
        
        if success:
            logger.info("\n🎉 Emoji输入测试完成！")
        else:
            logger.info("\n⚠️ Emoji输入测试遇到问题，请检查日志")
    
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