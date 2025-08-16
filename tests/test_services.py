"""
服务层测试
"""
import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# 导入服务
from src.services.emotion_analyzer import MultiModelEmotionAnalyzer
from src.services.image_service import ImageService
from src.core.exceptions import EmotionAnalysisError, AudioProcessingError, GenerationError, ImageProcessingError

class TestMultiModelEmotionAnalyzer:
    """三阶段多模型情感分析器测试"""
    
    @pytest.fixture
    def mock_config_manager(self):
        """模拟配置管理器"""
        mock_config = Mock()
        mock_config.config = {
            "models": {
                "text_emotion": {"local_path": "test_path", "use_local_models": True},
                "emotion2vec": {"local_path": "test_path", "use_local_models": True},
                "paraformer": {"local_path": "test_path", "use_local_models": True}
            },
            "image_models": {
                "i2i": {"model_name": "test_model"},
                "t2i": {"model_name": "test_model"}
            },
            "settings": {
                "use_local_models": True
            }
        }
        return mock_config
    
    @pytest.fixture
    def analyzer(self, mock_config_manager):
        """创建分析器实例"""
        with patch('src.services.emotion_analyzer.TextEmotionModel') as mock_text_model:
            with patch('src.services.emotion_analyzer.AudioEmotionModel') as mock_audio_model:
                with patch('src.services.emotion_analyzer.ParaformerModel') as mock_asr_model:
                    with patch('src.services.emotion_analyzer.ImageGenerator') as mock_image_gen:
                        # 模拟模型加载
                        mock_text_model.return_value.load_model.return_value = True
                        mock_audio_model.return_value.load_model.return_value = True
                        mock_asr_model.return_value.load_model.return_value = True
                        mock_image_gen.return_value.load_model.return_value = True
                        
                        analyzer = MultiModelEmotionAnalyzer(mock_config_manager)
                        return analyzer
    
    def test_run_three_stage_analysis_success(self, analyzer):
        """测试三阶段情感分析成功场景"""
        # 模拟ASR结果
        with patch.object(analyzer.asr_model, 'transcribe', return_value="识别的文字"):
            # 模拟文本情感分析结果
            mock_text_emotion = [{"label": "joy", "score": 0.8}]
            
            # 模拟音频情感分析结果
            mock_audio_emotion = [{"raw_result": {"emotion": 3}}]  # happy
            
            # 模拟图片生成结果
            mock_image_result = {
                "local_paths": ["data/generated_images/test.png"]
            }
            
            with patch.object(analyzer.text_emotion_model, 'analyze', return_value=mock_text_emotion):
                with patch.object(analyzer.audio_emotion_model, 'analyze', return_value=mock_audio_emotion):
                    with patch.object(analyzer.image_generator, 'generate', return_value=mock_image_result):
                        result = analyzer.run_three_stage_analysis("test.wav")
                        
                        assert result['status'] == 'success'
                        assert result['transcribed_text'] == "识别的文字"
                        assert 'emotion_analysis' in result
                        assert 'generated_content' in result
                        assert result['generated_content']['image_path'] == "data/generated_images/test.png"
    
    def test_run_three_stage_analysis_asr_failure(self, analyzer):
        """测试ASR失败场景"""
        with patch.object(analyzer.asr_model, 'transcribe', return_value=None):
            with pytest.raises(EmotionAnalysisError, match="语音识别失败"):
                analyzer.run_three_stage_analysis("test.wav")
    
    def test_extract_audio_emotion_tags(self, analyzer):
        """测试音频情感标签提取"""
        # 测试emotion2vec输出格式
        emotion_result = [{"raw_result": {"emotion": 3}}]  # happy
        tags = analyzer._extract_audio_emotion_tags(emotion_result)
        assert "happy" in tags
        
        # 测试多个情感标签
        emotion_result = [{"raw_result": {"emotions": [{"emotion": 0}, {"emotion": 6}]}}]
        tags = analyzer._extract_audio_emotion_tags(emotion_result)
        assert "angry" in tags
        assert "sad" in tags
    
    def test_extract_text_emotion_tags(self, analyzer):
        """测试文本情感标签提取"""
        # 测试transformers pipeline输出格式
        emotion_result = [{"label": "joy", "score": 0.8}]
        tags = analyzer._extract_text_emotion_tags(emotion_result)
        assert "joy" in tags
        
        # 测试多个标签
        emotion_result = [
            {"label": "excitement", "score": 0.9},
            {"label": "optimism", "score": 0.7}
        ]
        tags = analyzer._extract_text_emotion_tags(emotion_result)
        assert "excitement" in tags
        assert "optimism" in tags
    
    def test_fuse_emotions(self, analyzer):
        """测试情感融合"""
        audio_emotions = ["happy", "excited"]
        text_emotions = ["joy", "optimism"]
        
        # 测试weighted策略
        merged = analyzer._fuse_emotions(audio_emotions, text_emotions, "weighted")
        assert len(merged) <= 3
        
        # 测试max策略
        merged = analyzer._fuse_emotions(audio_emotions, text_emotions, "max")
        assert len(merged) == 2
        
        # 测试average策略
        merged = analyzer._fuse_emotions(audio_emotions, text_emotions, "average")
        assert len(merged) <= 4
    
    def test_build_image_prompt(self, analyzer):
        """测试图像提示词构建"""
        text = "今天天气很好"
        emotion_tags = ["happy", "joy"]
        
        prompt = analyzer._build_image_prompt(text, emotion_tags)
        assert text in prompt
        assert "happy" in prompt
        assert "joy" in prompt

