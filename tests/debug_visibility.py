#!/usr/bin/env python3
"""
调试可见范围设置功能
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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

setup_logger()
logger = get_logger()

async def debug_visibility_setting():
    """调试可见范围设置"""
    logger.info("\n" + "="*60)
    logger.info("🔍 调试可见范围设置功能")
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
        title=f"调试 {datetime.now().strftime('%H:%M')}",
        content="调试可见范围设置",
        images=test_images[:1],
        visibility="private",  # 设置为私密
        dry_run=True
    )
    
    try:
        # 初始化浏览器
        driver = client.browser_manager.create_driver()
        client.browser_manager.navigate_to_creator_center()
        
        # 加载cookies
        cookies = client.cookie_manager.load_cookies()
        client.browser_manager.load_cookies(cookies)
        
        # 访问发布页面
        logger.info("🌐 访问发布页面...")
        driver.get("https://creator.xiaohongshu.com/publish/publish?from=menu")
        await asyncio.sleep(5)
        
        # 等待页面完全加载
        logger.info("⏳ 等待页面元素完全渲染...")
        await asyncio.sleep(3)
        
        # 切换到图文模式
        logger.info("🔄 切换到图文模式...")
        image_tab = driver.find_element(By.XPATH, "//div[contains(@class, 'tab') and contains(text(), '图文')]")
        image_tab.click()
        await asyncio.sleep(2)
        
        # 上传图片
        logger.info("📸 上传图片...")
        upload_input = driver.find_element(By.XPATH, "//input[@type='file']")
        upload_input.send_keys(test_images[0])
        await asyncio.sleep(5)
        
        # 调试：查找所有可能的可见范围相关元素
        logger.info("\n🔍 开始查找可见范围相关元素...")
        
        # 方法1：查找包含特定文本的元素
        text_patterns = ["所有人可见", "公开", "可见", "权限", "隐私"]
        for pattern in text_patterns:
            try:
                elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{pattern}')]")
                for elem in elements:
                    if elem.is_displayed():
                        logger.info(f"📌 找到文本元素 '{pattern}': 标签={elem.tag_name}, 文本={elem.text[:50] if elem.text else '无文本'}")
            except Exception as e:
                logger.debug(f"查找'{pattern}'时出错: {e}")
        
        # 方法2：查找包含特定class的元素
        class_patterns = ["permission", "visibility", "privacy", "access", "public"]
        for pattern in class_patterns:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, f"[class*='{pattern}']")
                for elem in elements:
                    if elem.is_displayed():
                        logger.info(f"📌 找到class元素 '{pattern}': 标签={elem.tag_name}, class={elem.get_attribute('class')[:50]}")
            except Exception as e:
                logger.debug(f"查找class '{pattern}'时出错: {e}")
        
        # 方法3：查找可点击的按钮或下拉框
        clickable_selectors = [
            "button", "select", "[role='button']", "[role='combobox']", 
            "[role='listbox']", ".dropdown", ".select"
        ]
        for selector in clickable_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    text = elem.text or elem.get_attribute("aria-label") or ""
                    if elem.is_displayed() and ("可见" in text or "权限" in text or "隐私" in text):
                        logger.info(f"📌 找到可点击元素: 选择器={selector}, 文本={text[:50]}")
            except Exception as e:
                logger.debug(f"查找'{selector}'时出错: {e}")
        
        # 尝试点击找到的元素
        logger.info("\n🔍 尝试点击可见范围按钮...")
        permission_element = None
        
        # 优先尝试精确的选择器
        precise_selectors = [
            "//span[contains(text(), '所有人可见')]",
            "//div[contains(text(), '所有人可见')]",
            "//button[contains(., '所有人可见')]",
            "//*[@class='permission' or contains(@class, 'permission')]",
            "//*[@class='visibility' or contains(@class, 'visibility')]"
        ]
        
        for selector in precise_selectors:
            try:
                elem = driver.find_element(By.XPATH, selector)
                if elem.is_displayed():
                    logger.info(f"✅ 找到可见范围按钮: {selector}")
                    elem.click()
                    await asyncio.sleep(2)
                    
                    # 查找下拉选项
                    logger.info("🔍 查找下拉选项...")
                    option_selectors = [
                        "//span[contains(text(), '仅自己可见')]",
                        "//div[contains(text(), '仅自己可见')]",
                        "//li[contains(text(), '仅自己可见')]",
                        "//*[contains(text(), '仅我可见')]",
                        "//*[contains(text(), '私密')]"
                    ]
                    
                    for opt_selector in option_selectors:
                        try:
                            option = driver.find_element(By.XPATH, opt_selector)
                            if option.is_displayed():
                                logger.info(f"✅ 找到'仅自己可见'选项: {opt_selector}")
                                option.click()
                                await asyncio.sleep(1)
                                break
                        except:
                            continue
                    break
            except:
                continue
        
        # 截图当前状态
        logger.info("📸 保存调试截图...")
        driver.save_screenshot("debug_visibility.png")
        logger.info("✅ 截图已保存: debug_visibility.png")
        
        # 保持浏览器打开
        logger.info("\n⏰ 保持浏览器打开20秒供检查...")
        await asyncio.sleep(20)
        
    except Exception as e:
        logger.error(f"❌ 调试出错: {e}")
        import traceback
        logger.error(f"错误详情:\n{traceback.format_exc()}")
    finally:
        client.browser_manager.close_driver()

async def main():
    """主函数"""
    await debug_visibility_setting()

if __name__ == "__main__":
    asyncio.run(main())