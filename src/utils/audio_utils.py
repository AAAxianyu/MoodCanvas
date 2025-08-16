"""
音频处理工具
"""
import os
import wave
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import logging
from typing import Optional, Tuple
import wave
import io

logger = logging.getLogger(__name__)

def get_audio_info(audio_path: str) -> Dict[str, Any]:
    """获取音频文件信息"""
    try:
        with wave.open(audio_path, 'rb') as wav_file:
            info = {
                'channels': wav_file.getnchannels(),
                'sample_width': wav_file.getsampwidth(),
                'frame_rate': wav_file.getframerate(),
                'frames': wav_file.getnframes(),
                'duration': wav_file.getnframes() / wav_file.getframerate()
            }
            return info
    except Exception as e:
        return {'error': str(e)}

def validate_audio_file(file_data: bytes) -> bool:
    """
    验证音频文件格式
    
    Args:
        file_data: 文件数据字节
        
    Returns:
        是否为有效的音频文件
    """
    try:
        # 检查文件头信息
        if len(file_data) < 12:
            return False
        
        # WAV文件头: 52 49 46 46 (RIFF)
        if file_data.startswith(b'RIFF'):
            return True
        
        # MP3文件头: FF FB 或 FF F3 或 FF F2
        if file_data.startswith(b'\xff\xfb') or file_data.startswith(b'\xff\xf3') or file_data.startswith(b'\xff\xf2'):
            return True
        
        # M4A文件头: 00 00 00 20 66 74 79 70 4D 34 41
        if file_data.startswith(b'\x00\x00\x00\x20ftypM4A'):
            return True
        
        # FLAC文件头: 66 4C 61 43 (fLaC)
        if file_data.startswith(b'fLaC'):
            return True
        
        logger.warning("不支持的音频格式")
        return False
        
    except Exception as e:
        logger.error(f"音频文件验证失败: {str(e)}")
        return False

def get_audio_info(file_data: bytes) -> Optional[dict]:
    """
    获取音频文件基本信息
    
    Args:
        file_data: 音频文件数据
        
    Returns:
        音频信息字典
    """
    try:
        # 尝试作为WAV文件读取
        if file_data.startswith(b'RIFF'):
            with io.BytesIO(file_data) as audio_io:
                with wave.open(audio_io, 'rb') as wav_file:
                    return {
                        'format': 'WAV',
                        'channels': wav_file.getnchannels(),
                        'sample_width': wav_file.getsampwidth(),
                        'frame_rate': wav_file.getframerate(),
                        'frames': wav_file.getnframes(),
                        'duration': wav_file.getnframes() / wav_file.getframerate()
                    }
        
        # 其他格式暂时返回基本信息
        return {
            'format': 'Unknown',
            'size_bytes': len(file_data),
            'size_mb': len(file_data) / (1024 * 1024)
        }
        
    except Exception as e:
        logger.error(f"获取音频信息失败: {str(e)}")
        return None

def is_valid_audio_size(file_data: bytes, max_size_mb: float = 50.0) -> bool:
    """
    检查音频文件大小是否在允许范围内
    
    Args:
        file_data: 音频文件数据
        max_size_mb: 最大允许大小（MB）
        
    Returns:
        文件大小是否有效
    """
    try:
        file_size_mb = len(file_data) / (1024 * 1024)
        return file_size_mb <= max_size_mb
    except Exception:
        return False

def get_audio_duration_estimate(file_data: bytes) -> Optional[float]:
    """
    估算音频文件时长（秒）
    
    Args:
        file_data: 音频文件数据
        
    Returns:
        估算的时长（秒）
    """
    try:
        # 基于文件大小和常见比特率估算
        file_size_mb = len(file_data) / (1024 * 1024)
        
        # 常见音频比特率（kbps）
        bitrates = {
            'wav': 1411,    # CD质量
            'mp3': 128,     # 标准MP3
            'm4a': 256,     # AAC
            'flac': 1000    # 无损压缩
        }
        
        # 根据文件头判断格式
        if file_data.startswith(b'RIFF'):
            format_type = 'wav'
        elif file_data.startswith(b'\xff'):
            format_type = 'mp3'
        elif file_data.startswith(b'\x00\x00\x00\x20ftypM4A'):
            format_type = 'm4a'
        elif file_data.startswith(b'fLaC'):
            format_type = 'flac'
        else:
            format_type = 'mp3'  # 默认假设
        
        # 计算时长：文件大小(MB) * 8 * 1024 / 比特率(kbps) / 1000
        bitrate = bitrates.get(format_type, 128)
        duration = (file_size_mb * 8 * 1024) / (bitrate * 1000)
        
        return max(0.1, duration)  # 最小0.1秒
        
    except Exception as e:
        logger.error(f"估算音频时长失败: {str(e)}")
        return None

