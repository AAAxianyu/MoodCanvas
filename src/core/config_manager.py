import os
import json
from typing import Optional


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path="config/config.json"):
        self.config_path = config_path
        self._config = self.load_config()
        self.config = self._config  # 兼容旧代码
        self._validate_config()
        self.setup_environment()
        self._ensure_dirs()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self.get_default_config()
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            "project": {
                "name": "三阶段多模型情感分析系统",
                "version": "2.0.0",
                "description": "集成Paraformer-zh ASR、英文文本情感分类、emotion2vec声学情感分析"
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
                    "local_path": "./src/data/models/emotion2vec_plus_large",
                    "model_id": "iic/emotion2vec_plus_large",
                    "description": "音频情感识别模型"
                },
                "paraformer": {
                    "name": "damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
                    "type": "funasr",
                    "local_path": "./src/data/models/paraformer-zh",
                    "model_id": "damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
                    "description": "中文语音转文字模型"
                },
                "text_emotion": {
                    "name": "distilbert-base-uncased-go-emotions-student",
                    "type": "transformers",
                    "local_path": "./src/data/models/distilbert-base-uncased-go-emotions-student",
                    "model_id": "distilbert-base-uncased-go-emotions-student",
                    "description": "英文文本情感分类模型"
                }
            },
            "image_models": {
                "i2i": {
                    "use_api": True,
                    "provider": "doubao",
                    "model_name": "doubao-seededit-3-0-i2i-250628",
                    "api": {
                        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                        "api_key_env": "ARK_API_KEY"
                    },
                    "defaults": {
                        "guidance_scale": 5.5,
                        "size": "adaptive",
                        "watermark": True
                    }
                },
                "t2i": {
                    "use_api": True,
                    "provider": "doubao",
                    "model_name": "doubao-seedream-3-0-t2i-250415",
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
                    "temperature": 0.8,
                    "style_options": ["poetic", "professional", "casual", "emotional"]
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
            },
            "audio_files": {
                "default": "test.wav",
                "available": ["asr_example.wav", "hive-0001.wav", "test.wav"]
            },
            "output_format": {
                "include_timestamp": True,
                "include_raw_data": True,
                "sort_by_confidence": True,
                "max_emotions_display": 10
            }
        }
    
    def setup_environment(self):
        """设置环境变量"""
        cache_dir = self.config["paths"]["models_cache"]
        if cache_dir.startswith("./"):
            cache_dir = cache_dir[2:]  # 移除 "./" 前缀
        os.environ['HF_HOME'] = cache_dir
        os.environ['MODELSCOPE_CACHE'] = cache_dir
    
    def _ensure_dirs(self):
        """确保必要的目录存在"""
        for k in ("input_dir", "output_dir", "temp_dir", "models_cache", "generated_images_dir"):
            d = self.config["paths"].get(k)
            if d:
                # 处理相对路径
                if d.startswith("./"):
                    d = d[2:]  # 移除 "./" 前缀
                if not os.path.exists(d):
                    os.makedirs(d, exist_ok=True)
    
    def get_generated_images_dir(self):
        """获取生成的图片目录"""
        dir_path = self.config["paths"].get("generated_images_dir", "data/generated_images")
        if dir_path.startswith("./"):
            dir_path = dir_path[2:]  # 移除 "./" 前缀
        return dir_path

    def get_image_cfg(self, key="i2i"):
        """获取图像模型配置"""
        return self.config.get("image_models", {}).get(key, {})

    def get_secret(self, name="doubao_api_key_env"):
        """获取API密钥"""
        env_name = self.config.get("secrets", {}).get(name)
        return os.environ.get(env_name) if env_name else None
    
    def get_model_api_key(self, model_type: str) -> Optional[str]:
        """获取指定模型类型的API密钥"""
        if model_type in ["i2i", "t2i"]:
            # 豆包API模型
            return self.get_secret("doubao_api_key_env")
        elif model_type == "openai":
            # OpenAI模型
            return self.get_secret("openai_api_key_env")
        elif model_type == "stability":
            # Stability AI模型
            return self.get_secret("stability_api_key_env")
        elif model_type == "deepseek":
            # DeepSeek模型
            return self.get_secret("deepseek_api_key_env")
        else:
            return None
    
    def get_model_path(self, model_name):
        """获取模型路径"""
        if model_name in self.config["models"]:
            path = self.config["models"][model_name]["local_path"]
            # 处理相对路径
            if path.startswith("./"):
                path = path[2:]  # 移除 "./" 前缀
            return path
        return None
    
    def get_output_dir(self):
        """获取输出目录"""
        path = self.config["paths"]["output_dir"]
        if path.startswith("./"):
            path = path[2:]  # 移除 "./" 前缀
        return path
    
    def get_audio_path(self, filename):
        """获取音频文件路径"""
        input_dir = self.config["paths"]["input_dir"]
        if input_dir.startswith("./"):
            input_dir = input_dir[2:]  # 移除 "./" 前缀
        # 统一使用正斜杠路径
        return os.path.join(input_dir, filename).replace("\\", "/")
    
    def _validate_config(self):
        """验证配置有效性"""
        required_keys = ["paths", "models", "settings"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"配置文件缺少必需的键: {key}")
        
        # 验证路径配置
        paths = self.config.get("paths", {})
        for path_key in ["input_dir", "output_dir", "temp_dir", "models_cache"]:
            if path_key not in paths:
                raise ValueError(f"路径配置缺少必需的键: {path_key}")
        
        # 验证模型配置
        models = self.config.get("models", {})
        required_models = ["emotion2vec", "paraformer", "text_emotion"]
        for model_key in required_models:
            if model_key not in models:
                raise ValueError(f"模型配置缺少必需的键: {model_key}")
        
        # 验证图像模型配置
        image_models = self.config.get("image_models", {})
        required_image_models = ["i2i", "t2i"]
        for model_key in required_image_models:
            if model_key not in image_models:
                raise ValueError(f"图像模型配置缺少必需的键: {model_key}")
