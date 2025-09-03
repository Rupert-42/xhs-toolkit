#!/usr/bin/env python3
"""
Emoji 输入功能测试脚本

测试小红书发布中的 emoji 输入功能
包括标题、内容、话题等各种场景
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.xiaohongshu.refactored_client import XHSPublisher
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EmojiInputTester:
    """Emoji 输入测试器"""
    
    def __init__(self):
        self.publisher = None
        self.test_cases = []
        
    async def setup(self):
        """初始化测试环境"""
        logger.info("🚀 初始化测试环境...")
        self.publisher = XHSPublisher()
        await self.publisher.init()
        logger.info("✅ 测试环境初始化完成")
        
    async def teardown(self):
        """清理测试环境"""
        if self.publisher:
            await self.publisher.close()
        logger.info("✅ 测试环境清理完成")
    
    def prepare_test_cases(self):
        """准备测试用例"""
        self.test_cases = [
            {
                "name": "基础 Emoji 测试",
                "title": "测试标题 😊 开心",
                "content": "这是测试内容 🎉 庆祝一下\n第二行有表情 ❤️ 爱心\n第三行普通文本",
                "topics": ["测试话题😊", "美食🍔", "旅行✈️"],
                "description": "测试基础的 emoji 输入"
            },
            {
                "name": "复杂 Emoji 测试",
                "title": "复杂表情测试 👨‍👩‍👧‍👦 家庭",
                "content": "多种表情混合：\n😀😃😄😁😆😅🤣😂🙂🙃\n国旗：🇨🇳🇺🇸🇬🇧🇯🇵\n手势：👍👎👌✌️🤞",
                "topics": ["复杂emoji🏆", "多码点👨‍👩‍👧"],
                "description": "测试复杂的多码点 emoji"
            },
            {
                "name": "混合文本测试",
                "title": "中英文Mix😎with表情",
                "content": "第一段：普通中文文本\n第二段：English text with emoji 🚀\n第三段：中英混合with😊表情",
                "topics": ["中文话题", "English🎯", "混合Mix💪"],
                "description": "测试中英文与 emoji 混合"
            },
            {
                "name": "特殊符号测试",
                "title": "特殊符号™️版权©️注册®️",
                "content": "数学符号：∑∏∫∮\n货币符号：￥$€£\n箭头：→←↑↓⇒⇐\n其他：♠♥♦♣★☆",
                "topics": ["符号➕", "数学∑", "货币💰"],
                "description": "测试各种特殊符号"
            },
            {
                "name": "纯 Emoji 测试",
                "title": "🎉🎊🎈",
                "content": "😊😊😊\n🎉🎉🎉\n❤️❤️❤️",
                "topics": ["😊", "🎉", "❤️"],
                "description": "测试纯 emoji 输入"
            }
        ]
        logger.info(f"📋 准备了 {len(self.test_cases)} 个测试用例")
    
    async def test_single_case(self, test_case: dict):
        """
        测试单个用例
        
        Args:
            test_case: 测试用例
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 开始测试: {test_case['name']}")
        logger.info(f"📝 描述: {test_case['description']}")
        logger.info(f"{'='*60}")
        
        try:
            # 导航到发布页面
            logger.info("📍 导航到发布页面...")
            success = await self.publisher.navigate_to_publish_page()
            if not success:
                logger.error("❌ 无法导航到发布页面")
                return False
            
            await asyncio.sleep(2)  # 等待页面加载
            
            # 测试标题输入
            logger.info(f"\n📝 测试标题输入...")
            logger.info(f"   标题内容: {test_case['title']}")
            title_result = await self.publisher.content_filler.fill_title(test_case['title'])
            if title_result:
                logger.info("   ✅ 标题输入成功")
            else:
                logger.error("   ❌ 标题输入失败")
            
            await asyncio.sleep(1)
            
            # 测试内容输入
            logger.info(f"\n📝 测试内容输入...")
            logger.info(f"   内容预览: {test_case['content'][:50]}...")
            content_result = await self.publisher.content_filler.fill_content(test_case['content'])
            if content_result:
                logger.info("   ✅ 内容输入成功")
            else:
                logger.error("   ❌ 内容输入失败")
            
            await asyncio.sleep(1)
            
            # 测试话题输入
            if test_case.get('topics'):
                logger.info(f"\n🏷️ 测试话题输入...")
                logger.info(f"   话题列表: {test_case['topics']}")
                topics_result = await self.publisher.content_filler.fill_topics(test_case['topics'])
                if topics_result:
                    logger.info("   ✅ 话题输入成功")
                else:
                    logger.error("   ❌ 话题输入失败")
            
            # 等待用户确认
            logger.info(f"\n{'='*60}")
            logger.info("⏸️  请检查页面上的输入结果...")
            logger.info("   1. 标题是否正确显示了 emoji？")
            logger.info("   2. 内容中的 emoji 是否正确显示？")
            logger.info("   3. 话题中的 emoji 是否正确转换？")
            logger.info(f"{'='*60}")
            
            await asyncio.sleep(5)  # 给用户时间查看
            
            # 清理页面（刷新以准备下一个测试）
            logger.info("🔄 刷新页面准备下一个测试...")
            driver = self.publisher.browser_manager.driver
            driver.refresh()
            await asyncio.sleep(3)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 测试用例执行失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("\n" + "="*80)
        logger.info("🎯 开始 Emoji 输入功能测试")
        logger.info("="*80)
        
        self.prepare_test_cases()
        
        success_count = 0
        fail_count = 0
        
        for i, test_case in enumerate(self.test_cases, 1):
            logger.info(f"\n\n{'#'*80}")
            logger.info(f"📊 测试进度: {i}/{len(self.test_cases)}")
            logger.info(f"{'#'*80}")
            
            result = await self.test_single_case(test_case)
            
            if result:
                success_count += 1
                logger.info(f"✅ 测试用例 '{test_case['name']}' 通过")
            else:
                fail_count += 1
                logger.error(f"❌ 测试用例 '{test_case['name']}' 失败")
            
            if i < len(self.test_cases):
                logger.info("\n⏳ 等待 3 秒后继续下一个测试...")
                await asyncio.sleep(3)
        
        # 输出测试总结
        logger.info("\n" + "="*80)
        logger.info("📊 测试总结")
        logger.info("="*80)
        logger.info(f"✅ 成功: {success_count} 个")
        logger.info(f"❌ 失败: {fail_count} 个")
        logger.info(f"📈 成功率: {success_count/len(self.test_cases)*100:.1f}%")
        logger.info("="*80)
    
    async def run_interactive_test(self):
        """交互式测试模式"""
        logger.info("\n" + "="*80)
        logger.info("🎮 交互式 Emoji 测试模式")
        logger.info("="*80)
        
        while True:
            print("\n请选择测试内容：")
            print("1. 测试标题输入")
            print("2. 测试内容输入")
            print("3. 测试话题输入")
            print("4. 运行完整测试")
            print("0. 退出")
            
            choice = input("\n请输入选项 (0-4): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                title = input("请输入包含 emoji 的标题: ").strip()
                if title:
                    await self.publisher.navigate_to_publish_page()
                    result = await self.publisher.content_filler.fill_title(title)
                    logger.info(f"标题输入结果: {'成功' if result else '失败'}")
            elif choice == '2':
                content = input("请输入包含 emoji 的内容 (用 \\n 表示换行): ").strip()
                if content:
                    content = content.replace('\\n', '\n')
                    await self.publisher.navigate_to_publish_page()
                    result = await self.publisher.content_filler.fill_content(content)
                    logger.info(f"内容输入结果: {'成功' if result else '失败'}")
            elif choice == '3':
                topics_str = input("请输入包含 emoji 的话题 (逗号分隔): ").strip()
                if topics_str:
                    topics = [t.strip() for t in topics_str.split(',')]
                    await self.publisher.navigate_to_publish_page()
                    result = await self.publisher.content_filler.fill_topics(topics)
                    logger.info(f"话题输入结果: {'成功' if result else '失败'}")
            elif choice == '4':
                await self.run_all_tests()
            else:
                print("无效选项，请重新选择")
            
            if choice in ['1', '2', '3']:
                input("\n按回车键继续...")


async def main():
    """主函数"""
    tester = EmojiInputTester()
    
    try:
        # 初始化
        await tester.setup()
        
        # 选择测试模式
        print("\n" + "="*60)
        print("🧪 小红书 Emoji 输入测试工具")
        print("="*60)
        print("\n请选择测试模式：")
        print("1. 自动测试所有用例")
        print("2. 交互式测试")
        
        mode = input("\n请输入选项 (1-2): ").strip()
        
        if mode == '1':
            await tester.run_all_tests()
        elif mode == '2':
            await tester.run_interactive_test()
        else:
            logger.error("无效的选项")
    
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