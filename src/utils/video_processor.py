"""
视频处理模块

支持多种视频输入格式的处理：
- 本地文件路径（绝对路径和相对路径）
- 多种输入格式（字符串、数组、JSON等）
"""

import os
import json
from pathlib import Path
from typing import List, Union, Optional, Tuple

from .logger import get_logger

logger = get_logger(__name__)


class VideoProcessor:
    """视频处理器，支持多种路径格式"""
    
    def __init__(self, base_dir: str = None):
        """
        初始化视频处理器
        
        Args:
            base_dir: 用于解析相对路径的基础目录
        """
        # 设置基础目录（用于相对路径解析）
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        logger.info(f"视频处理器初始化，基础目录: {self.base_dir}")
    
    def process_videos(self, videos_input: Union[str, List, None]) -> Tuple[List[str], Optional[str]]:
        """
        处理各种格式的视频输入，返回本地文件路径列表和可能的错误信息
        
        支持格式：
        - 本地路径: "/path/to/video.mp4" 或 "./relative/path.mp4"
        - JSON数组: ["path1.mp4", "path2.mp4"]
        - 逗号分隔: "path1.mp4,path2.mp4"
        
        Args:
            videos_input: 视频输入（支持多种格式）
            
        Returns:
            Tuple[List[str], Optional[str]]: (本地文件路径列表, 错误信息)
        """
        logger.info(f"🎬 VideoProcessor.process_videos - 输入类型: {type(videos_input)}, 内容: {videos_input}")
        
        if not videos_input:
            logger.info("💭 视频输入为空，返回空列表")
            return [], None
        
        # 统一转换为列表格式
        videos_list = self._normalize_to_list(videos_input)
        logger.info(f"📦 标准化后的视频列表: {videos_list}")
        
        # 小红书只支持单个视频
        if len(videos_list) > 1:
            error_msg = f"小红书只支持发布1个视频文件，但收到了 {len(videos_list)} 个视频"
            logger.error(f"❌ {error_msg}")
            return [], error_msg
        
        # 处理视频路径
        local_paths = []
        failed_videos = []
        
        for idx, video in enumerate(videos_list):
            try:
                logger.info(f"🎯 处理视频: {video}")
                local_path = self._process_single_video(video)
                if local_path:
                    local_paths.append(local_path)
                    logger.info(f"✅ 处理视频成功: {local_path}")
                else:
                    logger.warning(f"⚠️ 处理视频返回None: {video}")
                    failed_videos.append(video)
            except Exception as e:
                logger.error(f"❌ 处理视频失败: {e}")
                failed_videos.append(f"{video} (错误: {str(e)})")
                
        # 生成错误信息
        error_msg = None
        if failed_videos and not local_paths:
            error_msg = self._generate_error_message(failed_videos, videos_input)
        
        return local_paths, error_msg
    
    def _normalize_to_list(self, videos_input: Union[str, List]) -> List:
        """将各种输入格式统一转换为列表"""
        logger.info(f"🔄 _normalize_to_list - 输入类型: {type(videos_input)}")
        
        if isinstance(videos_input, str):
            videos_str = videos_input.strip()
            
            # 尝试解析 JSON 数组
            if videos_str.startswith('[') and videos_str.endswith(']'):
                try:
                    parsed = json.loads(videos_str)
                    if isinstance(parsed, list):
                        result = [str(item).strip() for item in parsed if str(item).strip()]
                        logger.info(f"📦 JSON数组解析结果: {result}")
                        return result
                except json.JSONDecodeError:
                    # 可能是格式不标准的数组，尝试手动解析
                    try:
                        inner = videos_str[1:-1].strip()
                        if inner:
                            result = [item.strip().strip('"\'') for item in inner.split(',')]
                            result = [item for item in result if item]
                            logger.info(f"📦 手动数组解析结果: {result}")
                            return result
                    except:
                        pass
            
            # 逗号分隔的多个路径
            if ',' in videos_str:
                result = [v.strip().strip('"\'') for v in videos_str.split(',') if v.strip()]
                logger.info(f"📦 逗号分隔字符串转换结果: {result}")
                return result
            else:
                # 单个路径
                logger.info(f"📦 单个字符串转换结果: [{videos_str}]")
                return [videos_str]
                
        elif isinstance(videos_input, list):
            # 确保列表中的每个元素都是字符串
            result = []
            for item in videos_input:
                if isinstance(item, str):
                    result.append(item.strip())
                else:
                    result.append(str(item).strip())
            logger.info(f"📦 列表格式处理结果: {result}")
            return result
        else:
            # 其他类型，尝试转换为字符串
            logger.warning(f"⚠️ 不常见的输入类型: {type(videos_input)}，尝试转换为字符串")
            try:
                return self._normalize_to_list(str(videos_input))
            except:
                return []
    
    def _process_single_video(self, video_input: str) -> Optional[str]:
        """
        处理单个视频输入
        
        Args:
            video_input: 视频输入（字符串）
            
        Returns:
            Optional[str]: 本地文件路径，失败返回None
        """
        logger.info(f"🎯 _process_single_video - 输入: {video_input}")
        
        if not isinstance(video_input, str):
            logger.warning(f"⚠️ 无效的视频输入类型: {type(video_input)}")
            return None
            
        video_input = video_input.strip()
        
        # 检查文件扩展名
        valid_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.m4v']
        _, ext = os.path.splitext(video_input.lower())
        if ext not in valid_extensions:
            raise ValueError(f"不支持的视频格式: {ext}，支持的格式: {valid_extensions}")
        
        # 尝试解析本地路径
        # 1. 首先尝试原始路径
        if os.path.exists(video_input):
            abs_path = os.path.abspath(video_input)
            logger.info(f"📁 检测到本地视频文件（绝对/相对路径）: {abs_path}")
            return abs_path
        
        # 2. 如果是相对路径，尝试从基础目录解析
        if not os.path.isabs(video_input):
            base_path = self.base_dir / video_input
            if base_path.exists():
                abs_path = str(base_path.resolve())
                logger.info(f"📁 从基础目录解析相对路径成功: {video_input} -> {abs_path}")
                return abs_path
            
            # 3. 尝试从当前工作目录解析
            cwd_path = Path.cwd() / video_input
            if cwd_path.exists():
                abs_path = str(cwd_path.resolve())
                logger.info(f"📁 从当前目录解析相对路径成功: {video_input} -> {abs_path}")
                return abs_path
        
        # 路径无效
        logger.warning(f"⚠️ 无法找到视频文件: {video_input}")
        logger.info(f"   尝试过的路径:")
        logger.info(f"   - 原始路径: {video_input}")
        if not os.path.isabs(video_input):
            logger.info(f"   - 基础目录: {self.base_dir / video_input}")
            logger.info(f"   - 当前目录: {Path.cwd() / video_input}")
        
        raise FileNotFoundError(f"无法找到视频文件: {video_input}")
    
    def _generate_error_message(self, failed_videos: List[str], original_input) -> str:
        """
        生成友好的错误提示信息
        
        Args:
            failed_videos: 处理失败的视频列表
            original_input: 原始输入
            
        Returns:
            str: 错误提示信息
        """
        error_parts = ["未能读取到参数中的视频"]
        
        if failed_videos:
            error_parts.append(f"\n失败的文件: {failed_videos[0]}")
        
        error_parts.append("\n\n请使用以下格式之一：")
        error_parts.append("1. 单个视频路径: \"video.mp4\"")
        error_parts.append("2. JSON数组（仅限1个）: [\"video.mp4\"]")
        error_parts.append("3. 相对路径: \"./videos/video.mp4\"")
        error_parts.append("4. 绝对路径: \"/Users/name/Desktop/video.mp4\"")
        error_parts.append("\n支持的格式: .mp4, .mov, .avi, .mkv, .flv, .wmv, .m4v")
        error_parts.append("\n提示: 小红书只支持发布1个视频文件")
        
        return ''.join(error_parts)