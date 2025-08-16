"""
API层测试
"""
import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# 导入FastAPI应用
from src.main import app

class TestEmotionAPI:
    """情感分析API测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_emotion_service(self):
        """模拟情感分析服务"""
        mock_service = Mock()
        mock_service.run_three_stage_analysis.return_value = {
            "transcribed_text": "识别的文字",
            "emotion_analysis": {
                "audio_emotion": ["happy"],
                "text_emotion": ["joy"],
                "merged_emotion": ["happy", "joy"],
                "fusion_strategy": "weighted"
            },
            "generated_content": {
                "image_path": "data/generated_images/test.png",
                "style": "default",
                "metadata": {
                    "generation_timestamp": "2024-01-01T00:00:00Z"
                }
            },
            "processing_time": 2.1,
            "status": "success"
        }
        
        return mock_service
    
    def test_analyze_emotion_endpoint_success(self, client, mock_emotion_service):
        """测试情感分析接口成功场景"""
        with patch('src.api.v1.emotion.MultiModelEmotionAnalyzer', return_value=mock_emotion_service):
            # 创建模拟的音频文件
            audio_data = b"fake_audio_data"
            
            response = client.post(
                "/api/v1/emotion/analyze",
                files={"audio_file": ("test.wav", audio_data, "audio/wav")}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'success'
            assert data['transcribed_text'] == "识别的文字"
            assert 'emotion_analysis' in data
            assert 'generated_content' in data
    
    def test_analyze_emotion_endpoint_missing_file(self, client):
        """测试情感分析接口缺少文件"""
        response = client.post("/api/v1/emotion/analyze")
        assert response.status_code == 422
    
    def test_emotion_health_endpoint(self, client):
        """测试情感分析健康检查接口"""
        response = client.get("/api/v1/emotion/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'ok'
        assert data['service'] == 'emotion_analysis'

class TestImageAPI:
    """图片编辑API测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_image_service(self):
        """模拟图片服务"""
        mock_service = Mock()
        mock_service.edit_image.return_value = {
            "local_path": "data/generated_images/edited.png",
            "remote_url": "http://example.com/image.png"
        }
        
        return mock_service
    
    def test_edit_image_endpoint_success(self, client):
        """测试图片编辑接口成功场景"""
        # 创建模拟的图片文件
        image_data = b"fake_image_data"
        
        response = client.post(
            "/api/v1/images/edit",
            files={"image": ("test.png", image_data, "image/png")},
            data={"prompt": "让图片更明亮"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'succeeded'
        assert 'outputs' in data
        assert len(data['outputs']) > 0
        assert data['outputs'][0]['prompt'] == "让图片更明亮"
    
    def test_edit_image_endpoint_missing_image(self, client):
        """测试图片编辑接口缺少图片"""
        response = client.post(
            "/api/v1/images/edit",
            data={"prompt": "测试提示词"}
        )
        assert response.status_code == 422
    
    def test_edit_image_endpoint_missing_prompt(self, client):
        """测试图片编辑接口缺少提示词"""
        image_data = b"fake_image_data"
        
        response = client.post(
            "/api/v1/images/edit",
            files={"image": ("test.png", image_data, "image/png")}
        )
        assert response.status_code == 422
    
    def test_generate_image_endpoint_success(self, client):
        """测试图片生成接口成功场景"""
        response = client.post(
            "/api/v1/images/generate",
            json={
                "prompt": "一只可爱的小猫",
                "size": "1024x1024",
                "save_local": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'succeeded'
        assert 'outputs' in data
        assert len(data['outputs']) > 0
        assert data['outputs'][0]['prompt'] == "一只可爱的小猫"

class TestHealthAPI:
    """健康检查API测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)
    
    def test_health_check_endpoint(self, client):
        """测试健康检查接口"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'ok'
        assert 'version' in data

class TestErrorHandling:
    """错误处理测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)
    
    def test_emotion_analysis_error_handling(self, client):
        """测试情感分析错误处理"""
        with patch('src.api.v1.emotion.MultiModelEmotionAnalyzer') as mock_service_class:
            mock_service = Mock()
            mock_service.run_three_stage_analysis.side_effect = Exception("模拟错误")
            mock_service_class.return_value = mock_service
            
            audio_data = b"fake_audio_data"
            response = client.post(
                "/api/v1/emotion/analyze",
                files={"audio_file": ("test.wav", audio_data, "audio/wav")}
            )
            
            assert response.status_code == 500
            data = response.json()
            assert 'detail' in data
    
    def test_image_processing_error_handling(self, client):
        """测试图片处理错误处理"""
        with patch('src.api.v1.image.ImageEditor') as mock_editor_class:
            mock_editor = Mock()
            mock_editor.edit_image.side_effect = Exception("模拟错误")
            mock_editor_class.return_value = mock_editor
            
            image_data = b"fake_image_data"
            
            response = client.post(
                "/api/v1/images/edit",
                files={"image": ("test.png", image_data, "image/png")},
                data={"prompt": "测试提示词"}
            )
            
            assert response.status_code == 500
            data = response.json()
            assert 'detail' in data

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
