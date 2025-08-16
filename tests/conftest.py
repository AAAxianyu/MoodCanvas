import pytest
from unittest.mock import MagicMock, patch
import os
from fastapi.testclient import TestClient
from src.main import app
from src.core.config_manager import ConfigManager

@pytest.fixture
def mock_env_vars():
    """Mock环境变量"""
    with patch.dict(os.environ, {
        "OPENAI_API_KEY": "mock_key",
        "STABILITY_API_KEY": "mock_key",
        "MODEL_CACHE_DIR": "./data/models",
        "LOG_LEVEL": "DEBUG"
    }):
        yield

@pytest.fixture
def mock_config_manager(mock_env_vars):
    """Mock配置管理器"""
    with patch.object(ConfigManager, 'load_config', return_value={
        "openai": {"api_key": "mock_key"},
        "stability": {"api_key": "mock_key"},
        "models": {
            "asr": {"type": "paraformer"},
            "emotion": {"type": "text"},
            "image": {"type": "stability"}
        }
    }):
        yield ConfigManager()

@pytest.fixture
def test_client():
    """FastAPI测试客户端"""
    return TestClient(app)

@pytest.fixture
def mock_openai():
    """Mock OpenAI API"""
    with patch("openai.ChatCompletion.create") as mock:
        mock.return_value = {
            "choices": [{
                "message": {
                    "content": "测试响应内容"
                }
            }]
        }
        yield mock

@pytest.fixture
def mock_stability():
    """Mock Stability API"""
    with patch("stability_sdk.client.StabilityInference.generate") as mock:
        mock.return_value = [MagicMock()]
        yield mock

@pytest.fixture
def mock_asr_model():
    """Mock ASR模型"""
    with patch("src.models.asr.paraformer.ParaformerASR.transcribe") as mock:
        mock.return_value = "测试转录文本"
        yield mock

@pytest.fixture
def mock_emotion_model():
    """Mock情感分析模型"""
    with patch("src.models.emotion.text_emotion.TextEmotion.analyze") as mock:
        mock.return_value = {"emotion": "happy", "score": 0.9}
        yield mock

@pytest.fixture
def mock_image_model():
    """Mock图像生成模型"""
    with patch("src.models.image.text2image.Text2Image.generate") as mock:
        mock.return_value = b"mock_image_data"
        yield mock
