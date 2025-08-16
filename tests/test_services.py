import pytest
from unittest.mock import patch
from src.core.exceptions import ModelNotReadyError, InvalidModelTypeError
from src.services.emotion_analyzer import EmotionAnalyzer
from src.services.image_service import ImageService

class TestEmotionAnalyzer:
    """测试情感分析服务"""
    
    def test_analyze_text(self, mock_emotion_model, mock_config_manager):
        """测试文本情感分析"""
        analyzer = EmotionAnalyzer(mock_config_manager)
        result = analyzer.analyze("测试文本", "text")
        
        assert isinstance(result, dict)
        assert "emotion" in result
        assert "score" in result
        mock_emotion_model.assert_called_once_with("测试文本")
    
    def test_analyze_audio(self, mock_asr_model, mock_emotion_model, mock_config_manager):
        """测试音频情感分析"""
        analyzer = EmotionAnalyzer(mock_config_manager)
        result = analyzer.analyze_audio(b"mock_audio_data")
        
        assert isinstance(result, dict)
        mock_asr_model.assert_called_once_with(b"mock_audio_data")
        mock_emotion_model.assert_called_once()
    
    def test_invalid_model_type(self, mock_config_manager):
        """测试无效模型类型"""
        analyzer = EmotionAnalyzer(mock_config_manager)
        with pytest.raises(InvalidModelTypeError):
            analyzer.analyze("测试文本", "invalid_type")
    
    def test_model_not_ready(self, mock_emotion_model, mock_config_manager):
        """测试模型未就绪情况"""
        mock_emotion_model.side_effect = ModelNotReadyError("模型加载中")
        analyzer = EmotionAnalyzer(mock_config_manager)
        
        with pytest.raises(ModelNotReadyError):
            analyzer.analyze("测试文本", "text")
    
    def test_config_reload(self, mock_config_manager):
        """测试配置重载"""
        analyzer = EmotionAnalyzer(mock_config_manager)
        initial_config = analyzer.config
        
        # 模拟配置变更
        new_config = {"models": {"emotion": {"type": "new_type"}}}
        mock_config_manager.get_config.return_value = new_config
        analyzer.reload_config()
        
        assert analyzer.config == new_config
        assert analyzer.config != initial_config

class TestImageService:
    """测试图像生成服务"""
    
    def test_generate_image(self, mock_image_model, mock_config_manager):
        """测试图像生成"""
        service = ImageService(mock_config_manager)
        result = service.generate_image("测试提示", 512, 512)
        
        assert isinstance(result, bytes)
        mock_image_model.assert_called_once_with(
            prompt="测试提示",
            width=512,
            height=512
        )
    
    def test_missing_api_key(self, mock_config_manager):
        """测试缺少API密钥"""
        mock_config_manager.get_config.return_value = {"stability": {"api_key": None}}
        service = ImageService(mock_config_manager)
        
        with pytest.raises(ValueError, match="API密钥未配置"):
            service.generate_image("测试", 512, 512)
    
    def test_invalid_dimensions(self, mock_config_manager):
        """测试无效图像尺寸"""
        service = ImageService(mock_config_manager)
        
        with pytest.raises(ValueError, match="无效的图像尺寸"):
            service.generate_image("测试", 10000, 512)
        
        with pytest.raises(ValueError, match="无效的图像尺寸"):
            service.generate_image("测试", 512, 10000)
    
    def test_config_reload(self, mock_config_manager):
        """测试配置重载"""
        service = ImageService(mock_config_manager)
        initial_config = service.config
        
        # 模拟配置变更
        new_config = {"stability": {"api_key": "new_key"}}
        mock_config_manager.get_config.return_value = new_config
        service.reload_config()
        
        assert service.config == new_config
        assert service.config != initial_config
