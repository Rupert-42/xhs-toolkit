#!/usr/bin/env python
"""
通过HTTP调用MCP服务器发布测试笔记
"""

import aiohttp
import asyncio
import json
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


async def call_mcp_tool(tool_name: str, params: dict):
    """调用MCP工具"""
    url = "http://localhost:8000/sse"
    
    # 构建JSON-RPC请求
    request_data = {
        "jsonrpc": "2.0",
        "method": f"tools/{tool_name}",
        "params": params,
        "id": 1
    }
    
    logger.info(f"🔄 调用MCP工具: {tool_name}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=request_data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    logger.error(f"HTTP错误: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"调用失败: {e}")
        return None


async def test_publish():
    """测试发布功能"""
    logger.info("="*60)
    logger.info("🌺 小红书测试笔记发布 (HTTP调用)")
    logger.info("="*60)
    
    # 准备测试笔记
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    test_note = {
        "title": f"🧪 测试发布 - {current_time}",
        "content": f"""这是通过xhs-toolkit自动发布的测试笔记！

📅 时间: {current_time}
✨ 功能测试:

✅ 网络图片URL支持
✅ 自动下载处理
✅ MCP协议通信

测试图片来源: Lorem Picsum (随机图片服务)

#测试 #自动化 #小红书工具""",
        "images": "https://picsum.photos/seed/xhs1/600/400,https://picsum.photos/seed/xhs2/600/400",
        "topics": "测试,自动化工具",
        "location": "技术实验室"
    }
    
    logger.info(f"📝 准备发布笔记: {test_note['title']}")
    
    # 调用发布接口
    result = await call_mcp_tool("smart_publish_note", test_note)
    
    if result:
        logger.info("📊 调用结果:")
        logger.info(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 检查是否成功
        if result.get("result"):
            result_data = json.loads(result["result"])
            if result_data.get("success"):
                task_id = result_data.get("task_id")
                logger.info(f"✅ 任务创建成功: {task_id}")
                
                # 等待并检查状态
                logger.info("⏳ 等待发布完成...")
                await asyncio.sleep(10)
                
                # 检查任务状态
                status_result = await call_mcp_tool("check_task_status", {"task_id": task_id})
                if status_result:
                    logger.info("📊 任务状态:")
                    logger.info(json.dumps(status_result, ensure_ascii=False, indent=2))
    else:
        logger.error("❌ 调用MCP服务器失败")
    
    logger.info("="*60)
    logger.info("测试结束")


async def main():
    """主函数"""
    logger.info("🚀 MCP测试程序启动")
    logger.info("请确保MCP服务器正在运行 (端口8000)")
    
    await test_publish()
    
    logger.info("✨ 程序结束")


if __name__ == "__main__":
    asyncio.run(main())