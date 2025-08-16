import pytest
from fastapi import status
from src.core.exceptions import ModelNotReadyError

class TestHealthAPI:
    """测试健康检查API"""
    
    def test_health_check(self, test_client):
        """测试健康检查端点"""
        response = test_client.get("/v1/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}

class TestEmotionAPI:
    """测试情感分析API"""
    
    def test_analyze_text_emotion(self, test_client, mock_emotion_model):
        """测试文本情感分析"""
        payload = {"text": "今天天气真好"}
        response = test_client.post("/v1/emotion/analyze_text", json=payload)
        
        assert response.status_code == status.HTTP_200_OK
        assert "emotion" in response.json()
        assert "score" in response.json()
        mock_emotion_model.assert_called_once_with(payload["text"])
    
    def test_analyze_audio_emotion(self, test_client, mock_asr_model, mock_emotion_model):
        """测试音频情感分析"""
        test_file = {"file": ("test.wav", b"mock_audio_data", "audio/wav")}
        response = test_client.post("/v1/emotion/analyze_audio", files=test_file)
        
        assert response.status_code == status.HTTP_200_OK
        mock_asr_model.assert_called_once()
        mock_emotion_model.assert_called_once()
    
    def test_invalid_model_type(self, test_client):
        """测试无效模型类型"""
        payload = {"text": "测试", "model_type": "invalid"}
        response = test_client.post("/v1/emotion/analyze", json=payload)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.json()
    
    def test_model_not_ready(self, test_client, mock_emotion_model):
        """测试模型未就绪情况"""
        mock_emotion_model.side_effect = ModelNotReadyError("模型加载中")
        payload = {"text": "测试", "model_type": "text"}
        response = test_client.post("/v1/emotion/analyze", json=payload)
        
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "detail" in response.json()

class TestImageAPI:
    """测试图像生成API"""
    
    def test_generate_image(self, test_client, mock_image_model):
        """测试图像生成"""
        payload = {"prompt": "一只猫", "width": 512, "height": 512}
        response = test_client.post("/v1/image/generate", json=payload)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "image/png"
        mock_image_model.assert_called_once_with(
            prompt=payload["prompt"],
            width=payload["width"],
            height=payload["height"]
        )
    
    def test_invalid_dimensions(self, test_client):
        """测试无效图像尺寸"""
        payload = {"prompt": "测试", "width": 10000, "height": 512}
        response = test_client.post("/v1/image/generate", json=payload)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.json()
    
    def test_missing_api_key(self, test_client, mock_config_manager):
        """测试缺少API密钥情况"""
        mock_config_manager.get_config.return_value = {"stability": {"api_key": None}}
        payload = {"prompt": "测试", "width": 512, "height": 512}
        response = test_client.post("/v1/image/generate", json=payload)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "detail" in response.json()