class TestImageService:
    """图片服务测试"""
    
    @pytest.fixture
    def mock_config_manager(self):
        """模拟配置管理器"""
        mock_config = Mock()
        mock_config.config = {
            "image_models": {
                "i2i": {"model_name": "test_model"}
            }
        }
        return mock_config
    
    @pytest.fixture
    def service(self, mock_config_manager):
        """创建服务实例"""
        with patch('src.services.image_service.ConfigManager', return_value=mock_config_manager):
            with patch('src.services.image_service.ImageEditor') as mock_editor:
                mock_editor.return_value.edit_image.return_value = {
                    "local_path": "data/generated_images/edited.png",
                    "remote_url": "http://example.com/image.png"
                }
                
                service = ImageService()
                return service
    
    @pytest.mark.asyncio
    async def test_edit_image_service_success(self, service):
        """测试图片编辑服务成功场景"""
        # 模拟图片数据
        image_data = b"fake_image_data"
        
        with patch('src.utils.file_utils.validate_image_file', return_value=True):
            with patch('src.utils.file_utils.save_uploaded_file', return_value=True):
                result = await service.edit_image_service(
                    original_image_data=image_data,
                    new_prompt="让图片更明亮"
                )
                
                assert result['status'] == 'success'
                assert result['new_prompt'] == "让图片更明亮"
                assert 'edit_result' in result
                assert result['edit_result']['edited_image_path'] == "data/generated_images/edited.png"
    
    @pytest.mark.asyncio
    async def test_edit_image_service_invalid_format(self, service):
        """测试图片格式无效场景"""
        image_data = b"invalid_image_data"
        
        with patch('src.utils.file_utils.validate_image_file', return_value=False):
            with pytest.raises(ImageProcessingError, match="无效的图片文件格式"):
                await service.edit_image_service(
                    original_image_data=image_data,
                    new_prompt="测试提示词"
                )
    
    def test_calculate_guidance_scale(self, service):
        """测试guidance_scale计算"""
        # 测试强度0.0
        scale = service._calculate_guidance_scale(0.0)
        assert scale == 1.0
        
        # 测试强度1.0
        scale = service._calculate_guidance_scale(1.0)
        assert scale == 20.0
        
        # 测试强度0.5
        scale = service._calculate_guidance_scale(0.5)
        assert 1.0 < scale < 20.0
        
        # 测试边界值
        scale = service._calculate_guidance_scale(-0.1)
        assert scale == 1.0
        
        scale = service._calculate_guidance_scale(1.1)
        assert scale == 20.0
    
    def test_get_model_info(self, service):
        """测试获取模型信息"""
        info = service.get_model_info()
        assert info['model_name'] == 'doubao-seedit-3.0-i2i'
        assert info['provider'] == 'doubao'
        assert 'image_editing' in info['capabilities']

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
