"""
模型层测试
"""
import pytest
from unittest.mock import Mock, patch

# 导入模型
from src.models.emotion.text_emotion import TextEmotionModel
from src.models.emotion.audio_emotion import AudioEmotionModel
from src.models.asr.paraformer import ParaformerModel

class TestTextEmotionModel:
    """文本情感分析模型测试"""
    
    @pytest.fixture
    def config(self):
        return {
            "local_path": "src/data/models/distilbert-base-uncased-go-emotions-student",
            "use_local_models": True
        }
    
    @pytest.fixture
    def model(self, config):
        return TextEmotionModel(config)
    
    @patch('src.models.emotion.text_emotion.AutoTokenizer.from_pretrained')
    @patch('src.models.emotion.text_emotion.AutoModelForSequenceClassification.from_pretrained')
    @patch('src.models.emotion.text_emotion.pipeline')
    def test_load_model_local_success(self, mock_pipeline, mock_model, mock_tokenizer, model):
        """测试本地模型加载成功"""
        mock_tokenizer.return_value = Mock()
        mock_model.return_value = Mock()
        mock_pipeline.return_value = Mock()
        
        result = model.load_model()
        
        assert result == True
        assert model.is_loaded == True
        assert model.tokenizer is not None
        assert model.model is not None
        assert model.pipeline is not None
    
    def test_analyze_success(self, model):
        """测试情感分析成功"""
        model.is_loaded = True
        model.pipeline = Mock()
        model.pipeline.return_value = [
            {"label": "joy", "score": 0.85},
            {"label": "excitement", "score": 0.72}
        ]
        
        result = model.analyze("今天天气很好")
        
        assert len(result) == 2
        assert result[0]["label"] == "joy"
        assert result[0]["score"] == 0.85

class TestAudioEmotionModel:
    """音频情感分析模型测试"""
    
    @pytest.fixture
    def config(self):
        return {
            "local_path": "src/data/models/emotion2vec_plus_large",
            "use_local_models": True
        }
    
    @pytest.fixture
    def model(self, config):
        return AudioEmotionModel(config)
    
    @patch('src.models.emotion.audio_emotion.AutoModel')
    def test_load_model_local_success(self, mock_auto_model, model):
        """测试本地模型加载成功"""
        mock_model = Mock()
        mock_auto_model.return_value = mock_model
        
        result = model.load_model()
        
        assert result == True
        assert model.is_loaded == True
        assert model.model == mock_model
    
    def test_analyze_success(self, model):
        """测试音频情感分析成功"""
        model.is_loaded = True
        model.model = Mock()
        model.model.generate.return_value = {
            "emotion": 3,  # happy
            "confidence": 0.85
        }
        
        result = model.analyze("test.wav")
        
        assert len(result) == 1
        assert "raw_result" in result[0]
        assert result[0]["raw_result"]["emotion"] == 3

class TestParaformerModel:
    """Paraformer ASR模型测试"""
    
    @pytest.fixture
    def config(self):
        return {
            "local_path": "src/data/models/paraformer-zh",
            "use_local_models": True
        }
    
    @pytest.fixture
    def model(self, config):
        return ParaformerModel(config)
    
    @patch('src.models.asr.paraformer.AutoModel')
    def test_load_model_local_success(self, mock_auto_model, model):
        """测试本地模型加载成功"""
        mock_model = Mock()
        mock_auto_model.return_value = mock_model
        
        result = model.load_model()
        
        assert result == True
        assert model.is_loaded == True
        assert model.model == mock_model
    
    def test_transcribe_success(self, model):
        """测试语音识别成功"""
        model.is_loaded = True
        model.model = Mock()
        model.model.generate.return_value = {
            "text": "今天天气很好",
            "confidence": 0.95
        }
        
        result = model.transcribe("test.wav")
        
        assert result == "今天天气很好"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
