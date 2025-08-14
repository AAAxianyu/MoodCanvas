"""
pytest配置文件
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="session")
def mock_environment():
    """模拟环境变量"""
    env_vars = {
        "ARK_API_KEY": "test_api_key_value",
        "OPENAI_API_KEY": "test_openai_key",
        "STABILITY_API_KEY": "test_stability_key"
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture(scope="session")
def mock_config():
    """模拟配置数据"""
    return {
        "project": {
            "name": "测试项目",
            "version": "1.0.0",
            "description": "测试描述"
        },
        "paths": {
            "input_dir": "data/input",
            "output_dir": "data/output",
            "temp_dir": "data/temp",
            "models_cache": "./src/data/models",
            "generated_images_dir": "data/generated_images"
        },
        "models": {
            "emotion2vec": {
                "name": "iic/emotion2vec_plus_large",
                "type": "funasr",
                "local_path": "src/data/models/emotion2vec_plus_large",
                "use_local_models": True
            },
            "paraformer": {
                "name": "paraformer-zh",
                "type": "funasr",
                "local_path": "src/data/models/paraformer-zh",
                "use_local_models": True
            },
            "text_emotion": {
                "name": "distilbert-base-uncased-go-emotions-student",
                "type": "transformers",
                "local_path": "src/data/models/distilbert-base-uncased-go-emotions-student",
                "use_local_models": True
            }
        },
        "image_models": {
            "i2i": {
                "use_api": True,
                "provider": "doubao",
                "model_name": "doubao-seededit-3.0-i2i",
                "defaults": {
                    "guidance_scale": 5.5,
                    "size": "adaptive",
                    "watermark": True
                }
            },
            "t2i": {
                "use_api": True,
                "provider": "doubao",
                "model_name": "doubao-seedream-3.0-t2i",
                "defaults": {
                    "guidance_scale": 7.5,
                    "size": "1024x1024",
                    "num_images": 1,
                    "watermark": True
                }
            }
        },
        "secrets": {
            "doubao_api_key_env": "ARK_API_KEY",
            "openai_api_key_env": "OPENAI_API_KEY",
            "stability_api_key_env": "STABILITY_API_KEY"
        },
        "settings": {
            "use_local_models": True,
            "download_to_project": True,
            "cache_models": True,
            "batch_size": 1,
            "granularity": "utterance",
            "extract_embedding": False
        }
    }

@pytest.fixture(scope="session")
def mock_config_manager(mock_config):
    """模拟配置管理器"""
    mock_cm = Mock()
    mock_cm.config = mock_config
    mock_cm.get_model_path.side_effect = lambda name: mock_config["models"].get(name, {}).get("local_path")
    mock_cm.get_output_dir.return_value = mock_config["paths"]["output_dir"]
    mock_cm.get_audio_path.side_effect = lambda filename: os.path.join(mock_config["paths"]["input_dir"], filename)
    mock_cm.get_generated_images_dir.return_value = mock_config["paths"]["generated_images_dir"]
    mock_cm.get_image_cfg.side_effect = lambda key="i2i": mock_config["image_models"].get(key, {})
    mock_cm.get_secret.side_effect = lambda name: mock_config["secrets"].get(name)
    mock_cm.get_model_api_key.side_effect = lambda model_type: "test_api_key_value"
    
    return mock_cm

@pytest.fixture(scope="function")
def temp_dir():
    """临时目录"""
    import tempfile
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    
    # 清理临时目录
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture(scope="function")
def mock_emotion_result():
    """模拟情感分析结果"""
    return [
        {"label": "joy", "score": 0.85},
        {"label": "excitement", "score": 0.72}
    ]

@pytest.fixture(scope="function")
def mock_audio_emotion_result():
    """模拟音频情感分析结果"""
    return [
        {"raw_result": {"emotion": 3}}  # happy
    ]

@pytest.fixture(scope="function")
def mock_image_result():
    """模拟图片生成结果"""
    return {
        "local_paths": ["data/generated_images/test.png"],
        "remote_urls": ["http://example.com/test.png"]
    }

@pytest.fixture(scope="function")
def mock_edit_result():
    """模拟图片编辑结果"""
    return {
        "local_path": "data/generated_images/edited.png",
        "remote_url": "http://example.com/edited.png",
        "changes_applied": "根据提示词对图片进行了编辑"
    }

@pytest.fixture(scope="function")
def sample_text():
    """示例文本"""
    return "今天天气很好，心情愉快"

@pytest.fixture(scope="function")
def sample_audio_data():
    """示例音频数据"""
    return b"RIFF" + b"\x00\x00\x00\x08" + b"WAVE" + b"fake_wav_data"

@pytest.fixture(scope="function")
def sample_image_data():
    """示例图片数据"""
    return b'\x89PNG\r\n\x1a\n' + b'fake_png_data'

@pytest.fixture(scope="function")
def mock_requests_response():
    """模拟HTTP响应"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "images": [
                {"url": "http://example.com/image.png"}
            ]
        }
    }
    mock_response.content = b"fake_image_data"
    return mock_response

