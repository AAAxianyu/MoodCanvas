"""自定义异常类定义"""

class MoodCanvasError(Exception):
    """MoodCanvas基础异常类"""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

class EmotionAnalysisError(MoodCanvasError):
    """情感分析相关异常"""
    def __init__(self, message: str, error_code: str = "EMOTION_ANALYSIS_ERROR", details: dict = None):
        super().__init__(message, error_code, details)

class AudioProcessingError(MoodCanvasError):
    """音频处理相关异常"""
    def __init__(self, message: str, error_code: str = "AUDIO_PROCESSING_ERROR", details: dict = None):
        super().__init__(message, error_code, details)

class ImageProcessingError(MoodCanvasError):
    """图片处理相关异常"""
    def __init__(self, message: str, error_code: str = "IMAGE_PROCESSING_ERROR", details: dict = None):
        super().__init__(message, error_code, details)

class FileValidationError(MoodCanvasError):
    """文件验证相关异常"""
    def __init__(self, message: str, error_code: str = "FILE_VALIDATION_ERROR", details: dict = None):
        super().__init__(message, error_code, details)

class GenerationError(MoodCanvasError):
    """内容生成相关异常"""
    def __init__(self, message: str, error_code: str = "GENERATION_ERROR", details: dict = None):
        super().__init__(message, error_code, details)

class ModelLoadError(MoodCanvasError):
    """模型加载相关异常"""
    def __init__(self, message: str, error_code: str = "MODEL_LOAD_ERROR", details: dict = None):
        super().__init__(message, error_code, details)

class ConfigurationError(MoodCanvasError):
    """配置相关异常"""
    def __init__(self, message: str, error_code: str = "CONFIGURATION_ERROR", details: dict = None):
        super().__init__(message, error_code, details)

class ValidationError(MoodCanvasError):
    """数据验证相关异常"""
    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR", details: dict = None):
        super().__init__(message, error_code, details)

class ServiceUnavailableError(MoodCanvasError):
    """服务不可用异常"""
    def __init__(self, message: str, error_code: str = "SERVICE_UNAVAILABLE", details: dict = None):
        super().__init__(message, error_code, details)

class RateLimitError(MoodCanvasError):
    """速率限制异常"""
    def __init__(self, message: str, error_code: str = "RATE_LIMIT_ERROR", details: dict = None):
        super().__init__(message, error_code, details)
