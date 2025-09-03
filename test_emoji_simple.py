#!/usr/bin/env python3
"""
简化的 Emoji 输入功能测试脚本

自动运行指定的emoji测试场景，无需交互式输入
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

logger = get_logger(__name__)


class SimpleEmojiTester:
    """简化的Emoji输入测试器"""
    
    def __init__(self):
        self.browser_manager = None
        self.client = None
        self.publisher = None
        
    async def setup(self):
        """初始化测试环境"""
        logger.info("🚀 初始化测试环境...")
        
        # 初始化配置和浏览器管理器
        config = XHSConfig()
        self.browser_manager = ChromeDriverManager(config)
        self.browser_manager.create_driver()
        
        # 初始化客户端和发布器
        self.client = RefactoredXHSClient(self.browser_manager)
        self.publisher = self.client.get_publisher()
        
        logger.info("✅ 测试环境初始化完成")
        
    async def teardown(self):
        """清理测试环境"""
        if self.browser_manager:
            self.browser_manager.close_driver()
        logger.info("✅ 测试环境清理完成")
    
    async def test_emoji_inputs(self):
        """测试emoji输入功能"""
        logger.info("\n" + "="*80)
        logger.info("🎯 开始 Emoji 输入功能测试")
        logger.info("="*80)
        
        try:
            # 导航到发布页面
            logger.info("📍 导航到发布页面...")
            await self.publisher._navigate_to_publish_page()
            await asyncio.sleep(3)  # 等待页面加载
            
            # 测试1: 包含emoji的标题
            logger.info("\n🧪 测试1: 包含emoji的标题")
            title = "测试 😊 标题"
            logger.info(f"   输入内容: {title}")
            
            title_result = await self.publisher.content_filler.fill_title(title)
            if title_result:
                logger.info("   ✅ 标题输入成功")
            else:
                logger.error("   ❌ 标题输入失败")
            
            await asyncio.sleep(2)
            
            # 测试2: 包含emoji的内容 
            logger.info("\n🧪 测试2: 包含emoji的内容")
            content = "第一行 🎉\n第二行普通文本\n第三行 ❤️"
            logger.info(f"   输入内容: {content}")
            
            content_result = await self.publisher.content_filler.fill_content(content)
            if content_result:
                logger.info("   ✅ 内容输入成功")
            else:
                logger.error("   ❌ 内容输入失败")
            
            await asyncio.sleep(2)
            
            # 测试3: 包含emoji的话题
            logger.info("\n🧪 测试3: 包含emoji的话题")
            topics = ["测试😊", "美食🍔"]
            logger.info(f"   输入内容: {topics}")
            
            topics_result = await self.publisher.content_filler.fill_topics(topics)
            if topics_result:
                logger.info("   ✅ 话题输入成功")
            else:
                logger.error("   ❌ 话题输入失败")
            
            await asyncio.sleep(5)  # 给用户时间观察结果
            
            # 输出测试总结
            logger.info("\n" + "="*80)
            logger.info("📊 测试总结")
            logger.info("="*80)
            success_count = sum([title_result, content_result, topics_result])
            logger.info(f"✅ 成功: {success_count}/3 个测试")
            logger.info(f"❌ 失败: {3-success_count}/3 个测试")
            logger.info(f"📈 成功率: {success_count/3*100:.1f}%")
            logger.info("="*80)
            
            return success_count == 3
            
        except Exception as e:
            logger.error(f"❌ 测试过程出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False


async def main():
    """主函数"""
    tester = SimpleEmojiTester()
    
    try:
        # 初始化
        await tester.setup()
        
        # 运行测试
        success = await tester.test_emoji_inputs()
        
        if success:
            logger.info("\n🎉 所有Emoji输入测试通过！")
        else:
            logger.info("\n⚠️ 部分或全部Emoji输入测试失败，请检查日志")
    
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