def validate_wav_format(file_data: bytes) -> Tuple[bool, Optional[str]]:
    """
    专门验证WAV格式文件
    
    Args:
        file_data: 文件数据字节
        
    Returns:
        (是否有效, 错误信息)
    """
    try:
        if not file_data.startswith(b'RIFF'):
            return False, "不是有效的WAV文件格式"
        
        if len(file_data) < 44:  # WAV文件头至少44字节
            return False, "WAV文件头不完整"
        
        # 检查文件大小是否与RIFF头中的大小一致
        riff_size = int.from_bytes(file_data[4:8], 'little')
        if riff_size + 8 != len(file_data):
            return False, "WAV文件大小与头信息不匹配"
        
        # 检查WAVE标识
        if file_data[8:12] != b'WAVE':
            return False, "WAV文件格式标识错误"
        
        return True, None
        
    except Exception as e:
        return False, f"WAV文件验证异常: {str(e)}"

def get_audio_metadata(file_data: bytes) -> dict:
    """
    获取音频文件元数据
    
    Args:
        file_data: 音频文件数据
        
    Returns:
        元数据字典
    """
    try:
        metadata = {
            'file_size_bytes': len(file_data),
            'file_size_mb': round(len(file_data) / (1024 * 1024), 2),
            'format': 'Unknown',
            'valid': False
        }
        
        # 判断格式
        if file_data.startswith(b'RIFF'):
            metadata['format'] = 'WAV'
        elif file_data.startswith(b'\xff'):
            metadata['format'] = 'MP3'
        elif file_data.startswith(b'\x00\x00\x00\x20ftypM4A'):
            metadata['format'] = 'M4A'
        elif file_data.startswith(b'fLaC'):
            metadata['format'] = 'FLAC'
        
        # 验证文件
        if metadata['format'] == 'WAV':
            is_valid, error_msg = validate_wav_format(file_data)
            metadata['valid'] = is_valid
            if not is_valid:
                metadata['error'] = error_msg
        else:
            metadata['valid'] = validate_audio_file(file_data)
        
        # 获取时长估算
        duration = get_audio_duration_estimate(file_data)
        if duration:
            metadata['estimated_duration_seconds'] = round(duration, 2)
        
        return metadata
        
    except Exception as e:
        logger.error(f"获取音频元数据失败: {str(e)}")
        return {
            'file_size_bytes': len(file_data),
            'file_size_mb': round(len(file_data) / (1024 * 1024), 2),
            'format': 'Unknown',
            'valid': False,
            'error': str(e)
        }

def convert_audio_format(input_path: str, output_path: str, target_format: str = 'wav') -> bool:
    """转换音频格式（需要ffmpeg）"""
    try:
        import subprocess
        
        # 构建ffmpeg命令
        cmd = [
            'ffmpeg', '-i', input_path,
            '-y',  # 覆盖输出文件
            output_path
        ]
        
        # 执行转换
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
        else:
            print(f"音频转换失败: {result.stderr}")
            return False
            
    except ImportError:
        print("ffmpeg未安装，无法转换音频格式")
        return False
    except Exception as e:
        print(f"音频转换异常: {e}")
        return False

def normalize_audio_path(audio_path: str, base_dir: str = "data/temp") -> str:
    """标准化音频文件路径"""
    path = Path(audio_path)
    
    # 如果是相对路径，转换为绝对路径
    if not path.is_absolute():
        path = Path(base_dir) / path.name
    
    # 确保目录存在
    path.parent.mkdir(parents=True, exist_ok=True)
    
    return str(path)

def cleanup_temp_audio(temp_dir: str, max_age_hours: int = 24) -> int:
    """清理临时音频文件"""
    import time
    from datetime import datetime, timedelta
    
    temp_path = Path(temp_dir)
    if not temp_path.exists():
        return 0
    
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    cleaned_count = 0
    
    for audio_file in temp_path.glob("*.wav"):
        try:
            file_time = datetime.fromtimestamp(audio_file.stat().st_mtime)
            if file_time < cutoff_time:
                audio_file.unlink()
                cleaned_count += 1
        except Exception as e:
            print(f"清理文件失败 {audio_file}: {e}")
    
    return cleaned_count
