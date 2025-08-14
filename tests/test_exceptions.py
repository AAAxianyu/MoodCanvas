"""
异常处理测试
"""
import pytest
from src.core.exceptions import (
    MoodCanvasError, EmotionAnalysisError, AudioProcessingError,
    ImageProcessingError, FileValidationError, GenerationError,
    ValidationError, ServiceUnavailableError, RateLimitError
)

class TestMoodCanvasError:
    """基础异常测试"""
    
    def test_basic_error(self):
        """测试基础异常"""
        error = MoodCanvasError("测试错误")
        
        assert str(error) == "测试错误"
        assert error.message == "测试错误"
        assert error.error_code is None
        assert error.details == {}
    
    def test_error_with_code(self):
        """测试带错误代码的异常"""
        error = MoodCanvasError("测试错误", "TEST_ERROR")
        
        assert error.message == "测试错误"
        assert error.error_code == "TEST_ERROR"
        assert error.details == {}
    
    def test_error_with_details(self):
        """测试带详细信息的异常"""
        details = {"field": "value", "line": 42}
        error = MoodCanvasError("测试错误", "TEST_ERROR", details)
        
        assert error.message == "测试错误"
        assert error.error_code == "TEST_ERROR"
        assert error.details == details
    
    def test_error_inheritance(self):
        """测试异常继承关系"""
        error = MoodCanvasError("测试错误")
        
        assert isinstance(error, Exception)
        assert isinstance(error, MoodCanvasError)

class TestEmotionAnalysisError:
    """情感分析异常测试"""
    
    def test_emotion_analysis_error(self):
        """测试情感分析异常"""
        error = EmotionAnalysisError("情感分析失败")
        
        assert error.message == "情感分析失败"
        assert error.error_code == "EMOTION_ANALYSIS_ERROR"
        assert error.details == {}
    
    def test_emotion_analysis_error_with_details(self):
        """测试带详细信息的情感分析异常"""
        details = {"model": "emotion2vec", "input": "test.wav"}
        error = EmotionAnalysisError("情感分析失败", details=details)
        
        assert error.message == "情感分析失败"
        assert error.error_code == "EMOTION_ANALYSIS_ERROR"
        assert error.details == details
    
    def test_emotion_analysis_error_inheritance(self):
        """测试情感分析异常继承关系"""
        error = EmotionAnalysisError("测试错误")
        
        assert isinstance(error, MoodCanvasError)
        assert isinstance(error, EmotionAnalysisError)

class TestAudioProcessingError:
    """音频处理异常测试"""
    
    def test_audio_processing_error(self):
        """测试音频处理异常"""
        error = AudioProcessingError("音频处理失败")
        
        assert error.message == "音频处理失败"
        assert error.error_code == "AUDIO_PROCESSING_ERROR"
        assert error.details == {}
    
    def test_audio_processing_error_with_details(self):
        """测试带详细信息的音频处理异常"""
        details = {"file_format": "wav", "duration": 10.5}
        error = AudioProcessingError("音频处理失败", details=details)
        
        assert error.message == "音频处理失败"
        assert error.error_code == "AUDIO_PROCESSING_ERROR"
        assert error.details == details
    
    def test_audio_processing_error_inheritance(self):
        """测试音频处理异常继承关系"""
        error = AudioProcessingError("测试错误")
        
        assert isinstance(error, MoodCanvasError)
        assert isinstance(error, AudioProcessingError)

class TestImageProcessingError:
    """图片处理异常测试"""
    
    def test_image_processing_error(self):
        """测试图片处理异常"""
        error = ImageProcessingError("图片处理失败")
        
        assert error.message == "图片处理失败"
        assert error.error_code == "IMAGE_PROCESSING_ERROR"
        assert error.details == {}
    
    def test_image_processing_error_with_details(self):
        """测试带详细信息的图片处理异常"""
        details = {"format": "png", "size": "1024x1024"}
        error = ImageProcessingError("图片处理失败", details=details)
        
        assert error.message == "图片处理失败"
        assert error.error_code == "IMAGE_PROCESSING_ERROR"
        assert error.details == details
    
    def test_image_processing_error_inheritance(self):
        """测试图片处理异常继承关系"""
        error = ImageProcessingError("测试错误")
        
        assert isinstance(error, MoodCanvasError)
        assert isinstance(error, ImageProcessingError)

class TestFileValidationError:
    """文件验证异常测试"""
    
    def test_file_validation_error(self):
        """测试文件验证异常"""
        error = FileValidationError("文件格式无效")
        
        assert error.message == "文件格式无效"
        assert error.error_code == "FILE_VALIDATION_ERROR"
        assert error.details == {}
    
    def test_file_validation_error_with_details(self):
        """测试带详细信息的文件验证异常"""
        details = {"file_type": "audio", "max_size": "50MB"}
        error = FileValidationError("文件格式无效", details=details)
        
        assert error.message == "文件格式无效"
        assert error.error_code == "FILE_VALIDATION_ERROR"
        assert error.details == details
    
    def test_file_validation_error_inheritance(self):
        """测试文件验证异常继承关系"""
        error = FileValidationError("测试错误")
        
        assert isinstance(error, MoodCanvasError)
        assert isinstance(error, FileValidationError)

