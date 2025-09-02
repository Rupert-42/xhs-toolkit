"""
小红书相关数据模型

定义小红书笔记、用户、搜索结果等数据结构
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator
import logging

# 设置logger
logger = logging.getLogger(__name__)

# 尝试相对导入，失败则使用绝对导入
try:
    from ..utils.text_utils import validate_note_content, parse_topics_string, parse_file_paths_string, smart_parse_file_paths
except ImportError:
    from src.utils.text_utils import validate_note_content, parse_topics_string, parse_file_paths_string, smart_parse_file_paths


class XHSNote(BaseModel):
    """小红书笔记数据模型"""
    
    title: str
    content: str
    images: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    location: Optional[str] = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """验证标题"""
        if not v or not v.strip():
            raise ValueError("标题不能为空")
        if len(v.strip()) > 50:
            raise ValueError("标题长度不能超过50个字符")
        return v.strip()
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """验证内容"""
        if not v or not v.strip():
            raise ValueError("内容不能为空")
        # 使用原始长度而不是strip后的长度来检查
        if len(v) > 1000:
            raise ValueError("内容长度不能超过1000个字符")
        # 不使用strip()以保留换行符，只返回原始内容
        return v
    
    @field_validator('images')
    @classmethod
    def validate_images(cls, v):
        """验证图片列表"""
        if v is None:
            return v
        
        # 添加调试日志
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"🔍 验证图片列表: {v}")
        
        # 限制图片数量
        if len(v) > 9:
            raise ValueError("图片数量不能超过9张")
        
        # 检查路径格式（跳过URL的验证，因为它们会在async_smart_create中被处理）
        import os
        for image_path in v:
            # 如果是URL，跳过本地文件验证
            if isinstance(image_path, str) and image_path.startswith(('http://', 'https://')):
                logger.info(f"🌐 检测到URL图片，跳过本地验证: {image_path}")
                continue
            
            # 本地文件验证
            if not os.path.isabs(image_path):
                raise ValueError(f"图片路径必须是绝对路径: {image_path}")
            if not os.path.exists(image_path):
                raise ValueError(f"图片文件不存在: {image_path}")
            
            logger.info(f"✅ 本地图片验证通过: {image_path}")
        
        return v
    
    @field_validator('videos')
    @classmethod
    def validate_videos(cls, v):
        """验证视频列表"""
        if v is None:
            return v
        
        # 小红书只支持单个视频
        if len(v) > 1:
            raise ValueError("小红书只支持发布1个视频文件")
        
        # 检查路径格式和文件存在性
        import os
        from pathlib import Path
        
        validated_videos = []
        for video_path in v:
            # 尝试解析路径
            if os.path.exists(video_path):
                abs_path = os.path.abspath(video_path)
                validated_videos.append(abs_path)
            else:
                # 尝试从基础目录解析
                base_dir = Path(os.environ.get('MCP_WORKING_DIR', os.getcwd()))
                possible_paths = [
                    video_path,
                    base_dir / video_path,
                    Path.cwd() / video_path
                ]
                
                found = False
                for path in possible_paths:
                    if Path(path).exists():
                        validated_videos.append(str(Path(path).resolve()))
                        found = True
                        break
                
                if not found:
                    error_msg = f"未能找到视频文件: {video_path}\n"
                    error_msg += "请使用以下格式之一：\n"
                    error_msg += "1. 绝对路径: \"/Users/name/video.mp4\"\n"
                    error_msg += "2. 相对路径: \"./videos/video.mp4\"\n"
                    error_msg += "3. 文件名: \"video.mp4\" (当前目录)"
                    raise ValueError(error_msg)
            
            # 检查文件扩展名
            valid_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.m4v']
            _, ext = os.path.splitext(validated_videos[-1].lower())
            if ext not in valid_extensions:
                raise ValueError(f"不支持的视频格式: {ext}，支持的格式: {valid_extensions}")
        
        return validated_videos
    
    @field_validator('topics')
    @classmethod
    def validate_topics(cls, v):
        """验证话题列表"""
        if v is None:
            return v
            
        # 限制话题数量
        if len(v) > 10:
            raise ValueError("话题数量不能超过10个")
        
        # 检查话题长度
        for topic in v:
            if len(topic) > 20:
                raise ValueError(f"话题长度不能超过20个字符: {topic}")
        
        return v
    
    @field_validator('images', 'videos')
    @classmethod
    def validate_media_conflict(cls, v, info):
        """验证图片和视频不能同时存在"""
        # 在after模式下验证，确保能访问到其他字段
        return v
    
    def __init__(self, **data):
        """初始化时验证图片和视频冲突"""
        super().__init__(**data)
        
        # 检查图片和视频不能同时存在
        if self.images and self.videos:
            raise ValueError("不能同时上传图片和视频，请选择其中一种")
        
        # 至少需要图片或视频中的一种
        if not self.images and not self.videos:
            raise ValueError("必须上传至少1张图片或1个视频")
    
    @classmethod
    def from_strings(cls, title: str, content: str, topics_str: str = "", 
                    location: str = "", images_str: str = "", videos_str: str = "") -> 'XHSNote':
        """
        从字符串参数创建笔记对象
        
        Args:
            title: 笔记标题
            content: 笔记内容
            topics_str: 话题字符串（逗号分隔）
            location: 位置信息
            images_str: 图片路径字符串（支持多种格式：逗号分隔、数组字符串、JSON数组等）
            videos_str: 视频路径字符串（支持多种格式：逗号分隔、数组字符串、JSON数组等）
            
        Returns:
            XHSNote实例
        """
        topic_list = parse_topics_string(topics_str) if topics_str else None
        image_list = smart_parse_file_paths(images_str) if images_str else None
        video_list = smart_parse_file_paths(videos_str) if videos_str else None
        
        return cls(
            title=title,
            content=content,
            images=image_list,
            videos=video_list,
            topics=topic_list,
            location=location if location else None
        )

    @classmethod  
    def smart_create(cls, title: str, content: str, topics=None, 
                    location: str = "", images=None, videos=None) -> 'XHSNote':
        """
        智能创建笔记对象，支持多种输入格式
        
        Args:
            title: 笔记标题
            content: 笔记内容
            topics: 话题（支持字符串、列表等多种格式）
            location: 位置信息
            images: 图片路径（支持字符串、列表、JSON等多种格式）
            videos: 视频路径（支持字符串、列表、JSON等多种格式）
            
        Returns:
            XHSNote实例
        """
        # 智能解析话题
        if topics:
            if isinstance(topics, str):
                topic_list = parse_topics_string(topics)
            elif isinstance(topics, (list, tuple)):
                topic_list = [str(topic).strip() for topic in topics if str(topic).strip()]
            else:
                topic_list = parse_topics_string(str(topics))
        else:
            topic_list = None
        
        # 智能解析图片路径
        image_list = smart_parse_file_paths(images) if images else None
        
        # 智能解析视频路径  
        video_list = smart_parse_file_paths(videos) if videos else None
        
        return cls(
            title=title,
            content=content,
            images=image_list,
            videos=video_list,
            topics=topic_list,
            location=location if location else None
        )
    
    @classmethod
    async def async_smart_create(cls, title: str, content: str, topics=None,
                                location: str = "", images=None, videos=None) -> 'XHSNote':
        """
        异步智能创建笔记对象，支持多种输入格式（包括URL）
        
        Args:
            title: 笔记标题
            content: 笔记内容
            topics: 话题（支持字符串、列表等多种格式）
            location: 位置信息
            images: 图片，支持格式：
                   - 本地路径："image.jpg" 或 ["/path/to/image.jpg"]
                   - 网络地址："https://example.com/image.jpg"
                   - 混合数组：["local.jpg", "https://example.com/img.jpg"]
            videos: 视频路径（目前仅支持本地文件）
            
        Returns:
            XHSNote实例
        """
        logger.info(f"📝 异步创建笔记 - 标题: {title}")
        logger.info(f"📸 原始图片输入: {images}")
        logger.info(f"🎬 原始视频输入: {videos}")
        
        # 智能解析话题
        if topics:
            if isinstance(topics, str):
                topic_list = parse_topics_string(topics)
            elif isinstance(topics, (list, tuple)):
                topic_list = [str(topic).strip() for topic in topics if str(topic).strip()]
            else:
                topic_list = parse_topics_string(str(topics))
        else:
            topic_list = None
        
        logger.info(f"🏷️ 解析后的话题: {topic_list}")
        
        # 处理图片（支持URL和相对路径）
        processed_images = None
        if images:
            logger.info(f"🔄 开始处理图片...")
            from ..utils.image_processor import ImageProcessor
            # 传递基础目录用于解析相对路径
            import os
            base_dir = os.environ.get('MCP_WORKING_DIR', os.getcwd())
            processor = ImageProcessor(base_dir=base_dir)
            processed_images, error_msg = await processor.process_images(images)
            
            if error_msg and not processed_images:
                # 如果没有成功处理任何图片，抛出友好的错误信息
                raise ValueError(error_msg)
            
            logger.info(f"✅ 图片处理完成: {processed_images}")
        
        # 处理视频（支持相对路径）
        processed_videos = None
        if videos:
            logger.info(f"🎬 开始处理视频...")
            from ..utils.video_processor import VideoProcessor
            # 传递基础目录用于解析相对路径
            import os
            base_dir = os.environ.get('MCP_WORKING_DIR', os.getcwd())
            processor = VideoProcessor(base_dir=base_dir)
            processed_videos, error_msg = processor.process_videos(videos)
            
            if error_msg and not processed_videos:
                # 如果没有成功处理任何视频，抛出友好的错误信息
                raise ValueError(error_msg)
            
            logger.info(f"✅ 视频处理完成: {processed_videos}")
        else:
            processed_videos = None
        
        logger.info(f"🎥 最终视频列表: {processed_videos}")
        
        logger.info(f"🚀 创建XHSNote对象...")
        return cls(
            title=title,
            content=content,
            images=processed_images,
            videos=processed_videos,
            topics=topic_list,
            location=location if location else None
        )


class XHSSearchResult(BaseModel):
    """搜索结果数据模型"""
    
    note_id: str
    title: str
    author: str
    likes: int
    url: str
    thumbnail: Optional[str] = None
    
    @field_validator('note_id')
    @classmethod
    def validate_note_id(cls, v):
        """验证笔记ID"""
        if not v or not v.strip():
            raise ValueError("笔记ID不能为空")
        return v.strip()
    
    @field_validator('likes')
    @classmethod
    def validate_likes(cls, v):
        """验证点赞数"""
        if v < 0:
            raise ValueError("点赞数不能为负数")
        return v


class XHSUser(BaseModel):
    """小红书用户数据模型"""
    
    user_id: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    followers: Optional[int] = None
    following: Optional[int] = None
    notes_count: Optional[int] = None
    
    @field_validator('followers', 'following', 'notes_count')
    @classmethod
    def validate_counts(cls, v):
        """验证计数字段"""
        if v is not None and v < 0:
            raise ValueError("计数不能为负数")
        return v


class XHSPublishResult(BaseModel):
    """发布结果数据模型"""
    
    success: bool
    message: str
    note_title: Optional[str] = None
    final_url: Optional[str] = None
    error_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "success": self.success,
            "message": self.message,
            "note_title": self.note_title,
            "final_url": self.final_url,
            "error_type": self.error_type
        }


class CookieInfo(BaseModel):
    """Cookie信息数据模型"""
    
    name: str
    value: str
    domain: str
    path: str = "/"
    secure: bool = False
    expiry: Optional[int] = None
    
    @field_validator('name', 'value', 'domain')
    @classmethod
    def validate_required_fields(cls, v):
        """验证必需字段"""
        if not v or not v.strip():
            raise ValueError("Cookie的name、value、domain字段不能为空")
        return v.strip()


class CookiesData(BaseModel):
    """Cookies数据容器"""
    
    cookies: List[CookieInfo]
    saved_at: str
    domain: str = "creator.xiaohongshu.com"
    critical_cookies_found: List[str] = []
    version: str = "2.0"
    
    @field_validator('cookies')
    @classmethod
    def validate_cookies_list(cls, v):
        """验证cookies列表"""
        if not v:
            raise ValueError("cookies列表不能为空")
        return v
    
    def get_critical_cookies(self) -> List[str]:
        """获取关键cookies列表"""
        critical_names = [
            'web_session', 'a1', 'gid', 'webId', 
            'customer-sso-sid', 'x-user-id-creator.xiaohongshu.com',
            'access-token-creator.xiaohongshu.com', 'galaxy_creator_session_id',
            'galaxy.creator.beaker.session.id'
        ]
        
        found_critical = []
        for cookie in self.cookies:
            if cookie.name in critical_names:
                found_critical.append(cookie.name)
        
        return found_critical
    
    def is_valid(self) -> bool:
        """检查cookies是否有效"""
        critical_cookies = self.get_critical_cookies()
        # 至少需要前4个基础cookies中的3个
        required_basic = ['web_session', 'a1', 'gid', 'webId']
        found_basic = [name for name in critical_cookies if name in required_basic]
        
        return len(found_basic) >= 3


# 创作者中心关键cookies
CRITICAL_CREATOR_COOKIES = [
    'web_session', 'a1', 'gid', 'webId', 
    'customer-sso-sid', 'x-user-id-creator.xiaohongshu.com',
    'access-token-creator.xiaohongshu.com', 'galaxy_creator_session_id',
    'galaxy.creator.beaker.session.id'
] 