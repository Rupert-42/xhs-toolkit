#!/usr/bin/env python3
"""
测试 MCP API 改进功能
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path

# 设置项目路径
import sys
sys.path.append(str(Path(__file__).parent))

from src.utils.image_processor import ImageProcessor
from src.utils.video_processor import VideoProcessor
from src.xiaohongshu.models import XHSNote
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def test_image_formats():
    """测试各种图片输入格式"""
    print("\n" + "="*60)
    print("测试图片处理器的各种输入格式")
    print("="*60)
    
    # 创建临时测试文件
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # 创建测试图片文件
        test_images = []
        for i in range(3):
            img_path = tmpdir / f"test_{i}.jpg"
            img_path.write_text(f"fake image {i}")
            test_images.append(str(img_path))
        
        # 创建处理器
        processor = ImageProcessor(base_dir=tmpdir)
        
        # 测试案例
        test_cases = [
            # 格式1: 逗号分隔字符串
            (f"{test_images[0]},{test_images[1]}", "逗号分隔字符串"),
            
            # 格式2: JSON数组
            (json.dumps(test_images[:2]), "JSON数组"),
            
            # 格式3: Python列表
            (test_images[:2], "Python列表"),
            
            # 格式4: 单个文件
            (test_images[0], "单个文件路径"),
            
            # 格式5: 带引号的数组字符串
            (f'["{test_images[0]}", "{test_images[1]}"]', "带引号的数组字符串"),
            
            # 格式6: 相对路径
            ("test_0.jpg", "相对路径（文件名）"),
        ]
        
        for input_data, description in test_cases:
            print(f"\n测试: {description}")
            print(f"输入: {input_data}")
            
            try:
                result, error = await processor.process_images(input_data)
                if result:
                    print(f"✅ 成功: 处理了 {len(result)} 张图片")
                    for path in result:
                        print(f"  - {Path(path).name}")
                else:
                    print(f"❌ 失败: {error}")
            except Exception as e:
                print(f"❌ 异常: {e}")
        
        # 测试错误情况
        print("\n\n测试错误处理:")
        print("-" * 40)
        
        error_cases = [
            ("non_existent.jpg", "不存在的文件"),
            (["fake1.jpg", "fake2.jpg"], "多个不存在的文件"),
            ("", "空字符串"),
        ]
        
        for input_data, description in error_cases:
            print(f"\n测试: {description}")
            print(f"输入: {input_data}")
            
            try:
                result, error = await processor.process_images(input_data)
                if error:
                    print(f"✅ 正确返回错误信息:")
                    print(f"  {error[:100]}...")
                else:
                    print(f"⚠️ 未返回预期的错误信息")
            except Exception as e:
                print(f"✅ 捕获异常: {str(e)[:100]}...")


def test_video_formats():
    """测试各种视频输入格式"""
    print("\n" + "="*60)
    print("测试视频处理器的各种输入格式")
    print("="*60)
    
    # 创建临时测试文件
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # 创建测试视频文件
        video_path = tmpdir / "test_video.mp4"
        video_path.write_text("fake video content")
        
        # 创建处理器
        processor = VideoProcessor(base_dir=tmpdir)
        
        # 测试案例
        test_cases = [
            # 格式1: 单个文件路径
            (str(video_path), "绝对路径"),
            
            # 格式2: JSON数组（单个元素）
            (json.dumps([str(video_path)]), "JSON数组"),
            
            # 格式3: Python列表
            ([str(video_path)], "Python列表"),
            
            # 格式4: 相对路径
            ("test_video.mp4", "相对路径（文件名）"),
        ]
        
        for input_data, description in test_cases:
            print(f"\n测试: {description}")
            print(f"输入: {input_data}")
            
            try:
                result, error = processor.process_videos(input_data)
                if result:
                    print(f"✅ 成功: 处理了 {len(result)} 个视频")
                    for path in result:
                        print(f"  - {Path(path).name}")
                else:
                    print(f"❌ 失败: {error}")
            except Exception as e:
                print(f"❌ 异常: {e}")
        
        # 测试错误情况
        print("\n\n测试错误处理:")
        print("-" * 40)
        
        # 创建多个视频文件
        video2_path = tmpdir / "test_video2.mp4"
        video2_path.write_text("fake video 2")
        
        error_cases = [
            ("non_existent.mp4", "不存在的文件"),
            ([str(video_path), str(video2_path)], "多个视频（应该报错）"),
            ("test.txt", "不支持的格式"),
        ]
        
        for input_data, description in error_cases:
            print(f"\n测试: {description}")
            print(f"输入: {input_data}")
            
            try:
                result, error = processor.process_videos(input_data)
                if error:
                    print(f"✅ 正确返回错误信息:")
                    print(f"  {error[:100]}...")
                else:
                    print(f"⚠️ 未返回预期的错误信息")
            except Exception as e:
                print(f"✅ 捕获异常: {str(e)[:100]}...")


async def test_xhsnote_creation():
    """测试 XHSNote 的智能创建"""
    print("\n" + "="*60)
    print("测试 XHSNote 智能创建功能")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # 创建测试文件
        img1 = tmpdir / "image1.jpg"
        img1.write_text("fake image 1")
        img2 = tmpdir / "image2.jpg"
        img2.write_text("fake image 2")
        
        # 设置环境变量用于相对路径解析
        os.environ['MCP_WORKING_DIR'] = str(tmpdir)
        
        test_cases = [
            {
                "title": "测试笔记1",
                "content": "这是测试内容",
                "images": f"{img1},{img2}",
                "topics": "美食,生活",
                "description": "逗号分隔的图片和话题"
            },
            {
                "title": "测试笔记2",
                "content": "这是测试内容",
                "images": [str(img1), str(img2)],
                "topics": ["旅行", "摄影"],
                "description": "列表格式的图片和话题"
            },
            {
                "title": "测试笔记3",
                "content": "这是测试内容",
                "images": json.dumps(["image1.jpg", "image2.jpg"]),
                "topics": "购物",
                "description": "JSON格式的图片，相对路径"
            },
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n测试案例 {i}: {test_case['description']}")
            print(f"图片输入: {test_case['images']}")
            print(f"话题输入: {test_case['topics']}")
            
            try:
                note = await XHSNote.async_smart_create(
                    title=test_case['title'],
                    content=test_case['content'],
                    images=test_case['images'],
                    topics=test_case['topics']
                )
                print(f"✅ 成功创建笔记:")
                print(f"  - 标题: {note.title}")
                print(f"  - 图片数: {len(note.images) if note.images else 0}")
                print(f"  - 话题: {note.topics}")
            except Exception as e:
                print(f"❌ 创建失败: {e}")


async def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("MCP API 参数处理改进测试")
    print("="*80)
    
    # 测试图片格式
    await test_image_formats()
    
    # 测试视频格式
    test_video_formats()
    
    # 测试XHSNote创建
    await test_xhsnote_creation()
    
    print("\n" + "="*80)
    print("测试完成！")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())