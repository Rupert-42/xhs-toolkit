"""
话题标签处理器 - 专门处理小红书话题标签的添加
"""

import asyncio
from typing import List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

logger = logging.getLogger(__name__)


class TopicHandler:
    """话题标签处理器"""
    
    def __init__(self, browser_manager):
        self.browser_manager = browser_manager
        
    async def add_topics(self, topics: List[str], max_topics: int = 10) -> bool:
        """
        添加话题标签
        
        Args:
            topics: 话题列表
            max_topics: 最大话题数量，默认10个
            
        Returns:
            是否成功
        """
        try:
            driver = self.browser_manager.driver
            
            # 1. 限制话题数量
            topics_to_add = topics[:max_topics] if len(topics) > max_topics else topics
            logger.info(f"📝 准备添加 {len(topics_to_add)} 个话题")
            
            # 2. 找到内容编辑器
            content_editor = self._find_active_editor(driver)
            if not content_editor:
                logger.error("❌ 未找到内容编辑器")
                return False
            
            # 3. 保存原始内容
            original_content = content_editor.text
            logger.info(f"📝 保存原始内容长度: {len(original_content)} 字符")
            
            # 4. 移动到内容末尾并换行
            content_editor.click()
            await asyncio.sleep(0.3)
            content_editor.send_keys(Keys.END)
            await asyncio.sleep(0.3)
            content_editor.send_keys(Keys.ENTER)
            await asyncio.sleep(0.5)
            
            # 5. 逐个添加话题
            success_count = 0
            for i, topic in enumerate(topics_to_add):
                logger.info(f"🏷️ [{i+1}/{len(topics_to_add)}] 添加话题: {topic}")
                
                if await self._add_single_topic(driver, content_editor, topic):
                    success_count += 1
                    # 添加空格分隔
                    if i < len(topics_to_add) - 1:
                        content_editor.send_keys(" ")
                        await asyncio.sleep(0.3)
                else:
                    logger.warning(f"⚠️ 话题 '{topic}' 添加失败")
            
            # 6. 如果需要，补齐到10个话题
            if success_count < max_topics:
                additional_needed = max_topics - success_count
                logger.info(f"📝 自动补充 {additional_needed} 个话题")
                
                for i in range(additional_needed):
                    if success_count > 0:
                        content_editor.send_keys(" ")
                        await asyncio.sleep(0.3)
                    
                    if await self._add_auto_topic(driver, content_editor):
                        success_count += 1
                    else:
                        break
            
            # 7. 验证内容是否正确
            await asyncio.sleep(1)
            current_content = content_editor.text
            logger.info(f"✅ 话题添加完成，共 {success_count} 个")
            logger.info(f"📝 最终内容长度: {len(current_content)} 字符")
            
            # 检查是否保留了原始内容
            if len(original_content) > 10 and original_content[:10] not in current_content:
                logger.warning("⚠️ 原始内容可能被覆盖")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ 添加话题过程出错: {e}")
            return False
    
    def _find_active_editor(self, driver) -> Optional:
        """查找当前活动的内容编辑器"""
        selectors = [
            "div[contenteditable='true']",
            ".ql-editor",
            "[contenteditable='true']",
            "div.content-editor"
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled():
                        return elem
            except:
                continue
        return None
    
    async def _add_single_topic(self, driver, editor, topic: str) -> bool:
        """
        添加单个话题
        
        Args:
            driver: WebDriver实例
            editor: 编辑器元素
            topic: 话题名称
            
        Returns:
            是否成功
        """
        try:
            # 1. 输入完整的话题文本
            topic_text = f"#{topic}" if not topic.startswith('#') else topic
            logger.info(f"📝 输入: {topic_text}")
            
            # 记录输入前的内容
            before_input = editor.text
            
            # 输入话题
            editor.send_keys(topic_text)
            await asyncio.sleep(0.5)
            
            # 2. 等待弹框出现
            if await self._wait_for_dropdown(driver):
                # 3. 按回车选择第一个
                editor.send_keys(Keys.ENTER)
                await asyncio.sleep(0.5)
                
                # 4. 验证话题是否成功转换
                after_input = editor.text
                
                # 检查是否生成了话题标签（通常会变成特殊格式）
                if topic_text not in after_input or len(after_input) < len(before_input) + len(topic):
                    logger.info(f"✅ 话题 '{topic}' 成功转换为标签")
                    return True
                else:
                    logger.warning(f"⚠️ 话题 '{topic}' 可能未成功转换")
                    return True  # 即使不确定也继续
            else:
                # 如果没有弹框，删除输入的文本
                logger.warning(f"⚠️ 未检测到话题弹框，删除输入")
                for _ in range(len(topic_text)):
                    editor.send_keys(Keys.BACKSPACE)
                await asyncio.sleep(0.3)
                return False
                
        except Exception as e:
            logger.error(f"❌ 添加话题 '{topic}' 时出错: {e}")
            return False
    
    async def _add_auto_topic(self, driver, editor) -> bool:
        """
        自动添加一个推荐话题
        
        Args:
            driver: WebDriver实例
            editor: 编辑器元素
            
        Returns:
            是否成功
        """
        try:
            logger.info("🏷️ 自动添加推荐话题")
            
            # 只输入#号
            editor.send_keys("#")
            await asyncio.sleep(0.5)
            
            # 等待弹框
            if await self._wait_for_dropdown(driver):
                # 直接回车选择第一个推荐
                editor.send_keys(Keys.ENTER)
                await asyncio.sleep(0.5)
                logger.info("✅ 自动话题添加成功")
                return True
            else:
                # 删除#号
                editor.send_keys(Keys.BACKSPACE)
                return False
                
        except Exception as e:
            logger.error(f"❌ 自动添加话题出错: {e}")
            return False
    
    async def _wait_for_dropdown(self, driver, max_wait: int = 10) -> bool:
        """
        等待话题下拉框出现并加载完成
        
        Args:
            driver: WebDriver实例
            max_wait: 最大等待时间（秒）
            
        Returns:
            是否找到下拉框
        """
        logger.info(f"⏳ 等待话题弹框加载（最多{max_wait}秒）...")
        
        # 根据实际页面，弹框可能的选择器
        dropdown_selectors = [
            # 更通用的选择器
            "//div[contains(@style, 'position') and contains(@style, 'absolute')]//ul",
            "//div[contains(@style, 'position') and contains(@style, 'fixed')]//ul",
            # 基于class的选择器
            "//div[contains(@class, 'mention')]",
            "//div[contains(@class, 'dropdown')]",
            "//div[contains(@class, 'suggest')]",
            "//div[contains(@class, 'popover')]",
            "//ul[contains(@class, 'mention')]",
            # 基于属性的选择器
            "//*[@role='listbox']",
            "//*[@role='menu']",
            "//div[@data-mentionable]",
            # CSS选择器
            ".mention-dropdown",
            ".topic-suggestions",
            ".dropdown-menu:visible",
            "[class*='mention']:visible",
            "[class*='suggest']:visible"
        ]
        
        start_time = asyncio.get_event_loop().time()
        last_check_time = start_time
        
        while (asyncio.get_event_loop().time() - start_time) < max_wait:
            current_time = asyncio.get_event_loop().time()
            
            # 每秒输出一次进度
            if current_time - last_check_time >= 1:
                elapsed = int(current_time - start_time)
                logger.debug(f"⏳ 已等待 {elapsed} 秒...")
                last_check_time = current_time
            
            for selector in dropdown_selectors:
                try:
                    # 判断是XPath还是CSS选择器
                    if selector.startswith("//") or selector.startswith("/*"):
                        # XPath选择器
                        elements = driver.find_elements(By.XPATH, selector)
                    else:
                        # CSS选择器
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for elem in elements:
                        if elem.is_displayed():
                            # 检查是否有选项
                            options = elem.find_elements(By.CSS_SELECTOR, "li, [role='option'], .item, .suggestion") or \
                                     elem.find_elements(By.XPATH, ".//li | .//*[@role='option']")
                            if options and len(options) > 0:
                                logger.info(f"✅ 话题弹框已加载，包含 {len(options)} 个选项")
                                # 等待一下确保完全加载
                                await asyncio.sleep(0.5)
                                return True
                except:
                    continue
            
            await asyncio.sleep(0.2)
        
        logger.warning(f"⚠️ 等待 {max_wait} 秒后未检测到话题弹框")
        return False