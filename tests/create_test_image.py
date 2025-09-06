#!/usr/bin/env python3
"""
创建真实的测试图片文件
使用纯Python创建一个简单的BMP图片
"""

import struct
import os
from datetime import datetime

def create_simple_bmp(filename, width=100, height=100, color=(255, 0, 0)):
    """创建一个简单的BMP图片文件"""
    
    # BMP文件头
    file_size = 54 + width * height * 3  # 文件头 + 图像数据
    reserved = 0
    offset = 54
    
    # BMP信息头
    header_size = 40
    planes = 1
    bits_per_pixel = 24
    compression = 0
    image_size = width * height * 3
    x_pixels_per_meter = 0
    y_pixels_per_meter = 0
    colors_used = 0
    important_colors = 0
    
    # 创建文件
    with open(filename, 'wb') as f:
        # 写入文件头
        f.write(b'BM')  # 签名
        f.write(struct.pack('<I', file_size))
        f.write(struct.pack('<H', reserved))
        f.write(struct.pack('<H', reserved))
        f.write(struct.pack('<I', offset))
        
        # 写入信息头
        f.write(struct.pack('<I', header_size))
        f.write(struct.pack('<I', width))
        f.write(struct.pack('<I', height))
        f.write(struct.pack('<H', planes))
        f.write(struct.pack('<H', bits_per_pixel))
        f.write(struct.pack('<I', compression))
        f.write(struct.pack('<I', image_size))
        f.write(struct.pack('<I', x_pixels_per_meter))
        f.write(struct.pack('<I', y_pixels_per_meter))
        f.write(struct.pack('<I', colors_used))
        f.write(struct.pack('<I', important_colors))
        
        # 写入图像数据（从下到上，BGR格式）
        b, g, r = color
        pixel = struct.pack('BBB', b, g, r)
        row_padding = (4 - (width * 3) % 4) % 4
        
        for y in range(height):
            for x in range(width):
                # 创建简单的渐变效果
                if y < height // 3:
                    f.write(struct.pack('BBB', 255, 100, 100))  # 红色
                elif y < 2 * height // 3:
                    f.write(struct.pack('BBB', 100, 255, 100))  # 绿色
                else:
                    f.write(struct.pack('BBB', 100, 100, 255))  # 蓝色
            f.write(b'\x00' * row_padding)
    
    print(f"✅ 创建BMP图片: {filename}")
    return filename

def create_test_images(count=3):
    """创建多个测试图片
    
    Args:
        count: 要创建的图片数量
    
    Returns:
        图片路径列表
    """
    # 确保目录存在
    test_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(test_dir, "test_images")
    os.makedirs(images_dir, exist_ok=True)
    
    images = []
    colors = [
        (255, 100, 100),  # 红色调
        (100, 255, 100),  # 绿色调
        (100, 100, 255),  # 蓝色调
        (255, 255, 100),  # 黄色调
        (255, 100, 255),  # 紫色调
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i in range(count):
        # 创建测试图片
        image_path = os.path.join(images_dir, f"test_{timestamp}_{i+1}.bmp")
        
        # 使用不同的颜色创建图片
        color = colors[i % len(colors)]
        
        # 创建不同大小的图片(200-400像素)
        size = 200 + (i * 50)
        create_simple_bmp(image_path, width=size, height=size, color=color)
        
        # 验证文件
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"📊 图片{i+1} - 大小: {file_size} bytes, 尺寸: {size}x{size}")
            print(f"📍 路径: {image_path}")
            images.append(image_path)
        else:
            print(f"❌ 创建图片{i+1}失败")
    
    return images

if __name__ == "__main__":
    images = create_test_images(3)  # 创建3张测试图片
    if images:
        print(f"\n✨ 成功创建 {len(images)} 张测试图片！")
        for i, img in enumerate(images, 1):
            print(f"{i}. {img}")