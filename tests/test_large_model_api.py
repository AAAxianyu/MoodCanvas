"""
大模型API调用测试
测试豆包、OpenAI等大模型的API调用功能
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.config_manager import ConfigManager
from src.models.image.image2image import ImageEditor
from src.models.image.text2image import ImageGenerator
from src.services.text_generator import TextGenerator


class TestLargeModelAPI:
    """大模型API调用测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前设置"""
        # 设置测试环境变量
        self.test_env = {
            "ARK_API_KEY": "test_doubao_api_key_12345",
            "OPENAI_API_KEY": "sk-test_openai_key_12345",
            "STABILITY_API_KEY": "test_stability_key_12345"
        }
        
        # 模拟环境变量
        with patch.dict(os.environ, self.test_env):
            yield
    
    def test_doubao_image_edit_api(self):
        """测试豆包图片编辑API"""
        # 模拟配置管理器
        mock_config = {
            "image_models": {
                "i2i": {
                    "use_api": True,
                    "provider": "doubao",
                    "model_name": "doubao-seededit-3.0-i2i",
                    "api": {
                        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                        "api_key_env": "ARK_API_KEY"
                    },
                    "defaults": {
                        "guidance_scale": 5.5,
                        "size": "adaptive",
                        "watermark": True
                    }
                }
            },
            "secrets": {
                "doubao_api_key_env": "ARK_API_KEY"
            },
            "paths": {
                "generated_images_dir": "data/generated_images"
            }
        }
        
        with patch.object(ConfigManager, 'config', mock_config), \
             patch.object(ConfigManager, 'get_model_api_key', return_value="test_doubao_api_key_12345"), \
             patch.object(ConfigManager, 'get_generated_images_dir', return_value="data/generated_images"):
            
            # 模拟Ark客户端
            mock_ark_client = Mock()
            mock_response = Mock()
            mock_response.data = [Mock(url="https://example.com/generated_image.png")]
            
            mock_ark_client.images.generate.return_value = mock_response
            
            with patch('src.models.image.image2image.Ark', return_value=mock_ark_client):
                # 创建图片编辑器实例
                config_manager = ConfigManager()
                editor = ImageEditor(config_manager)
                
                # 测试图片编辑
                result = editor.edit_image(
                    input_path_or_url="https://example.com/test_image.jpg",
                    prompt="将图片改为水彩画风格",
                    guidance_scale=5.5,
                    size="adaptive",
                    watermark=True
                )
                
                # 验证结果
                assert result["remote_url"] == "https://example.com/generated_image.png"
                assert "local_path" not in result  # 没有保存本地
                
                # 验证API调用参数
                mock_ark_client.images.generate.assert_called_once()
                call_args = mock_ark_client.images.generate.call_args
                assert call_args[1]["model"] == "doubao-seededit-3.0-i2i"
                assert call_args[1]["prompt"] == "将图片改为水彩画风格"
                assert call_args[1]["guidance_scale"] == 5.5
                assert call_args[1]["size"] == "adaptive"
                assert call_args[1]["watermark"] is True
    
    def test_doubao_text_to_image_api(self):
        """测试豆包文本生成图片API"""
        mock_config = {
            "image_models": {
                "t2i": {
                    "use_api": True,
                    "provider": "doubao",
                    "model_name": "doubao-seedream-3.0-t2i",
                    "api": {
                        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                        "api_key_env": "ARK_API_KEY"
                    },
                    "defaults": {
                        "guidance_scale": 7.5,
                        "size": "1024x1024",
                        "num_images": 1,
                        "watermark": True
                    }
                }
            },
            "secrets": {
                "doubao_api_key_env": "ARK_API_KEY"
            },
            "paths": {
                "generated_images_dir": "data/generated_images"
            }
        }
        
        with patch.object(ConfigManager, 'config', mock_config), \
             patch.object(ConfigManager, 'get_model_api_key', return_value="test_doubao_api_key_12345"), \
             patch.object(ConfigManager, 'get_generated_images_dir', return_value="data/generated_images"):
            
            # 模拟Ark客户端
            mock_ark_client = Mock()
            mock_response = Mock()
            mock_response.data = [Mock(url="https://example.com/generated_image.png")]
            
            mock_ark_client.images.generate.return_value = mock_response
            
            with patch('src.models.image.text2image.Ark', return_value=mock_ark_client):
                # 创建图片生成器实例
                config_manager = ConfigManager()
                generator = ImageGenerator(config_manager)
                
                # 测试图片生成
                result = generator.generate(
                    prompt="一只可爱的小猫在花园里玩耍",
                    guidance_scale=7.5,
                    size="1024x1024",
                    num_images=1,
                    watermark=True
                )
                
                # 验证结果
                assert "remote_urls" in result
                assert len(result["remote_urls"]) == 1
                assert result["remote_urls"][0] == "https://example.com/generated_image.png"
                
                # 验证API调用参数
                mock_ark_client.images.generate.assert_called_once()
                call_args = mock_ark_client.images.generate.call_args
                assert call_args[1]["model"] == "doubao-seedream-3.0-t2i"
                assert call_args[1]["prompt"] == "一只可爱的小猫在花园里玩耍"
                assert call_args[1]["guidance_scale"] == 7.5
                assert call_args[1]["size"] == "1024x1024"
                assert call_args[1]["watermark"] is True
    
    def test_openai_text_generation_api(self):
        """测试OpenAI文本生成API"""
        mock_config = {
            "text_generation": {
                "use_api": True,
                "provider": "openai",
                "model_name": "gpt-3.5-turbo",
                "api": {
                    "base_url": "https://api.openai.com/v1",
                    "api_key_env": "OPENAI_API_KEY"
                },
                "defaults": {
                    "max_tokens": 300,
                    "temperature": 0.8
                }
            },
            "secrets": {
                "openai_api_key_env": "OPENAI_API_KEY"
            }
        }
        
        with patch.object(ConfigManager, 'config', mock_config), \
             patch.object(ConfigManager, 'get_secret', return_value="sk-test_openai_key_12345"):
            
            # 模拟OpenAI客户端
            mock_openai_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="这是一段生成的文本内容"))]
            
            mock_openai_client.chat.completions.create.return_value = mock_response
            
            with patch('src.services.text_generator.openai', mock_openai_client):
                # 创建文本生成器实例
                config_manager = ConfigManager()
                generator = TextGenerator(config_manager)
                
                # 测试文本生成
                result = generator.generate_text(
                    prompt="请写一首关于春天的诗",
                    style="poetic",
                    max_tokens=300,
                    temperature=0.8
                )
                
                # 验证结果
                assert "text" in result
                assert result["text"] == "这是一段生成的文本内容"
                
                # 验证API调用参数
                mock_openai_client.chat.completions.create.assert_called_once()
                call_args = mock_openai_client.chat.completions.create.call_args
                assert call_args[1]["model"] == "gpt-3.5-turbo"
                assert call_args[1]["messages"][0]["content"] == "请写一首关于春天的诗"
                assert call_args[1]["max_tokens"] == 300
                assert call_args[1]["temperature"] == 0.8
    
    def test_api_key_validation(self):
        """测试API密钥验证"""
        # 测试豆包API密钥
        with patch.dict(os.environ, {"ARK_API_KEY": ""}):
            with pytest.raises(RuntimeError, match="豆包API密钥未设置"):
                mock_config = {
                    "image_models": {
                        "i2i": {
                            "use_api": True,
                            "provider": "doubao",
                            "model_name": "doubao-seededit-3.0-i2i",
                            "api": {
                                "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                                "api_key_env": "ARK_API_KEY"
                            }
                        }
                    },
                    "paths": {
                        "generated_images_dir": "data/generated_images"
                    }
                }
                
                with patch.object(ConfigManager, 'config', mock_config), \
                     patch.object(ConfigManager, 'get_model_api_key', return_value=None):
                    config_manager = ConfigManager()
                    ImageEditor(config_manager)
    
    def test_api_error_handling(self):
        """测试API错误处理"""
        mock_config = {
            "image_models": {
                "i2i": {
                    "use_api": True,
                    "provider": "doubao",
                    "model_name": "doubao-seededit-3.0-i2i",
                    "api": {
                        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                        "api_key_env": "ARK_API_KEY"
                    },
                    "defaults": {
                        "guidance_scale": 5.5,
                        "size": "adaptive",
                        "watermark": True
                    }
                }
            },
            "secrets": {
                "doubao_api_key_env": "ARK_API_KEY"
            },
            "paths": {
                "generated_images_dir": "data/generated_images"
            }
        }
        
        with patch.object(ConfigManager, 'config', mock_config), \
             patch.object(ConfigManager, 'get_model_api_key', return_value="test_doubao_api_key_12345"), \
             patch.object(ConfigManager, 'get_generated_images_dir', return_value="data/generated_images"):
            
            # 模拟API调用失败
            mock_ark_client = Mock()
            mock_ark_client.images.generate.side_effect = Exception("API调用失败")
            
            with patch('src.models.image.image2image.Ark', return_value=mock_ark_client):
                config_manager = ConfigManager()
                editor = ImageEditor(config_manager)
                
                # 测试错误处理
                with pytest.raises(Exception, match="API调用失败"):
                    editor.edit_image(
                        input_path_or_url="https://example.com/test_image.jpg",
                        prompt="将图片改为水彩画风格"
                    )
    
    def test_local_file_handling(self):
        """测试本地文件处理"""
        mock_config = {
            "image_models": {
                "i2i": {
                    "use_api": True,
                    "provider": "doubao",
                    "model_name": "doubao-seededit-3.0-i2i",
                    "api": {
                        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                        "api_key_env": "ARK_API_KEY"
                    },
                    "defaults": {
                        "guidance_scale": 5.5,
                        "size": "adaptive",
                        "watermark": True
                    }
                }
            },
            "secrets": {
                "doubao_api_key_env": "ARK_API_KEY"
            },
            "paths": {
                "generated_images_dir": "data/generated_images"
            }
        }
        
        with patch.object(ConfigManager, 'config', mock_config), \
             patch.object(ConfigManager, 'get_model_api_key', return_value="test_doubao_api_key_12345"), \
             patch.object(ConfigManager, 'get_generated_images_dir', return_value="data/generated_images"):
            
            # 模拟Ark客户端
            mock_ark_client = Mock()
            mock_response = Mock()
            mock_response.data = [Mock(url="https://example.com/generated_image.png")]
            
            mock_ark_client.images.generate.return_value = mock_response
            
            with patch('src.models.image.image2image.Ark', return_value=mock_ark_client), \
                 patch('builtins.open', create=True), \
                 patch('os.path.exists', return_value=True):
                
                config_manager = ConfigManager()
                editor = ImageEditor(config_manager)
                
                # 测试本地文件处理
                result = editor.edit_image(
                    input_path_or_url="/path/to/local/image.jpg",
                    prompt="将图片改为水彩画风格"
                )
                
                # 验证结果
                assert result["remote_url"] == "https://example.com/generated_image.png"
                
                # 验证文件处理
                mock_ark_client.images.generate.assert_called_once()
                call_args = mock_ark_client.images.generate.call_args
                assert call_args[1]["image"] is not None  # 应该是文件对象


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
