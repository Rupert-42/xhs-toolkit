"""
图片处理模块

支持多种图片输入格式的处理：
- 本地文件路径
- 网络URL
"""

import os
import asyncio
import aiohttp
import tempfile
from pathlib import Path
from typing import List, Union, Optional, Tuple
import uuid
import json

from .logger import get_logger

logger = get_logger(__name__)


class ImageProcessor:
    """图片处理器，支持本地路径和URL下载"""
    
    def __init__(self, temp_dir: str = None, base_dir: str = None):
        """
        初始化图片处理器
        
        Args:
            temp_dir: 临时文件目录路径
            base_dir: 用于解析相对路径的基础目录
        """
        # 设置临时目录
        if temp_dir:
            self.temp_dir = Path(temp_dir)
        else:
            # 使用系统临时目录
            self.temp_dir = Path(tempfile.gettempdir()) / "xhs_images"
        
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        
        # 设置基础目录（用于相对路径解析）
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        
        logger.info(f"图片处理器初始化，临时目录: {self.temp_dir}")
        logger.info(f"基础目录（用于相对路径）: {self.base_dir}")
    
    async def process_images(self, images_input: Union[str, List, None]) -> Tuple[List[str], Optional[str]]:
        """
        处理各种格式的图片输入，返回本地文件路径列表和可能的错误信息
        
        支持格式：
        - 本地路径: "/path/to/image.jpg" 或 "./relative/path.jpg"
        - 网络地址: "https://example.com/image.jpg"
        - JSON数组: ["path1.jpg", "path2.jpg"]
        - 逗号分隔: "path1.jpg,path2.jpg"
        - 混合列表: ["path.jpg", "https://..."]
        
        Args:
            images_input: 图片输入（支持多种格式）
            
        Returns:
            Tuple[List[str], Optional[str]]: (本地文件路径列表, 错误信息)
        """
        logger.info(f"🔍 ImageProcessor.process_images - 输入类型: {type(images_input)}, 内容: {images_input}")
        
        if not images_input:
            logger.info("💭 图片输入为空，返回空列表")
            return [], None
        
        # 统一转换为列表格式
        images_list = self._normalize_to_list(images_input)
        logger.info(f"📦 标准化后的图片列表: {images_list}")
        
        # 处理每个图片
        local_paths = []
        failed_images = []
        
        for idx, img in enumerate(images_list):
            try:
                logger.info(f"🎯 处理第 {idx+1}/{len(images_list)} 张图片: {img}")
                local_path = await self._process_single_image(img, idx)
                if local_path:
                    local_paths.append(local_path)
                    logger.info(f"✅ 处理图片成功 [{idx+1}/{len(images_list)}]: {local_path}")
                else:
                    logger.warning(f"⚠️ 处理图片返回None [{idx+1}/{len(images_list)}]: {img}")
                    failed_images.append(img)
            except Exception as e:
                logger.error(f"❌ 处理图片失败 [{idx+1}/{len(images_list)}]: {e}")
                logger.error(f"🔍 失败的图片: {img}")
                failed_images.append(f"{img} (错误: {str(e)})")
                continue
        
        logger.info(f"📸 图片处理完成，共处理 {len(local_paths)}/{len(images_list)} 张")
        logger.info(f"📦 最终返回的本地路径: {local_paths}")
        
        # 生成错误信息
        error_msg = None
        if failed_images and not local_paths:
            error_msg = self._generate_error_message(failed_images, images_input)
        
        return local_paths, error_msg
    
    def _normalize_to_list(self, images_input: Union[str, List]) -> List:
        """将各种输入格式统一转换为列表"""
        logger.info(f"🔄 _normalize_to_list - 输入类型: {type(images_input)}")
        
        if isinstance(images_input, str):
            images_str = images_input.strip()
            
            # 尝试解析 JSON 数组
            if images_str.startswith('[') and images_str.endswith(']'):
                try:
                    parsed = json.loads(images_str)
                    if isinstance(parsed, list):
                        result = [str(item).strip() for item in parsed if str(item).strip()]
                        logger.info(f"📦 JSON数组解析结果: {result}")
                        return result
                except json.JSONDecodeError:
                    # 可能是格式不标准的数组，尝试手动解析
                    try:
                        inner = images_str[1:-1].strip()
                        if inner:
                            result = [item.strip().strip('"\'') for item in inner.split(',')]
                            result = [item for item in result if item]
                            logger.info(f"📦 手动数组解析结果: {result}")
                            return result
                    except:
                        pass
            
            # 逗号分隔的多个路径
            if ',' in images_str:
                result = [img.strip().strip('"\'') for img in images_str.split(',') if img.strip()]
                logger.info(f"📦 逗号分隔字符串转换结果: {result}")
                return result
            else:
                # 单个路径
                logger.info(f"📦 单个字符串转换结果: [{images_str}]")
                return [images_str]
                
        elif isinstance(images_input, list):
            # 确保列表中的每个元素都是字符串
            result = []
            for item in images_input:
                if isinstance(item, str):
                    result.append(item.strip())
                else:
                    result.append(str(item).strip())
            logger.info(f"📦 列表格式处理结果: {result}")
            return result
        else:
            # 其他类型，尝试转换为字符串
            logger.warning(f"⚠️ 不常见的输入类型: {type(images_input)}，尝试转换为字符串")
            try:
                return self._normalize_to_list(str(images_input))
            except:
                return []
    
    async def _process_single_image(self, img_input: str, index: int) -> Optional[str]:
        """
        处理单个图片输入
        
        Args:
            img_input: 图片输入（字符串）
            index: 图片索引
            
        Returns:
            Optional[str]: 本地文件路径，失败返回None
        """
        logger.info(f"🎯 _process_single_image - 输入: {img_input}, 类型: {type(img_input)}")
        
        if not isinstance(img_input, str):
            logger.warning(f"⚠️ 无效的图片输入类型: {type(img_input)}, 内容: {img_input}")
            return None
            
        img_input = img_input.strip()
        
        # 检查是否是网络地址
        if img_input.startswith(('http://', 'https://')):
            # 网络地址
            logger.info(f"🌐 检测到网络图片URL: {img_input}")
            return await self._download_from_url(img_input, index)
        
        # 尝试解析本地路径
        # 1. 首先尝试原始路径
        if os.path.exists(img_input):
            abs_path = os.path.abspath(img_input)
            logger.info(f"📁 检测到本地图片文件（绝对/相对路径）: {abs_path}")
            return abs_path
        
        # 2. 如果是相对路径，尝试从基础目录解析
        if not os.path.isabs(img_input):
            base_path = self.base_dir / img_input
            if base_path.exists():
                abs_path = str(base_path.resolve())
                logger.info(f"📁 从基础目录解析相对路径成功: {img_input} -> {abs_path}")
                return abs_path
            
            # 3. 尝试从当前工作目录解析
            cwd_path = Path.cwd() / img_input
            if cwd_path.exists():
                abs_path = str(cwd_path.resolve())
                logger.info(f"📁 从当前目录解析相对路径成功: {img_input} -> {abs_path}")
                return abs_path
        
        # 路径无效
        logger.warning(f"⚠️ 无法找到图片文件: {img_input}")
        logger.info(f"   尝试过的路径:")
        logger.info(f"   - 原始路径: {img_input}")
        if not os.path.isabs(img_input):
            logger.info(f"   - 基础目录: {self.base_dir / img_input}")
            logger.info(f"   - 当前目录: {Path.cwd() / img_input}")
        
        raise FileNotFoundError(f"无法找到图片文件: {img_input}")
    
    async def _download_from_url(self, url: str, index: int) -> Optional[str]:
        """
        下载网络图片到本地
        
        Args:
            url: 图片URL
            index: 图片索引
            
        Returns:
            Optional[str]: 本地文件路径，失败返回None
        """
        try:
            logger.info(f"⬇️ 开始下载图片: {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        logger.error(f"❌ 下载图片失败: {url}, 状态码: {response.status}")
                        return None
                    
                    # 获取文件扩展名
                    content_type = response.headers.get('content-type', '')
                    ext = self._get_extension_from_content_type(content_type)
                    if not ext:
                        # 从URL中尝试获取扩展名
                        url_path = Path(url.split('?')[0])
                        ext = url_path.suffix or '.jpg'
                    
                    # 生成唯一文件名
                    filename = f"download_{index}_{uuid.uuid4().hex[:8]}{ext}"
                    filepath = self.temp_dir / filename
                    
                    # 保存文件
                    content = await response.read()
                    filepath.write_bytes(content)
                    
                    logger.info(f"✅ 下载图片成功: {url} -> {filepath}")
                    return str(filepath)
                    
        except asyncio.TimeoutError:
            raise Exception(f"下载图片超时: {url}")
        except Exception as e:
            raise Exception(f"下载图片失败: {url}, 错误: {str(e)}")
    
    def _get_extension_from_content_type(self, content_type: str) -> str:
        """根据content-type获取文件扩展名"""
        mapping = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp'
        }
        
        # 提取主要的内容类型（去除参数）
        main_type = content_type.split(';')[0].strip().lower()
        return mapping.get(main_type, '')
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        清理超过指定时间的临时文件
        
        Args:
            max_age_hours: 文件最大保留时间（小时）
        """
        import time
        current_time = time.time()
        cleaned_count = 0
        
        try:
            for file in self.temp_dir.iterdir():
                if file.is_file():
                    file_age_hours = (current_time - file.stat().st_mtime) / 3600
                    if file_age_hours > max_age_hours:
                        try:
                            file.unlink()
                            cleaned_count += 1
                        except Exception as e:
                            logger.warning(f"清理文件失败: {file}, 错误: {e}")
            
            if cleaned_count > 0:
                logger.info(f"🧹 清理了 {cleaned_count} 个临时文件")
                
        except Exception as e:
            logger.error(f"清理临时文件出错: {e}")
    
    def _generate_error_message(self, failed_images: List[str], original_input) -> str:
        """
        生成友好的错误提示信息
        
        Args:
            failed_images: 处理失败的图片列表
            original_input: 原始输入
            
        Returns:
            str: 错误提示信息
        """
        error_parts = ["未能读取到参数中的图片"]
        
        if failed_images:
            error_parts.append(f"\n失败的文件: {', '.join(failed_images[:3])}")
            if len(failed_images) > 3:
                error_parts.append(f"... 等共 {len(failed_images)} 个文件")
        
        error_parts.append("\n\n请使用以下格式之一：")
        error_parts.append("1. JSON数组: [\"image1.jpg\", \"image2.jpg\"]")
        error_parts.append("2. 逗号分隔: \"image1.jpg,image2.jpg\"")
        error_parts.append("3. 网络图片: \"https://example.com/image.jpg\"")
        error_parts.append("4. 相对路径: \"./images/photo.jpg\"")
        error_parts.append("5. 绝对路径: \"/Users/name/Desktop/image.jpg\"")
        error_parts.append("\n提示: 确保文件路径正确且文件存在")
        
        return ''.join(error_parts)