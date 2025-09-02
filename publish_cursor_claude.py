#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发布Cursor vs Claude的小红书笔记
"""

import sys
import asyncio
from pathlib import Path
sys.path.insert(0, '/Users/rupert/mcp_service/xhs-toolkit')

from src.xiaohongshu.models import XHSNote
from src.xiaohongshu.client import XHSClient
from src.core.config import XHSConfig
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('publish_cursor_claude.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

async def publish_note():
    """发布笔记到小红书"""
    try:
        # 读取笔记内容
        content_file = Path('/Users/rupert/xiaohongshu-agent-team/projects/2025-09-02-cursor-vs-claude/final_content.txt')
        with open(content_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info("📝 准备发布内容:")
        logger.info(f"标题: 从Cursor叛逃到Claude的72小时")
        logger.info(f"字数: {len(content)}字符")
        
        # 准备图片路径（使用已转换的PNG图片）
        images_dir = Path('/Users/rupert/xiaohongshu-agent-team/projects/2025-09-02-cursor-vs-claude/png_images')
        
        # PNG图片文件列表（按顺序）
        png_files = [
            'cover.png',
            'scene-1.png',
            'scene-2.png', 
            'scene-3.png',
            'scene-4.png',
            'scene-5.png',
            'scene-6.png',
            'comparison.png'
        ]
        
        # 构建图片路径列表
        image_paths = []
        for png_file in png_files:
            png_path = images_dir / png_file
            if png_path.exists():
                image_paths.append(str(png_path))
                logger.info(f"✅ 找到图片: {png_file}")
            else:
                logger.warning(f"⚠️ 图片不存在: {png_file}")
        
        logger.info(f"📸 共找到 {len(image_paths)} 张PNG图片")
        
        # 创建笔记对象
        note = await XHSNote.async_smart_create(
            title="从Cursor叛逃到Claude的72小时",
            content=content,
            topics=["编程工具", "AI编程", "程序员", "技术分享", "Claude", "Cursor"],
            images=image_paths  # PNG图片路径列表
        )
        
        logger.info(f"📋 笔记创建成功: {note.title}")
        logger.info(f"🏷️ 话题: {note.topics}")
        logger.info(f"📸 图片数量: {len(note.images) if note.images else 0}")
        
        # 初始化客户端
        config = XHSConfig()
        client = XHSClient(config)
        
        # 发布笔记
        logger.info("🚀 开始发布笔记...")
        result = await client.publish_note(note)
        
        if result.success:
            logger.info(f"✅ 发布成功!")
            logger.info(f"📄 标题: {result.note_title}")
            if result.final_url:
                logger.info(f"🔗 笔记链接: {result.final_url}")
        else:
            logger.error(f"❌ 发布失败: {result.message}")
            if result.error_type:
                logger.error(f"错误类型: {result.error_type}")
        
        return result
        
    except Exception as e:
        logger.error(f"💥 发布过程出错: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("发布 Cursor vs Claude 小红书笔记")  
    print("=" * 60)
    
    result = asyncio.run(publish_note())
    
    if result:
        print("\n🎉 发布任务完成!")
        print(f"成功: {result.success}")
        print(f"消息: {result.message}")
    else:
        print("\n⚠️ 发布失败，请查看日志文件")