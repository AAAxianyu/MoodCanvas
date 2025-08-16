"""
API依赖注入管理
"""
from pathlib import Path
import os
from src.core.config_manager import ConfigManager
from src.services.emotion_analyzer import MultiModelEmotionAnalyzer
from src.services.emotion_analyzer import ImageEmotionAnalyzerService
def get_config_manager():
    """获取配置管理器实例"""
    # 使用更稳定的路径查找方式
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    config_path = project_root / "config" / "config.json"
    return ConfigManager(str(config_path))

def get_emotion_analyzer():
    """获取情感分析器实例"""
    config_manager = get_config_manager()
    return MultiModelEmotionAnalyzer(config_manager)

def get_image_emotion_analyzer():
    """获取图像情感分析器实例"""
    config_manager = get_config_manager()
    return ImageEmotionAnalyzerService(config_manager)
