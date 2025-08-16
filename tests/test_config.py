"""
配置管理器测试
"""
import pytest
import os
import tempfile
import json
from unittest.mock import Mock, patch

from src.core.config_manager import ConfigManager

class TestConfigManager:
    """配置管理器测试"""
    
    @pytest.fixture
    def temp_config_file(self):
        """创建临时配置文件"""
        config_data = {
            "project": {
                "name": "测试项目",
                "version": "1.0.0",
                "description": "测试描述"
            },
            "paths": {
                "input_dir": "data/input",
                "output_dir": "data/output",
                "temp_dir": "data/temp",
                "models_cache": "./data/models",
                "generated_images_dir": "data/generated_images"
            },
            "models": {
                "emotion2vec": {
                    "name": "iic/emotion2vec_plus_large",
                    "type": "funasr",
                    "local_path": "data/models/emotion2vec_plus_large"
                },
                "paraformer": {
                    "name": "paraformer-zh",
                    "type": "funasr",
                    "local_path": "data/models/paraformer-zh"
                },
                "text_emotion": {
                    "name": "distilbert-base-uncased-go-emotions-student",
                    "type": "transformers",
                    "local_path": "data/models/distilbert-base-uncased-go-emotions-student"
                }
            },
            "image_models": {
                "i2i": {
                    "use_api": True,
                    "provider": "doubao",
                    "model_name": "doubao-seededit-3.0-i2i"
                },
                "t2i": {
                    "use_api": True,
                    "provider": "doubao",
                    "model_name": "doubao-seedream-3.0-t2i"
                }
            },
            "secrets": {
                "doubao_api_key_env": "ARK_API_KEY",
                "openai_api_key_env": "OPENAI_API_KEY"
            },
            "settings": {
                "use_local_models": True,
                "download_to_project": True,
                "cache_models": True
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        yield temp_path
        
        # 清理临时文件
        os.unlink(temp_path)
    
    @pytest.fixture
    def config_manager(self, temp_config_file):
        """创建配置管理器实例"""
        return ConfigManager(temp_config_file)
    
    def test_init_with_default_config(self):
        """测试使用默认配置初始化"""
        config_manager = ConfigManager()
        
        assert config_manager.config is not None
        assert "paths" in config_manager.config
        assert "models" in config_manager.config
        assert "image_models" in config_manager.config
    
    def test_init_with_custom_config(self, temp_config_file):
        """测试使用自定义配置文件初始化"""
        config_manager = ConfigManager(temp_config_file)
        
        assert config_manager.config is not None
        assert config_manager.config["project"]["name"] == "测试项目"
        assert config_manager.config["project"]["version"] == "1.0.0"
    
    def test_get_model_path(self, config_manager):
        """测试获取模型路径"""
        emotion2vec_path = config_manager.get_model_path("emotion2vec")
        assert emotion2vec_path == "data/models/emotion2vec_plus_large"
        
        paraformer_path = config_manager.get_model_path("paraformer")
        assert paraformer_path == "data/models/paraformer-zh"
        
        # 测试不存在的模型
        nonexistent_path = config_manager.get_model_path("nonexistent")
        assert nonexistent_path is None
    
    def test_get_output_dir(self, config_manager):
        """测试获取输出目录"""
        output_dir = config_manager.get_output_dir()
        assert output_dir == "data/output"
    
    def test_get_audio_path(self, config_manager):
        """测试获取音频文件路径"""
        audio_path = config_manager.get_audio_path("test.wav")
        assert audio_path == "data/input/test.wav"
    
    def test_get_generated_images_dir(self, config_manager):
        """测试获取生成图片目录"""
        images_dir = config_manager.get_generated_images_dir()
        assert images_dir == "data/generated_images"
    
    def test_get_image_cfg(self, config_manager):
        """测试获取图片模型配置"""
        i2i_cfg = config_manager.get_image_cfg("i2i")
        assert i2i_cfg["model_name"] == "doubao-seededit-3.0-i2i"
        assert i2i_cfg["provider"] == "doubao"
        
        t2i_cfg = config_manager.get_image_cfg("t2i")
        assert t2i_cfg["model_name"] == "doubao-seedream-3.0-t2i"
        
        # 测试默认配置
        default_cfg = config_manager.get_image_cfg()
        assert default_cfg["model_name"] == "doubao-seededit-3.0-i2i"
    
    def test_get_secret(self, config_manager):
        """测试获取密钥"""
        doubao_key = config_manager.get_secret("doubao_api_key_env")
        assert doubao_key == "ARK_API_KEY"
        
        openai_key = config_manager.get_secret("openai_api_key_env")
        assert openai_key == "OPENAI_API_KEY"
        
        # 测试不存在的密钥
        nonexistent_key = config_manager.get_secret("nonexistent")
        assert nonexistent_key is None
    
    @patch.dict(os.environ, {"ARK_API_KEY": "test_api_key_value"})
    def test_get_model_api_key(self, config_manager):
        """测试获取模型API密钥"""
        # 测试豆包API密钥
        i2i_key = config_manager.get_model_api_key("i2i")
        assert i2i_key == "test_api_key_value"
        
        t2i_key = config_manager.get_model_api_key("t2i")
        assert t2i_key == "test_api_key_value"
        
        # 测试OpenAI API密钥
        openai_key = config_manager.get_model_api_key("openai")
        assert openai_key == "test_api_key_value"
        
        # 测试不存在的模型类型
        nonexistent_key = config_manager.get_model_api_key("nonexistent")
        assert nonexistent_key is None
    
    def test_validate_config(self, config_manager):
        """测试配置验证"""
        # 有效配置应该不抛出异常
        config_manager._validate_config()
        
        # 测试缺少必需键的配置
        invalid_config = {"paths": {}}
        config_manager.config = invalid_config
        
        with pytest.raises(ValueError, match="配置文件缺少必需的键"):
            config_manager._validate_config()
    
    def test_ensure_dirs(self, config_manager):
        """测试目录创建"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 修改配置使用临时目录
            config_manager.config["paths"]["input_dir"] = os.path.join(temp_dir, "input")
            config_manager.config["paths"]["output_dir"] = os.path.join(temp_dir, "output")
            config_manager.config["paths"]["temp_dir"] = os.path.join(temp_dir, "temp")
            config_manager.config["paths"]["models_cache"] = os.path.join(temp_dir, "models")
            config_manager.config["paths"]["generated_images_dir"] = os.path.join(temp_dir, "images")
            
            config_manager._ensure_dirs()
            
            # 验证目录是否创建
            assert os.path.exists(config_manager.config["paths"]["input_dir"])
            assert os.path.exists(config_manager.config["paths"]["output_dir"])
            assert os.path.exists(config_manager.config["paths"]["temp_dir"])
            assert os.path.exists(config_manager.config["paths"]["models_cache"])
            assert os.path.exists(config_manager.config["paths"]["generated_images_dir"])
    
    @patch.dict(os.environ, {
        "HF_HOME": "/tmp/hf_home",
        "MODELSCOPE_CACHE": "/tmp/modelscope_cache"
    })
    def test_setup_environment(self, config_manager):
        """测试环境变量设置"""
        config_manager.setup_environment()
        
        assert os.environ["HF_HOME"] == "data/models"
        assert os.environ["MODELSCOPE_CACHE"] == "data/models"
    
    def test_config_structure(self, config_manager):
        """测试配置结构完整性"""
        config = config_manager.config
        
        # 检查项目信息
        assert "project" in config
        assert "name" in config["project"]
        assert "version" in config["project"]
        assert "description" in config["project"]
        
        # 检查路径配置
        assert "paths" in config
        required_paths = ["input_dir", "output_dir", "temp_dir", "models_cache", "generated_images_dir"]
        for path_key in required_paths:
            assert path_key in config["paths"]
        
        # 检查模型配置
        assert "models" in config
        required_models = ["emotion2vec", "paraformer", "text_emotion"]
        for model_key in required_models:
            assert model_key in config["models"]
        
        # 检查图片模型配置
        assert "image_models" in config
        required_image_models = ["i2i", "t2i"]
        for image_model_key in required_image_models:
            assert image_model_key in config["image_models"]
        
        # 检查密钥配置
        assert "secrets" in config
        assert "doubao_api_key_env" in config["secrets"]
        
        # 检查设置配置
        assert "settings" in config
        assert "use_local_models" in config["settings"]
        assert "download_to_project" in config["settings"]
        assert "cache_models" in config["settings"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

