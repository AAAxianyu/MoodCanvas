"""
配置管理设置
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional

class Settings:
    """应用配置设置"""
    
    # 项目基本信息
    PROJECT_NAME: str = "MoodCanvas"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = "三阶段多模型情感分析系统"
    
    # 服务器配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # 环境变量
    ARK_API_KEY: Optional[str] = os.getenv("ARK_API_KEY")
    
    # 路径配置
    BASE_DIR: Path = Path(__file__).parent.parent
    CONFIG_DIR: Path = BASE_DIR / "config"
    DATA_DIR: Path = BASE_DIR / "data"
    MODELS_DIR: Path = DATA_DIR / "models"
    INPUT_DIR: Path = DATA_DIR / "input"
    OUTPUT_DIR: Path = DATA_DIR / "output"
    TEMP_DIR: Path = DATA_DIR / "temp"
    GENERATED_IMAGES_DIR: Path = DATA_DIR / "generated_images"
    
    # 模型配置
    USE_LOCAL_MODELS: bool = os.getenv("USE_LOCAL_MODELS", "true").lower() == "true"
    DOWNLOAD_TO_PROJECT: bool = os.getenv("DOWNLOAD_TO_PROJECT", "true").lower() == "true"
    CACHE_MODELS: bool = os.getenv("CACHE_MODELS", "true").lower() == "true"
    
    # 音频处理配置
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "1"))
    GRANULARITY: str = os.getenv("GRANULARITY", "utterance")
    EXTRACT_EMBEDDING: bool = os.getenv("EXTRACT_EMBEDDING", "false").lower() == "true"
    
    # 输出格式配置
    INCLUDE_TIMESTAMP: bool = os.getenv("INCLUDE_TIMESTAMP", "true").lower() == "true"
    INCLUDE_RAW_DATA: bool = os.getenv("INCLUDE_RAW_DATA", "true").lower() == "true"
    SORT_BY_CONFIDENCE: bool = os.getenv("SORT_BY_CONFIDENCE", "true").lower() == "true"
    MAX_EMOTIONS_DISPLAY: int = int(os.getenv("MAX_EMOTIONS_DISPLAY", "10"))
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    @classmethod
    def get_model_path(cls, model_name: str) -> Path:
        """获取模型路径"""
        return cls.MODELS_DIR / model_name
    
    @classmethod
    def ensure_directories(cls) -> None:
        """确保必要的目录存在"""
        directories = [
            cls.DATA_DIR,
            cls.MODELS_DIR,
            cls.INPUT_DIR,
            cls.OUTPUT_DIR,
            cls.TEMP_DIR,
            cls.GENERATED_IMAGES_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """验证配置有效性"""
        errors = []
        warnings = []
        
        # 检查环境变量
        if not cls.ARK_API_KEY:
            warnings.append("ARK_API_KEY 环境变量未设置")
        
        # 检查目录权限
        try:
            cls.ensure_directories()
        except Exception as e:
            errors.append(f"无法创建数据目录: {e}")
        
        # 检查模型目录
        if cls.USE_LOCAL_MODELS:
            if not cls.MODELS_DIR.exists():
                warnings.append("本地模型目录不存在，将使用在线模型")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

# 全局设置实例
settings = Settings()
