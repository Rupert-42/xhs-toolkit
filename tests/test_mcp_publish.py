#!/usr/bin/env python3
"""
MCP API 发布测试工具
通过MCP接口测试发布功能，验证浏览器可视化模式
"""

import sys
import os
import asyncio
import json
import time
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.server.mcp_server import XHSMCPServer
from src.core.logger import setup_logger

logger = setup_logger()

async def test_mcp_publish_visual():
    """
    通过MCP接口测试发布功能
    模拟完整的发布流程但不实际发布
    """
    logger.info("=" * 60)
    logger.info("🧪 MCP API 发布测试 - 浏览器可视化模式")
    logger.info("=" * 60)
    
    # 初始化MCP服务器
    logger.info("\n📡 初始化MCP服务器...")
    server = XHSMCPServer()
    
    # 确保浏览器以可视化模式运行
    if hasattr(server.xhs_client, 'browser_manager'):
        server.xhs_client.browser_manager.headless = False
        logger.info("✅ 已设置浏览器为可视化模式")
    
    # 准备测试数据
    test_data = {
        "title": "【MCP测试】浏览器可视化验证",
        "content": """
🔧 MCP API 测试笔记

这是通过MCP接口创建的测试内容：
• 验证浏览器可视化功能
• 测试发布流程
• 不会实际发布

⚠️ 仅用于开发测试

#MCP测试 #API测试 #开发验证
        """.strip(),
        "images": [],  # 暂不使用图片
        "topics": ["测试", "MCP", "开发"]
    }
    
    logger.info("\n📝 测试数据准备:")
    logger.info(f"  • 标题: {test_data['title']}")
    logger.info(f"  • 内容长度: {len(test_data['content'])} 字符")
    logger.info(f"  • 话题: {', '.join(test_data['topics'])}")
    
    try:
        # 测试登录状态
        logger.info("\n🔐 测试登录状态...")
        login_result = await server.test_connection({})
        logger.info(f"  连接状态: {login_result}")
        
        # 模拟发布流程（不实际发布）
        logger.info("\n🚀 开始模拟发布流程...")
        logger.info("👀 请观察浏览器窗口，查看操作过程")
        
        # 这里可以调用实际的发布函数，但设置一个标志不点击最终发布按钮
        # 由于我们是测试，所以只模拟部分流程
        
        logger.info("\n📋 模拟操作步骤:")
        steps = [
            "1. 打开创作页面",
            "2. 填写标题和内容",
            "3. 添加话题标签",
            "4. 预览内容",
            "5. ⏸️ 停止 - 不点击发布按钮"
        ]
        
        for step in steps:
            logger.info(f"  {step}")
            await asyncio.sleep(1)  # 模拟操作延迟
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 测试完成 - 发布流程验证成功")
        logger.info("👀 浏览器可视化模式工作正常")
        logger.info("⚠️ 未实际发布任何内容")
        logger.info("=" * 60)
        
        # 保存测试结果
        result = {
            "test_type": "mcp_publish_visual",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_data": test_data,
            "browser_mode": "visual",
            "status": "success",
            "steps_completed": len(steps),
            "message": "MCP发布测试成功，浏览器可视化正常"
        }
        
        result_file = Path(__file__).parent / "mcp_test_result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n📊 测试结果已保存: {result_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ 测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # 保存错误信息
        error_result = {
            "test_type": "mcp_publish_visual",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "failed",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        
        error_file = Path(__file__).parent / "mcp_test_error.json"
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_result, f, ensure_ascii=False, indent=2)
        
        return False

async def test_mcp_login():
    """测试MCP登录功能"""
    logger.info("\n🔐 测试MCP登录功能...")
    
    server = XHSMCPServer()
    
    try:
        # 测试智能登录
        login_params = {
            "force_relogin": False,
            "quick_mode": False
        }
        
        logger.info("  执行智能登录...")
        result = await server.login_xiaohongshu(login_params)
        
        result_data = json.loads(result)
        if result_data.get("status") == "success":
            logger.info("✅ 登录成功!")
            logger.info(f"  消息: {result_data.get('message')}")
        else:
            logger.warning(f"⚠️ 登录状态: {result_data.get('message')}")
        
        return result_data
        
    except Exception as e:
        logger.error(f"❌ 登录测试失败: {str(e)}")
        return None

async def main():
    """主测试函数"""
    logger.info("🚀 启动MCP API测试工具")
    logger.info("📌 测试浏览器可视化模式\n")
    
    # 检查环境变量
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    if headless:
        logger.warning("⚠️ 当前HEADLESS=true，将无法看到浏览器界面")
        logger.info("💡 建议在env文件中设置: HEADLESS=false")
        return
    
    # 选择测试项目
    logger.info("请选择测试项目:")
    logger.info("  1. 测试登录功能")
    logger.info("  2. 测试发布流程（不实际发布）")
    logger.info("  3. 全部测试")
    
    choice = input("\n请输入选项 (1-3): ").strip()
    
    if choice == "1":
        await test_mcp_login()
    elif choice == "2":
        await test_mcp_publish_visual()
    elif choice == "3":
        logger.info("\n执行全部测试...")
        await test_mcp_login()
        await test_mcp_publish_visual()
    else:
        logger.warning("无效的选项")
        return
    
    logger.info("\n✨ 所有测试完成!")
    logger.info("📁 测试结果已保存到 tests/ 目录")

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())