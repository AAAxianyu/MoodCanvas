"""
文件处理工具
"""
import os
import hashlib
from typing import Optional
import logging
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)

def validate_image_file(file_data: bytes) -> bool:
    """
    验证图片文件格式
    
    Args:
        file_data: 文件数据字节
        
    Returns:
        是否为有效的图片文件
    """
    try:
        # 检查文件头信息
        if len(file_data) < 8:
            return False
        
        # PNG文件头: 89 50 4E 47 0D 0A 1A 0A
        if file_data.startswith(b'\x89PNG\r\n\x1a\n'):
            return True
        
        # JPEG文件头: FF D8 FF
        if file_data.startswith(b'\xff\xd8\xff'):
            return True
        
        # WebP文件头: 52 49 46 46 ... 57 45 42 50
        if file_data.startswith(b'RIFF') and file_data[8:12] == b'WEBP':
            return True
        
        # GIF文件头: 47 49 46 38 37 61 或 47 49 46 38 39 61
        if file_data.startswith(b'GIF87a') or file_data.startswith(b'GIF89a'):
            return True
        
        logger.warning("不支持的图片格式")
        return False
        
    except Exception as e:
        logger.error(f"图片文件验证失败: {str(e)}")
        return False

def save_uploaded_file(file_data: bytes, file_path: str) -> bool:
    """
    保存上传的文件
    
    Args:
        file_data: 文件数据字节
        file_path: 保存路径
        
    Returns:
        是否保存成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 写入文件
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        logger.info(f"文件已保存到: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"保存文件失败: {str(e)}")
        return False

def get_file_hash(file_data: bytes) -> str:
    """
    计算文件的MD5哈希值
    
    Args:
        file_data: 文件数据字节
        
    Returns:
        MD5哈希字符串
    """
    try:
        return hashlib.md5(file_data).hexdigest()
    except Exception as e:
        logger.error(f"计算文件哈希失败: {str(e)}")
        return ""

def get_file_size_mb(file_data: bytes) -> float:
    """
    获取文件大小（MB）
    
    Args:
        file_data: 文件数据字节
        
    Returns:
        文件大小（MB）
    """
    try:
        return len(file_data) / (1024 * 1024)
    except Exception as e:
        logger.error(f"计算文件大小失败: {str(e)}")
        return 0.0

def cleanup_file(file_path: str) -> bool:
    """
    清理指定文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否清理成功
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"文件已删除: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"删除文件失败: {str(e)}")
        return False

def ensure_directory_exists(directory_path: str) -> bool:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory_path: 目录路径
        
    Returns:
        是否成功创建或已存在
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"创建目录失败: {str(e)}")
        return False

def get_file_extension(file_path: str) -> Optional[str]:
    """
    获取文件扩展名
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件扩展名（不含点号）
    """
    try:
        return os.path.splitext(file_path)[1][1:].lower()
    except Exception:
        return None

def is_valid_file_size(file_data: bytes, max_size_mb: float = 10.0) -> bool:
    """
    检查文件大小是否在允许范围内
    
    Args:
        file_data: 文件数据字节
        max_size_mb: 最大允许大小（MB）
        
    Returns:
        文件大小是否有效
    """
    try:
        file_size_mb = get_file_size_mb(file_data)
        return file_size_mb <= max_size_mb
    except Exception:
        return False

def save_upload_file(upload_file, temp_dir: Path, prefix: str = "upload") -> Path:
    """
    保存上传的文件到临时目录
    
    Args:
        upload_file: FastAPI的UploadFile对象
        temp_dir: 临时目录路径
        prefix: 文件名前缀
        
    Returns:
        保存后的文件路径
    """
    try:
        # 确保目录存在
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成唯一文件名
        import uuid
        file_extension = Path(upload_file.filename or "").suffix
        unique_filename = f"{prefix}_{uuid.uuid4().hex}{file_extension}"
        file_path = temp_dir / unique_filename
        
        # 保存文件
        with open(file_path, "wb") as f:
            shutil.copyfileobj(upload_file.file, f)
        
        logger.info(f"上传文件已保存到: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"保存上传文件失败: {str(e)}")
        raise
