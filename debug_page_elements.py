#!/usr/bin/env python3
"""
调试页面元素脚本

探测小红书发布页面的实际元素结构，帮助找到正确的选择器
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.xiaohongshu.refactored_client import RefactoredXHSClient
from src.core.browser import ChromeDriverManager
from src.core.config import XHSConfig
from src.utils.logger import get_logger
from selenium.webdriver.common.by import By

logger = get_logger(__name__)


class PageElementDebugger:
    """页面元素调试器"""
    
    def __init__(self):
        self.browser_manager = None
        self.client = None
        self.driver = None
        
    async def setup(self):
        """初始化测试环境"""
        logger.info("🚀 初始化调试环境...")
        
        # 初始化配置和浏览器管理器
        config = XHSConfig()
        self.browser_manager = ChromeDriverManager(config)
        self.browser_manager.create_driver()
        self.driver = self.browser_manager.driver
        
        # 初始化客户端
        self.client = RefactoredXHSClient(self.browser_manager)
        
        logger.info("✅ 调试环境初始化完成")
        
    async def teardown(self):
        """清理环境"""
        if self.browser_manager:
            self.browser_manager.close_driver()
        logger.info("✅ 调试环境清理完成")
    
    async def debug_page_structure(self):
        """调试页面结构"""
        logger.info("\n" + "="*80)
        logger.info("🔍 开始调试小红书发布页面结构")
        logger.info("="*80)
        
        try:
            # 导航到发布页面
            logger.info("📍 导航到发布页面...")
            publisher = self.client.get_publisher()
            await publisher._navigate_to_publish_page()
            await asyncio.sleep(5)  # 等待页面完全加载
            
            # 检查页面标题
            page_title = self.driver.title
            logger.info(f"📄 页面标题: {page_title}")
            
            # 检查当前URL
            current_url = self.driver.current_url
            logger.info(f"🌐 当前URL: {current_url}")
            
            # 查找可能的输入框元素
            logger.info("\n🔍 查找可能的输入框元素...")
            
            # 方法1: 查找所有input元素
            logger.info("\n📝 所有 input 元素:")
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            for i, input_elem in enumerate(inputs):
                try:
                    input_type = input_elem.get_attribute("type")
                    placeholder = input_elem.get_attribute("placeholder")
                    class_name = input_elem.get_attribute("class")
                    name = input_elem.get_attribute("name")
                    id_attr = input_elem.get_attribute("id")
                    
                    logger.info(f"  Input {i+1}: type={input_type}, placeholder='{placeholder}', class='{class_name}', name='{name}', id='{id_attr}'")
                    
                    # 特别关注包含'标题'的元素
                    if (placeholder and ('标题' in placeholder or 'title' in placeholder.lower())) or \
                       (class_name and ('title' in class_name.lower() or 'd-text' in class_name)):
                        logger.info(f"    ⭐ 可能的标题输入框！")
                        
                except Exception as e:
                    logger.debug(f"    获取input属性失败: {e}")
            
            # 方法2: 查找所有textarea元素
            logger.info("\n📝 所有 textarea 元素:")
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            for i, textarea_elem in enumerate(textareas):
                try:
                    placeholder = textarea_elem.get_attribute("placeholder")
                    class_name = textarea_elem.get_attribute("class")
                    name = textarea_elem.get_attribute("name")
                    id_attr = textarea_elem.get_attribute("id")
                    
                    logger.info(f"  Textarea {i+1}: placeholder='{placeholder}', class='{class_name}', name='{name}', id='{id_attr}'")
                    
                    # 特别关注包含'内容'的元素
                    if (placeholder and ('内容' in placeholder or 'content' in placeholder.lower())) or \
                       (class_name and 'editor' in class_name.lower()):
                        logger.info(f"    ⭐ 可能的内容编辑器！")
                        
                except Exception as e:
                    logger.debug(f"    获取textarea属性失败: {e}")
            
            # 方法3: 查找所有div元素（可能是富文本编辑器）
            logger.info("\n📝 所有可能的富文本编辑器 div:")
            divs_with_contenteditable = self.driver.find_elements(By.CSS_SELECTOR, "div[contenteditable]")
            for i, div_elem in enumerate(divs_with_contenteditable):
                try:
                    class_name = div_elem.get_attribute("class")
                    id_attr = div_elem.get_attribute("id")
                    contenteditable = div_elem.get_attribute("contenteditable")
                    
                    logger.info(f"  ContentEditable Div {i+1}: class='{class_name}', id='{id_attr}', contenteditable='{contenteditable}'")
                    
                    # 特别关注quill编辑器
                    if class_name and ('ql-editor' in class_name or 'editor' in class_name):
                        logger.info(f"    ⭐ 可能的富文本编辑器！")
                        
                except Exception as e:
                    logger.debug(f"    获取div属性失败: {e}")
                    
            # 方法4: 测试旧的选择器
            logger.info("\n🧪 测试现有选择器...")
            
            # 测试标题选择器
            selectors_to_test = [
                ('.d-text', '标题选择器1'),
                ('[placeholder*="标题"]', '标题选择器2'),
                ('input[type="text"]', '通用文本输入'),
                ('.ql-editor', '富文本编辑器'),
                ('.title-input', '标题输入框'),
                ('[data-testid*="title"]', 'title测试ID'),
                ('[aria-label*="标题"]', '标题aria-label')
            ]
            
            for selector, desc in selectors_to_test:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"  ✅ {desc} ({selector}): 找到 {len(elements)} 个元素")
                        for j, elem in enumerate(elements[:2]):  # 只显示前2个
                            try:
                                tag = elem.tag_name
                                class_attr = elem.get_attribute("class")
                                placeholder = elem.get_attribute("placeholder")
                                logger.info(f"    元素{j+1}: <{tag}> class='{class_attr}' placeholder='{placeholder}'")
                            except:
                                pass
                    else:
                        logger.info(f"  ❌ {desc} ({selector}): 未找到")
                except Exception as e:
                    logger.info(f"  ⚠️ {desc} ({selector}): 查询出错 - {e}")
                    
            # 方法5: 获取页面HTML源码片段（只显示部分）
            logger.info("\n📄 页面HTML源码片段分析...")
            try:
                page_source = self.driver.page_source
                
                # 查找包含关键词的行
                keywords = ['标题', 'title', 'input', 'textarea', 'ql-editor', 'd-text']
                relevant_lines = []
                
                for line in page_source.split('\n'):
                    for keyword in keywords:
                        if keyword in line.lower() and len(relevant_lines) < 10:  # 限制输出行数
                            relevant_lines.append(line.strip()[:200])  # 限制行长度
                            break
                
                logger.info("  相关HTML行:")
                for line in relevant_lines:
                    logger.info(f"    {line}")
                    
            except Exception as e:
                logger.warning(f"获取页面源码失败: {e}")
            
            logger.info("\n" + "="*80)
            logger.info("🎯 调试完成！请检查上述输出以找到正确的选择器")
            logger.info("="*80)
            
        except Exception as e:
            logger.error(f"❌ 调试过程出错: {e}")
            import traceback
            logger.error(traceback.format_exc())


async def main():
    """主函数"""
    debugger = PageElementDebugger()
    
    try:
        # 初始化
        await debugger.setup()
        
        # 运行调试
        await debugger.debug_page_structure()
    
    except KeyboardInterrupt:
        logger.info("\n⚠️ 用户中断调试")
    except Exception as e:
        logger.error(f"❌ 调试过程出错: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # 清理
        await debugger.teardown()
        logger.info("\n👋 调试结束")


if __name__ == "__main__":
    # 运行调试
    asyncio.run(main())