#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将HTML文件转换为PNG图片
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def html_to_png(html_file: Path, output_file: Path):
    """将HTML文件转换为PNG图片"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 读取HTML内容
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 设置页面内容
        await page.set_content(html_content)
        await page.wait_for_timeout(2000)  # 等待渲染完成
        
        # 设置视口大小以适应小红书
        await page.set_viewport_size({"width": 1080, "height": 1920})
        
        # 截图
        await page.screenshot(path=str(output_file), full_page=True)
        await browser.close()
        
        logger.info(f"✅ 已生成图片: {output_file.name}")

async def convert_all_html_to_images():
    """转换所有HTML文件为图片"""
    project_dir = Path('/Users/rupert/xiaohongshu-agent-team/projects/2025-09-02-cursor-vs-claude')
    images_dir = project_dir / 'images'
    output_dir = project_dir / 'png_images'
    
    # 创建输出目录
    output_dir.mkdir(exist_ok=True)
    
    # HTML文件列表（按顺序）
    html_files = [
        'cover.html',
        'scene-1.html',
        'scene-2.html',
        'scene-3.html',
        'scene-4.html',
        'scene-5.html',
        'scene-6.html',
        'comparison.html'
    ]
    
    converted_images = []
    
    for html_file in html_files:
        html_path = images_dir / html_file
        if html_path.exists():
            # 生成输出文件名
            output_name = html_file.replace('.html', '.png')
            output_path = output_dir / output_name
            
            logger.info(f"🔄 正在转换: {html_file} -> {output_name}")
            await html_to_png(html_path, output_path)
            converted_images.append(str(output_path))
        else:
            logger.warning(f"⚠️ HTML文件不存在: {html_file}")
    
    return converted_images

if __name__ == "__main__":
    print("=" * 60)
    print("HTML转PNG工具")
    print("=" * 60)
    
    images = asyncio.run(convert_all_html_to_images())
    
    print(f"\n✅ 转换完成，共生成 {len(images)} 张图片:")
    for img in images:
        print(f"  📸 {Path(img).name}")