@pytest.fixture(scope="function")
def mock_funasr_model():
    """模拟FunASR模型"""
    mock_model = Mock()
    mock_model.generate.return_value = {
        "emotion": 3,  # happy
        "confidence": 0.85
    }
    return mock_model

@pytest.fixture(scope="function")
def mock_transformers_pipeline():
    """模拟Transformers pipeline"""
    mock_pipeline = Mock()
    mock_pipeline.return_value = [
        {"label": "joy", "score": 0.85},
        {"label": "excitement", "score": 0.72}
    ]
    return mock_pipeline

@pytest.fixture(scope="function")
def mock_asr_result():
    """模拟ASR结果"""
    return {
        "text": "今天天气很好",
        "confidence": 0.95
    }

@pytest.fixture(scope="function")
def mock_llm_response():
    """模拟LLM响应"""
    return "基于您的情感'joy'，我为'今天天气很好'创作了这段文案：在joy的旋律中，今天天气很好仿佛有了新的生命..."

@pytest.fixture(scope="function")
def mock_file_validation():
    """模拟文件验证"""
    return {
        "image": True,
        "audio": True,
        "size": True
    }

@pytest.fixture(scope="function")
def mock_error_response():
    """模拟错误响应"""
    return {
        "success": False,
        "error": {
            "message": "测试错误",
            "code": "TEST_ERROR",
            "status_code": 500,
            "details": {}
        },
        "timestamp": "2024-01-01T00:00:00Z"
    }

@pytest.fixture(scope="function")
def mock_success_response():
    """模拟成功响应"""
    return {
        "success": True,
        "message": "操作成功",
        "data": {"key": "value"},
        "status_code": 200,
        "timestamp": "2024-01-01T00:00:00Z"
    }

# 标记测试类型
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line(
        "markers", "unit: 单元测试"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试"
    )
    config.addinivalue_line(
        "markers", "api: API测试"
    )
    config.addinivalue_line(
        "markers", "models: 模型测试"
    )
    config.addinivalue_line(
        "markers", "services: 服务测试"
    )
    config.addinivalue_line(
        "markers", "utils: 工具函数测试"
    )

# 测试收集钩子
def pytest_collection_modifyitems(config, items):
    """修改测试收集"""
    for item in items:
        # 根据文件名自动标记测试类型
        if "test_api" in item.nodeid:
            item.add_marker(pytest.mark.api)
        elif "test_models" in item.nodeid:
            item.add_marker(pytest.mark.models)
        elif "test_services" in item.nodeid:
            item.add_marker(pytest.mark.services)
        elif "test_utils" in item.nodeid:
            item.add_marker(pytest.mark.utils)
        elif "test_config" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "test_exceptions" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        
        # 默认标记为单元测试
        if not any(item.iter_markers()):
            item.add_marker(pytest.mark.unit)

# 测试报告钩子
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """测试总结"""
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    # 统计测试结果
    stats = terminalreporter.stats
    if stats:
        for key, value in stats.items():
            print(f"{key}: {len(value)}")
    
    print(f"退出状态: {exitstatus}")
    print("="*60)



