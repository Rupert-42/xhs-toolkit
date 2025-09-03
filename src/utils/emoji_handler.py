"""
Emoji 输入处理器

处理 ChromeDriver 对 emoji 和非 BMP 字符的限制问题
通过 JavaScript 注入方式实现 emoji 的正确输入
"""

import re
from typing import Optional, List, Dict, Any, Tuple
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import JavascriptException, WebDriverException

from ..utils.logger import get_logger

logger = get_logger(__name__)


class EmojiHandler:
    """Emoji 输入处理器"""
    
    # Emoji 配置
    ENABLE_JS_INJECTION = True  # 总开关
    LOG_VERBOSE = True  # 详细日志开关
    
    # JavaScript 注入模式
    INJECTION_MODES = {
        'basic': 'basic_injection',      # 基础注入（input/textarea）
        'react': 'react_injection',      # React 应用注入
        'contenteditable': 'rich_editor_injection',  # 富文本编辑器
        'simulate': 'full_simulation'    # 完整事件模拟
    }
    
    @staticmethod
    def contains_emoji(text: str) -> bool:
        """
        检测文本是否包含 emoji 或非 BMP 字符
        
        Args:
            text: 要检测的文本
            
        Returns:
            是否包含 emoji
        """
        if not text:
            return False
            
        # 检测非 BMP 字符（Unicode > U+FFFF）
        for char in text:
            code_point = ord(char)
            # 基本多文种平面之外的字符
            if code_point > 0xFFFF:
                logger.debug(f"🔍 检测到非 BMP 字符: {char} (U+{code_point:04X})")
                return True
                
        # 检测常见 emoji 范围（即使在 BMP 内）
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # 表情符号
            "\U0001F300-\U0001F5FF"  # 符号和图标
            "\U0001F680-\U0001F6FF"  # 交通和地图符号
            "\U0001F1E0-\U0001F1FF"  # 国旗
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"  # 封闭字符
            "\U0001F900-\U0001F9FF"  # 补充符号和图标
            "\U00002600-\U000026FF"  # 杂项符号
            "\U00002700-\U000027BF"  # Dingbats
            "]+", 
            flags=re.UNICODE
        )
        
        if emoji_pattern.search(text):
            logger.debug(f"🔍 检测到 emoji 表情: {text}")
            return True
            
        return False
    
    @staticmethod
    def split_text_by_emoji(text: str) -> List[Dict[str, Any]]:
        """
        将文本按 emoji 和普通文本分段
        
        Args:
            text: 要分段的文本
            
        Returns:
            分段列表，每段包含 type 和 text
        """
        segments = []
        current_segment = ""
        current_type = None
        
        for char in text:
            is_emoji = EmojiHandler.contains_emoji(char)
            
            if current_type is None:
                current_type = 'emoji' if is_emoji else 'normal'
                current_segment = char
            elif (is_emoji and current_type == 'emoji') or (not is_emoji and current_type == 'normal'):
                current_segment += char
            else:
                # 类型切换，保存当前段
                segments.append({
                    'type': current_type,
                    'text': current_segment
                })
                current_type = 'emoji' if is_emoji else 'normal'
                current_segment = char
        
        # 保存最后一段
        if current_segment:
            segments.append({
                'type': current_type,
                'text': current_segment
            })
        
        if EmojiHandler.LOG_VERBOSE and segments:
            logger.debug(f"📊 文本分段结果: {segments}")
        
        return segments
    
    @staticmethod
    def get_element_type(driver, element: WebElement) -> str:
        """
        识别元素类型以选择合适的注入方式
        
        Args:
            driver: WebDriver 实例
            element: 要识别的元素
            
        Returns:
            元素类型标识
        """
        try:
            tag_name = element.tag_name.lower()
            contenteditable = element.get_attribute('contenteditable')
            element_class = element.get_attribute('class') or ''
            
            logger.debug(f"🏷️ 元素信息: tag={tag_name}, contenteditable={contenteditable}, class={element_class}")
            
            # 判断元素类型
            if tag_name in ['input', 'textarea']:
                return 'basic'
            elif contenteditable == 'true':
                return 'contenteditable'
            elif 'ql-editor' in element_class or 'editor' in element_class:
                # 可能是 Quill 或其他富文本编辑器
                return 'contenteditable'
            else:
                # 默认使用 React 模式（小红书是 React 应用）
                return 'react'
                
        except Exception as e:
            logger.warning(f"⚠️ 获取元素类型失败: {e}，使用默认模式")
            return 'react'
    
    @staticmethod
    async def js_inject_text(driver, element: WebElement, text: str, mode: str = 'auto') -> bool:
        """
        使用 JavaScript 注入文本
        
        Args:
            driver: WebDriver 实例
            element: 目标元素
            text: 要注入的文本
            mode: 注入模式 ('auto', 'basic', 'react', 'contenteditable', 'simulate')
            
        Returns:
            是否成功
        """
        try:
            # 自动检测模式
            if mode == 'auto':
                mode = EmojiHandler.get_element_type(driver, element)
                logger.info(f"🤖 自动选择注入模式: {mode}")
            
            # 转义文本中的特殊字符
            escaped_text = text.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
            
            if mode == 'basic':
                # 基础注入（适用于 input/textarea）
                js_code = f"""
                    var elm = arguments[0];
                    var txt = "{escaped_text}";
                    console.log('🚀 JS注入 - 基础模式，文本:', txt);
                    elm.focus();
                    elm.value = txt;
                    elm.dispatchEvent(new Event('input', {{bubbles: true}}));
                    elm.dispatchEvent(new Event('change', {{bubbles: true}}));
                    console.log('✅ JS注入完成');
                    return true;
                """
                
            elif mode == 'contenteditable':
                # 富文本编辑器注入
                js_code = f"""
                    var elm = arguments[0];
                    var txt = "{escaped_text}";
                    console.log('🚀 JS注入 - 富文本模式，文本:', txt);
                    elm.focus();
                    elm.innerHTML = txt.replace(/\\n/g, '<br>');
                    elm.dispatchEvent(new Event('input', {{bubbles: true}}));
                    elm.dispatchEvent(new Event('change', {{bubbles: true}}));
                    console.log('✅ JS注入完成');
                    return true;
                """
                
            elif mode == 'simulate':
                # 完整事件模拟（最复杂但最兼容）
                js_code = f"""
                    var elm = arguments[0];
                    var txt = "{escaped_text}";
                    console.log('🚀 JS注入 - 完整模拟模式，文本:', txt);
                    elm.focus();
                    elm.value = txt;
                    
                    // 触发完整的事件链
                    var events = ['keydown', 'keypress', 'input', 'keyup', 'change'];
                    events.forEach(function(eventType) {{
                        var event = new Event(eventType, {{bubbles: true, cancelable: true}});
                        elm.dispatchEvent(event);
                        console.log('📤 触发事件:', eventType);
                    }});
                    
                    elm.blur();
                    console.log('✅ JS注入完成');
                    return true;
                """
                
            else:  # react 模式（默认）
                # React 应用注入（适用于小红书）
                js_code = f"""
                    var elm = arguments[0];
                    var txt = "{escaped_text}";
                    console.log('🚀 JS注入 - React模式，文本:', txt);
                    
                    // 获取 React 内部实例（如果存在）
                    var reactKey = Object.keys(elm).find(key => key.startsWith('__react'));
                    console.log('React key:', reactKey);
                    
                    elm.focus();
                    
                    // 设置值
                    if (elm.tagName.toLowerCase() === 'input' || elm.tagName.toLowerCase() === 'textarea') {{
                        elm.value = txt;
                    }} else {{
                        elm.textContent = txt;
                    }}
                    
                    // 触发 React 事件
                    var inputEvent = new Event('input', {{bubbles: true, cancelable: true}});
                    Object.defineProperty(inputEvent, 'target', {{value: elm, enumerable: true}});
                    elm.dispatchEvent(inputEvent);
                    
                    var changeEvent = new Event('change', {{bubbles: true, cancelable: true}});
                    elm.dispatchEvent(changeEvent);
                    
                    console.log('✅ JS注入完成');
                    return true;
                """
            
            logger.info(f"💉 执行 JS 注入: mode={mode}, text_length={len(text)}")
            if EmojiHandler.LOG_VERBOSE:
                logger.debug(f"📝 注入文本内容: {text[:100]}...")
            
            # 执行 JavaScript
            result = driver.execute_script(js_code, element)
            
            if result:
                logger.info(f"✅ JS 注入成功！模式: {mode}")
            else:
                logger.warning(f"⚠️ JS 注入返回 False，模式: {mode}")
                
            return bool(result)
            
        except JavascriptException as e:
            logger.error(f"❌ JavaScript 执行错误: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ JS 注入失败: {e}")
            return False
    
    @staticmethod
    async def smart_send_keys(driver, element: WebElement, text: str, force_js: bool = False) -> bool:
        """
        智能发送文本，自动处理 emoji
        
        Args:
            driver: WebDriver 实例
            element: 目标元素
            text: 要发送的文本
            force_js: 是否强制使用 JS 注入
            
        Returns:
            是否成功
        """
        try:
            # 检查是否启用 JS 注入
            if not EmojiHandler.ENABLE_JS_INJECTION and not force_js:
                logger.info("📌 JS 注入已禁用，使用普通 send_keys")
                element.send_keys(text)
                return True
            
            # 检查是否需要 JS 注入
            needs_injection = force_js or EmojiHandler.contains_emoji(text)
            
            if not needs_injection:
                # 普通文本，使用原生 send_keys
                logger.debug(f"📤 使用普通 send_keys 输入: {text[:50]}...")
                element.send_keys(text)
                return True
            
            # 需要 JS 注入
            logger.info(f"🎯 检测到 emoji，使用 JS 注入方式")
            
            # 分段处理（混合模式）
            segments = EmojiHandler.split_text_by_emoji(text)
            
            for i, segment in enumerate(segments):
                logger.debug(f"📝 处理第 {i+1}/{len(segments)} 段: type={segment['type']}, text={segment['text'][:20]}...")
                
                if segment['type'] == 'normal':
                    # 普通文本用 send_keys
                    element.send_keys(segment['text'])
                    logger.debug(f"✅ 普通文本段发送完成")
                else:
                    # emoji 用 JS 注入
                    success = await EmojiHandler.js_inject_text(driver, element, segment['text'])
                    if not success:
                        logger.warning(f"⚠️ Emoji 段注入失败，尝试降级处理")
                        # 降级：尝试直接 send_keys（可能会失败）
                        try:
                            element.send_keys(segment['text'])
                        except Exception as e:
                            logger.error(f"❌ 降级发送也失败: {e}")
                            return False
                    else:
                        logger.debug(f"✅ Emoji 段注入成功")
            
            logger.info(f"✅ 智能文本输入完成，共处理 {len(segments)} 段")
            return True
            
        except Exception as e:
            logger.error(f"❌ 智能发送失败: {e}")
            # 最后的降级方案
            try:
                logger.info("🔄 尝试最后的降级方案...")
                element.send_keys(text.encode('ascii', 'ignore').decode('ascii'))
                return True
            except:
                return False
    
    @staticmethod
    async def send_keys_with_enter(driver, element: WebElement, text: str, enter_after: bool = True) -> bool:
        """
        发送文本并按回车（用于话题等场景）
        
        Args:
            driver: WebDriver 实例
            element: 目标元素
            text: 要发送的文本
            enter_after: 是否在文本后按回车
            
        Returns:
            是否成功
        """
        try:
            logger.info(f"📝 发送文本并回车: {text}")
            
            # 发送文本
            success = await EmojiHandler.smart_send_keys(driver, element, text)
            
            if success and enter_after:
                # 发送回车键
                logger.debug("⏎ 发送回车键")
                element.send_keys(Keys.ENTER)
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 发送文本并回车失败: {e}")
            return False


# 便捷函数
async def smart_input(driver, element: WebElement, text: str) -> bool:
    """
    便捷函数：智能输入文本
    
    Args:
        driver: WebDriver 实例
        element: 目标元素
        text: 要输入的文本
        
    Returns:
        是否成功
    """
    return await EmojiHandler.smart_send_keys(driver, element, text)


def has_emoji(text: str) -> bool:
    """
    便捷函数：检测文本是否包含 emoji
    
    Args:
        text: 要检测的文本
        
    Returns:
        是否包含 emoji
    """
    return EmojiHandler.contains_emoji(text)