class TestGenerationError:
    """生成异常测试"""
    
    def test_generation_error(self):
        """测试生成异常"""
        error = GenerationError("内容生成失败")
        
        assert error.message == "内容生成失败"
        assert error.error_code == "GENERATION_ERROR"
        assert error.details == {}
    
    def test_generation_error_with_details(self):
        """测试带详细信息的生成异常"""
        details = {"model": "doubao", "prompt": "测试提示词"}
        error = GenerationError("内容生成失败", details=details)
        
        assert error.message == "内容生成失败"
        assert error.error_code == "GENERATION_ERROR"
        assert error.details == details
    
    def test_generation_error_inheritance(self):
        """测试生成异常继承关系"""
        error = GenerationError("测试错误")
        
        assert isinstance(error, MoodCanvasError)
        assert isinstance(error, GenerationError)

class TestValidationError:
    """验证异常测试"""
    
    def test_validation_error(self):
        """测试验证异常"""
        error = ValidationError("输入验证失败")
        
        assert error.message == "输入验证失败"
        assert error.error_code == "VALIDATION_ERROR"
        assert error.details == {}
    
    def test_validation_error_with_details(self):
        """测试带详细信息的验证异常"""
        details = {"field": "text", "constraint": "min_length=1"}
        error = ValidationError("输入验证失败", details=details)
        
        assert error.message == "输入验证失败"
        assert error.error_code == "VALIDATION_ERROR"
        assert error.details == details
    
    def test_validation_error_inheritance(self):
        """测试验证异常继承关系"""
        error = ValidationError("测试错误")
        
        assert isinstance(error, MoodCanvasError)
        assert isinstance(error, ValidationError)

class TestServiceUnavailableError:
    """服务不可用异常测试"""
    
    def test_service_unavailable_error(self):
        """测试服务不可用异常"""
        error = ServiceUnavailableError("服务暂时不可用")
        
        assert error.message == "服务暂时不可用"
        assert error.error_code == "SERVICE_UNAVAILABLE_ERROR"
        assert error.details == {}
    
    def test_service_unavailable_error_with_details(self):
        """测试带详细信息的服务不可用异常"""
        details = {"service": "doubao", "retry_after": 300}
        error = ServiceUnavailableError("服务暂时不可用", details=details)
        
        assert error.message == "服务暂时不可用"
        assert error.error_code == "SERVICE_UNAVAILABLE_ERROR"
        assert error.details == details
    
    def test_service_unavailable_error_inheritance(self):
        """测试服务不可用异常继承关系"""
        error = ServiceUnavailableError("测试错误")
        
        assert isinstance(error, MoodCanvasError)
        assert isinstance(error, ServiceUnavailableError)

class TestRateLimitError:
    """速率限制异常测试"""
    
    def test_rate_limit_error(self):
        """测试速率限制异常"""
        error = RateLimitError("请求过于频繁")
        
        assert error.message == "请求过于频繁"
        assert error.error_code == "RATE_LIMIT_ERROR"
        assert error.details == {}
    
    def test_rate_limit_error_with_details(self):
        """测试带详细信息的速率限制异常"""
        details = {"limit": 100, "reset_time": "2024-01-01T00:00:00Z"}
        error = RateLimitError("请求过于频繁", details=details)
        
        assert error.message == "请求过于频繁"
        assert error.error_code == "RATE_LIMIT_ERROR"
        assert error.details == details
    
    def test_rate_limit_error_inheritance(self):
        """测试速率限制异常继承关系"""
        error = RateLimitError("测试错误")
        
        assert isinstance(error, MoodCanvasError)
        assert isinstance(error, RateLimitError)

class TestExceptionUsage:
    """异常使用场景测试"""
    
    def test_exception_chaining(self):
        """测试异常链式调用"""
        try:
            raise EmotionAnalysisError("情感分析失败", details={"model": "emotion2vec"})
        except EmotionAnalysisError as e:
            assert e.message == "情感分析失败"
            assert e.error_code == "EMOTION_ANALYSIS_ERROR"
            assert e.details["model"] == "emotion2vec"
    
    def test_exception_re_raising(self):
        """测试异常重新抛出"""
        try:
            try:
                raise ValueError("原始错误")
            except ValueError as e:
                raise EmotionAnalysisError("包装后的错误", details={"original_error": str(e)})
        except EmotionAnalysisError as e:
            assert e.message == "包装后的错误"
            assert "原始错误" in e.details["original_error"]
    
    def test_exception_comparison(self):
        """测试异常比较"""
        error1 = EmotionAnalysisError("错误1")
        error2 = EmotionAnalysisError("错误2")
        
        assert error1 != error2
        assert error1.message != error2.message
        assert error1.error_code == error2.error_code
    
    def test_exception_str_representation(self):
        """测试异常字符串表示"""
        error = MoodCanvasError("测试错误", "TEST_CODE", {"key": "value"})
        
        str_repr = str(error)
        assert "测试错误" in str_repr
        assert "TEST_CODE" in str_repr
        assert "key" in str_repr
        assert "value" in str_repr

if __name__ == "__main__":
    pytest.main([__file__, "-v"])



