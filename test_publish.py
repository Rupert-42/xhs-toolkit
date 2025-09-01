#!/usr/bin/env python
"""
测试小红书发布功能，包括网络图片URL支持
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# 导入所需模块
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.xiaohongshu.models import XHSNote
from src.core.config import XHSConfig
from src.server.mcp_server import MCPServer


async def test_image_url_support():
    """测试图片URL支持功能"""
    logger.info("=" * 60)
    logger.info("🧪 开始测试图片URL支持功能")
    logger.info("=" * 60)
    
    # 测试数据
    test_cases = [
        {
            "name": "网络图片URL测试",
            "title": f"测试笔记 - 网络图片 {datetime.now().strftime('%H:%M:%S')}",
            "content": "这是一个测试笔记，用于验证网络图片URL功能是否正常工作。\n\n测试内容：\n1. 支持网络图片URL下载\n2. 支持混合本地和网络图片\n3. 添加了详细的调试日志\n\n#测试 #小红书工具",
            "images": "https://picsum.photos/400/300",  # 使用随机图片服务
            "topics": ["测试", "工具测试"],
            "location": "测试地点"
        },
        {
            "name": "混合图片测试（如果有本地图片）",
            "title": f"测试笔记 - 混合图片 {datetime.now().strftime('%H:%M:%S')}",
            "content": "这是一个混合图片测试，同时包含网络和本地图片。\n\n测试要点：\n- 网络图片自动下载\n- 本地图片直接使用\n- 验证器正确处理\n\n#混合测试 #图片处理",
            "images": ["https://picsum.photos/400/300", "https://picsum.photos/300/400"],  # 多个网络图片
            "topics": ["混合测试", "图片处理"],
            "location": "测试实验室"
        }
    ]
    
    # 执行测试
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n{'='*50}")
        logger.info(f"📝 执行测试用例 {i}: {test_case['name']}")
        logger.info(f"{'='*50}")
        
        try:
            # 使用async_smart_create创建笔记
            logger.info(f"🔄 创建XHSNote对象...")
            note = await XHSNote.async_smart_create(
                title=test_case["title"],
                content=test_case["content"],
                images=test_case["images"],
                topics=test_case["topics"],
                location=test_case["location"]
            )
            
            logger.info(f"✅ 笔记创建成功!")
            logger.info(f"  - 标题: {note.title}")
            logger.info(f"  - 内容长度: {len(note.content)} 字符")
            logger.info(f"  - 图片数量: {len(note.images) if note.images else 0}")
            if note.images:
                for idx, img_path in enumerate(note.images, 1):
                    logger.info(f"    [{idx}] {img_path}")
            logger.info(f"  - 话题: {note.topics}")
            logger.info(f"  - 位置: {note.location}")
            
            # 验证图片文件是否存在
            if note.images:
                logger.info(f"\n🔍 验证图片文件...")
                for img_path in note.images:
                    if Path(img_path).exists():
                        file_size = Path(img_path).stat().st_size
                        logger.info(f"  ✅ 文件存在: {img_path} (大小: {file_size} bytes)")
                    else:
                        logger.error(f"  ❌ 文件不存在: {img_path}")
            
        except Exception as e:
            logger.error(f"❌ 测试失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    logger.info(f"\n{'='*60}")
    logger.info("🎉 测试完成!")
    logger.info(f"{'='*60}")


async def test_mcp_publish():
    """测试通过MCP服务器发布笔记"""
    logger.info("\n" + "="*60)
    logger.info("🚀 测试MCP服务器发布功能")
    logger.info("="*60)
    
    try:
        # 创建配置和服务器实例
        config = XHSConfig()
        server = MCPServer(config)
        
        # 准备测试数据
        test_data = {
            "title": f"MCP测试笔记 {datetime.now().strftime('%m-%d %H:%M')}",
            "content": "通过MCP服务器发布的测试笔记。\n\n功能验证：\n✅ 网络图片URL支持\n✅ 自动下载和处理\n✅ 调试日志输出\n\n#MCP测试 #自动发布",
            "images": "https://picsum.photos/500/400",
            "topics": "MCP测试,自动化",
            "location": "测试环境"
        }
        
        logger.info("📤 调用smart_publish_note...")
        logger.info(f"  标题: {test_data['title']}")
        logger.info(f"  图片: {test_data['images']}")
        
        # 模拟MCP调用
        result = await server.mcp.tools["smart_publish_note"](
            title=test_data["title"],
            content=test_data["content"],
            images=test_data["images"],
            topics=test_data["topics"],
            location=test_data["location"]
        )
        
        # 解析结果
        result_data = json.loads(result)
        logger.info(f"\n📊 发布结果:")
        logger.info(json.dumps(result_data, ensure_ascii=False, indent=2))
        
        if result_data.get("success"):
            task_id = result_data.get("task_id")
            logger.info(f"\n✅ 任务创建成功! 任务ID: {task_id}")
            
            # 等待一段时间后检查状态
            await asyncio.sleep(3)
            
            logger.info(f"\n🔍 检查任务状态...")
            status_result = await server.mcp.tools["check_task_status"](task_id=task_id)
            status_data = json.loads(status_result)
            logger.info(json.dumps(status_data, ensure_ascii=False, indent=2))
            
        else:
            logger.error(f"❌ 任务创建失败: {result_data.get('message')}")
            
    except Exception as e:
        logger.error(f"❌ MCP测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())


async def main():
    """主测试函数"""
    logger.info("🧪 小红书工具包测试程序")
    logger.info(f"⏰ 开始时间: {datetime.now()}")
    
    # 测试1: 图片URL支持
    await test_image_url_support()
    
    # 测试2: MCP服务器发布（可选）
    logger.info("\n" + "="*60)
    logger.info("跳过MCP服务器测试（需要手动运行）")
    logger.info("如需测试MCP服务器，请运行: python3 test_publish.py --mcp")
    
    logger.info(f"\n✨ 所有测试完成! 结束时间: {datetime.now()}")


if __name__ == "__main__":
    asyncio.run(main())