import pytest
from unittest.mock import patch, MagicMock
from src.core.exceptions import ModelNotReadyError
from src.models.asr.paraformer import ParaformerASR
from src.models.emotion.text_emotion import TextEmotion
from src.models.emotion.audio_emotion import AudioEmotion
from src.models.image.text2image import Text2Image

class TestParaformerASR:
    """测试语音识别模型"""
    
    def test_init(self, mock_config_manager):
        """测试模型初始化"""
        model = ParaformerASR(mock_config_manager)
        assert model.model_type == "paraformer"
        assert model.config == mock_config_manager.get_config()
    
    @patch("src.models.asr.paraformer.Paraformer")
    def test_load_model(self, mock_paraformer, mock_config_manager):
        """测试模型加载"""
        mock_paraformer.return_value = MagicMock()
        model = ParaformerASR(mock_config_manager)
        model.load_model()
        
        assert model.model is not None
        mock_paraformer.assert_called_once()
    
    def test_transcribe(self, mock_config_manager):
        """测试语音转录"""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = "测试转录结果"
        
        model = ParaformerASR(mock_config_manager)
        model.model = mock_model
        result = model.transcribe(b"audio_data")
        
        assert result == "测试转录结果"
        mock_model.transcribe.assert_called_once_with(b"audio_data")
    
    def test_not_ready(self, mock_config_manager):
        """测试模型未就绪情况"""
        model = ParaformerASR(mock_config_manager)
        with pytest.raises(ModelNotReadyError):
            model.transcribe(b"audio_data")

class TestTextEmotion:
    """测试文本情感分析模型"""
    
    def test_init(self, mock_config_manager):
        """测试模型初始化"""
        model = TextEmotion(mock_config_manager)
        assert model.model_type == "text"
        assert model.config == mock_config_manager.get_config()
    
    @patch("transformers.pipeline")
    def test_load_model(self, mock_pipeline, mock_config_manager):
        """测试模型加载"""
        mock_pipeline.return_value = MagicMock()
        model = TextEmotion(mock_config_manager)
        model.load_model()
        
        assert model.pipeline is not None
        mock_pipeline.assert_called_once()
    
    def test_analyze(self, mock_config_manager):
        """测试情感分析"""
        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [{"label": "happy", "score": 0.9}]
        
        model = TextEmotion(mock_config_manager)
        model.pipeline = mock_pipeline
        result = model.analyze("测试文本")
        
        assert "emotion" in result
        assert "score" in result
        mock_pipeline.assert_called_once_with("测试文本")
    
    def test_not_ready(self, mock_config_manager):
        """测试模型未就绪情况"""
        model = TextEmotion(mock_config_manager)
        with pytest.raises(ModelNotReadyError):
            model.analyze("测试文本")

class TestText2Image:
    """测试文本到图像生成模型"""
    
    def test_init(self, mock_config_manager):
        """测试模型初始化"""
        model = Text2Image(mock_config_manager)
        assert model.model_type == "stability"
        assert model.config == mock_config_manager.get_config()
    
    @patch("stability_sdk.client.StabilityInference")
    def test_load_model(self, mock_stability, mock_config_manager):
        """测试模型加载"""
        mock_stability.return_value = MagicMock()
        model = Text2Image(mock_config_manager)
        model.load_model()
        
        assert model.client is not None
        mock_stability.assert_called_once()
    
    def test_generate(self, mock_config_manager):
        """测试图像生成"""
        mock_client = MagicMock()
        mock_client.generate.return_value = [MagicMock(artifacts=[MagicMock(binary=b"image_data")])]
        
        model = Text2Image(mock_config_manager)
        model.client = mock_client
        result = model.generate("测试提示", 512, 512)
        
        assert isinstance(result, bytes)
        mock_client.generate.assert_called_once()
    
    def test_not_ready(self, mock_config_manager):
        """测试模型未就绪情况"""
        model = Text2Image(mock_config_manager)
        with pytest.raises(ModelNotReadyError):
            model.generate("测试", 512, 512)
    
    def test_invalid_dimensions(self, mock_config_manager):
        """测试无效图像尺寸"""
        model = Text2Image(mock_config_manager)
        model.client = MagicMock()
        
        with pytest.raises(ValueError, match="宽度必须在"):
            model.generate("测试", 10000, 512)
        
        with pytest.raises(ValueError, match="高度必须在"):
            model.generate("测试", 512, 10000)
