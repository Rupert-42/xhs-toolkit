#!/usr/bin/env python
"""
实际发布测试笔记到小红书
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

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

from src.core.config import XHSConfig
from src.server.mcp_server import MCPServer


async def publish_test_note():
    """发布测试笔记"""
    logger.info("="*60)
    logger.info("🚀 开始发布测试笔记到小红书")
    logger.info("="*60)
    
    try:
        # 创建配置和服务器实例
        config = XHSConfig()
        server = MCPServer(config)
        
        # 准备测试笔记内容
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        test_note = {
            "title": f"🧪 XHS工具包测试 - {current_time}",
            "content": f"""这是一篇由XHS-Toolkit自动发布的测试笔记！

📅 发布时间: {current_time}
🔧 工具版本: 1.3.0
✨ 新功能测试:

1️⃣ 网络图片URL支持 ✅
   - 支持直接使用网络图片链接
   - 自动下载并处理图片
   
2️⃣ 智能路径解析 ✅
   - 自动识别URL和本地路径
   - 混合使用多种格式
   
3️⃣ 增强日志输出 ✅
   - 详细的处理过程日志
   - 方便问题定位和调试

🎯 测试目标:
验证图片URL功能是否正常工作

💡 技术栈:
Python + Selenium + FastMCP + Async

#小红书工具 #自动化测试 #开发工具 #技术分享 #Python开发""",
            "images": [
                "https://picsum.photos/seed/xhs-test1/600/400",  # 使用固定seed确保图片一致
                "https://picsum.photos/seed/xhs-test2/600/400",
                "https://picsum.photos/seed/xhs-test3/600/400"
            ],
            "topics": ["技术分享", "开发工具", "自动化测试"],
            "location": "技术实验室"
        }
        
        logger.info("📝 笔记内容准备完成:")
        logger.info(f"  标题: {test_note['title']}")
        logger.info(f"  内容长度: {len(test_note['content'])} 字符")
        logger.info(f"  图片数量: {len(test_note['images'])}")
        logger.info(f"  话题: {test_note['topics']}")
        
        # 调用发布接口
        logger.info("\n📤 调用smart_publish_note发布笔记...")
        # 直接调用服务器中定义的工具函数
        result = await server.mcp._tools["smart_publish_note"]["handler"](
            title=test_note["title"],
            content=test_note["content"],
            images=test_note["images"],
            topics=test_note["topics"],
            location=test_note["location"]
        )
        
        # 解析结果
        result_data = json.loads(result)
        logger.info("\n📊 任务创建结果:")
        logger.info(json.dumps(result_data, ensure_ascii=False, indent=2))
        
        if result_data.get("success"):
            task_id = result_data.get("task_id")
            logger.info(f"\n✅ 任务创建成功! 任务ID: {task_id}")
            
            # 监控任务状态
            logger.info("\n⏳ 等待发布完成...")
            max_wait = 120  # 最多等待120秒
            check_interval = 5  # 每5秒检查一次
            elapsed = 0
            
            while elapsed < max_wait:
                await asyncio.sleep(check_interval)
                elapsed += check_interval
                
                # 检查任务状态
                status_result = await server.mcp._tools["check_task_status"]["handler"](task_id=task_id)
                status_data = json.loads(status_result)
                
                logger.info(f"[{elapsed}s] 状态: {status_data.get('status')} | 进度: {status_data.get('progress')}% | {status_data.get('message')}")
                
                # 检查是否完成
                if status_data.get("is_completed"):
                    if status_data.get("status") == "completed":
                        logger.info("\n🎉 发布成功!")
                        
                        # 获取最终结果
                        final_result = await server.mcp._tools["get_task_result"]["handler"](task_id=task_id)
                        final_data = json.loads(final_result)
                        logger.info("\n📋 最终结果:")
                        logger.info(json.dumps(final_data, ensure_ascii=False, indent=2))
                        
                        if final_data.get("publish_result", {}).get("final_url"):
                            logger.info(f"\n🔗 笔记链接: {final_data['publish_result']['final_url']}")
                    else:
                        logger.error(f"\n❌ 发布失败: {status_data.get('message')}")
                    break
            
            if elapsed >= max_wait:
                logger.warning(f"\n⚠️ 等待超时 ({max_wait}秒)")
                
        else:
            logger.error(f"❌ 任务创建失败: {result_data.get('message')}")
            
    except Exception as e:
        logger.error(f"❌ 发布失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    logger.info("\n" + "="*60)
    logger.info("测试结束")
    logger.info("="*60)


async def main():
    """主函数"""
    logger.info("🌺 小红书测试笔记发布程序")
    logger.info(f"⏰ 开始时间: {datetime.now()}")
    
    # 提示用户
    logger.info("\n⚠️ 注意事项:")
    logger.info("1. 请确保已经登录小红书（运行过 ./xhs server start 并登录）")
    logger.info("2. 请确保MCP服务器正在运行")
    logger.info("3. 发布过程可能需要1-2分钟")
    
    logger.info("\n准备发布测试笔记...")
    await asyncio.sleep(2)  # 给用户时间阅读提示
    
    # 发布测试笔记
    await publish_test_note()
    
    logger.info(f"\n✨ 程序结束! 时间: {datetime.now()}")


if __name__ == "__main__":
    asyncio.run(main())