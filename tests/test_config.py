import pytest
import os
from pathlib import Path
from src.core.config_manager import ConfigManager
from src.core.exceptions import InvalidConfigError

class TestConfigManager:
    """测试配置管理器"""
    
    def test_load_config(self, mock_env_vars, tmp_path):
        """测试配置加载"""
        # 创建临时配置文件
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
        openai:
          api_key: ${OPENAI_API_KEY}
        stability:
          api_key: ${STABILITY_API_KEY}
        models:
          asr:
            type: paraformer
          emotion:
            type: text
          image:
            type: stability
        """)
        
        # 初始化配置管理器
        config = ConfigManager(config_file=str(config_file))
        config.load_config()
        
        # 验证配置
        assert config.get_config()["openai"]["api_key"] == "mock_key"
        assert config.get_config()["stability"]["api_key"] == "mock_key"
        assert config.get_config()["models"]["asr"]["type"] == "paraformer"
    
    def test_missing_config_file(self):
        """测试缺失配置文件"""
        config = ConfigManager(config_file="nonexistent.yaml")
        with pytest.raises(FileNotFoundError):
            config.load_config()
    
    def test_invalid_config(self, tmp_path):
        """测试无效配置"""
        # 创建无效配置文件
        config_file = tmp_path / "invalid_config.yaml"
        config_file.write_text("invalid: yaml: format")
        
        config = ConfigManager(config_file=str(config_file))
        with pytest.raises(InvalidConfigError):
            config.load_config()
    
    def test_missing_env_vars(self, tmp_path):
        """测试缺失环境变量"""
        # 创建需要环境变量的配置文件
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
        openai:
          api_key: ${MISSING_VAR}
        """)
        
        config = ConfigManager(config_file=str(config_file))
        with pytest.raises(ValueError, match="环境变量未设置"):
            config.load_config()
    
    def test_config_reload(self, mock_env_vars, tmp_path):
        """测试配置重载"""
        # 创建初始配置文件
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
        openai:
          api_key: ${OPENAI_API_KEY}
        """)
        
        config = ConfigManager(config_file=str(config_file))
        config.load_config()
        initial_config = config.get_config()
        
        # 修改配置文件
        config_file.write_text("""
        openai:
          api_key: new_key
        """)
        
        # 重载配置
        config.reload_config()
        new_config = config.get_config()
        
        assert new_config != initial_config
        assert new_config["openai"]["api_key"] == "new_key"
    
    def test_get_model_config(self, mock_env_vars, tmp_path):
        """测试获取模型配置"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
        models:
          asr:
            type: paraformer
            param1: value1
          emotion:
            type: text
            param2: value2
        """)
        
        config = ConfigManager(config_file=str(config_file))
        config.load_config()
        
        asr_config = config.get_model_config("asr")
        assert asr_config["type"] == "paraformer"
        assert asr_config["param1"] == "value1"
        
        emotion_config = config.get_model_config("emotion")
        assert emotion_config["type"] == "text"
        assert emotion_config["param2"] == "value2"
        
        with pytest.raises(KeyError):
            config.get_model_config("nonexistent")
