#!/usr/bin/env python
"""
发布关于NIW(National Interest Waiver)的小红书笔记
"""

import asyncio
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

from src.xiaohongshu.models import XHSNote
from src.xiaohongshu.client import XHSClient
from src.core.config import XHSConfig


async def publish_niw_note():
    """发布NIW相关的小红书笔记"""
    logger.info("="*60)
    logger.info("📚 发布NIW国家利益豁免移民笔记")
    logger.info("="*60)
    
    try:
        # 创建配置和客户端
        config = XHSConfig()
        client = XHSClient(config)
        
        # 准备NIW相关内容
        current_time = datetime.now().strftime('%m月%d日')
        
        logger.info("📝 创建NIW笔记...")
        note = await XHSNote.async_smart_create(
            title=f"🇺🇸 NIW国家利益豁免 | 无需雇主的美国绿卡途径",
            content=f"""你知道吗？有一种美国绿卡申请方式，不需要雇主担保，不需要劳工证，甚至可以自己给自己申请！这就是NIW（National Interest Waiver）国家利益豁免。

✨ 什么是NIW？
NIW是EB-2类别下的特殊通道，申请人可以基于自身对美国国家利益的贡献，申请豁免劳工证和雇主担保的要求。

📋 NIW的三大优势：
1️⃣ 无需雇主担保 - 自由度高，不受雇主限制
2️⃣ 无需劳工证 - 省时省力，流程简化
3️⃣ 可同时递交I-140和I-485 - 加快绿卡进程

🎯 适合人群：
• STEM领域的研究人员和工程师
• 医疗健康领域的专业人士
• 商业领域的企业家
• 艺术、教育等领域的杰出人才

💡 申请要点：
关键在于证明你的工作对美国具有实质性价值和国家重要性，且你有能力推进相关领域的发展。

📊 成功案例：
许多博士、资深工程师、医生等专业人士通过NIW成功获得绿卡，平均审理时间约12-18个月。

想了解更多NIW申请细节？欢迎留言交流！

#美国移民 #NIW #国家利益豁免 #美国绿卡 #EB2 #移民申请 #STEM移民 #自主移民""",
            images=[
                "https://images.unsplash.com/photo-1565043589221-1a6fd9ae45c7?w=600&h=400",  # 自由女神像
                "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=600&h=400",  # 签证文件
                "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=600&h=400"   # 美国国旗
            ],
            topics=["美国移民", "NIW", "绿卡申请", "移民知识", "留学生活"],
            location="移民咨询"
        )
        
        logger.info(f"✅ 笔记创建成功")
        logger.info(f"  标题: {note.title}")
        logger.info(f"  内容长度: {len(note.content)} 字符")
        logger.info(f"  图片数: {len(note.images) if note.images else 0}")
        logger.info(f"  话题: {note.topics}")
        
        # 检查cookies
        cookies = client.cookie_manager.load_cookies()
        if not cookies:
            logger.warning("⚠️ 未找到cookies，需要先登录")
            logger.info("请运行: ./xhs login 进行登录")
            return
        
        logger.info(f"✅ 找到 {len(cookies)} 个cookies")
        
        # 发布笔记
        logger.info("\n📤 开始发布NIW笔记...")
        result = await client.publish_note(note)
        
        # 显示结果
        if result.success:
            logger.info(f"🎉 发布成功!")
            logger.info(f"  消息: {result.message}")
            if result.final_url:
                logger.info(f"  笔记链接: {result.final_url}")
        else:
            logger.error(f"❌ 发布失败: {result.message}")
            if result.error_type:
                logger.error(f"  错误类型: {result.error_type}")
    
    except Exception as e:
        logger.error(f"❌ 发布失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    logger.info("\n" + "="*60)
    logger.info("发布流程结束")
    logger.info("="*60)


async def main():
    """主函数"""
    logger.info("🌟 小红书NIW笔记发布程序")
    logger.info(f"⏰ 开始时间: {datetime.now()}")
    
    await publish_niw_note()
    
    logger.info(f"\n✨ 结束时间: {datetime.now()}")


if __name__ == "__main__":
    asyncio.run(main())