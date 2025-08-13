import os
import json


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.load_config()
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
            "paths": {
                "input_dir": "input",
                "output_dir": "outputs",
                "temp_dir": "temp_outputs",
                "models_cache": "./models_cache"
            },
            "models": {
                "emotion2vec": {
                    "name": "iic/emotion2vec_plus_large",
                    "type": "funasr",
                    "local_path": "emotion2vec_plus_large"
                },
                "paraformer": {
                    "name": "paraformer-zh",
                    "type": "funasr",
                    "local_path": "paraformer-zh"
                },
                "text_emotion": {
                    "name": "distilbert-base-uncased-go-emotions-student",
                    "type": "transformers",
                    "local_path": "distilbert-base-uncased-go-emotions-student"
                }
            },
            "image_models": {
                "i2i": {
                    "model_name": "doubao-seedit-3.0-i2i",
                    "use_local": True,

                }
            },
            "settings": {
                "use_local_models": True,
                "download_to_project": True
            },
            "audio_files": {
                "default": "asr_example.wav",
                "available": ["asr_example.wav", "example.wav"]
            }
        }
    
    def setup_environment(self):
        """设置环境变量"""
        cache_dir = self.config["paths"]["models_cache"]
        os.environ['HF_HOME'] = cache_dir
        os.environ['MODELSCOPE_CACHE'] = cache_dir
    
    def get_model_path(self, model_name):
        """获取模型路径"""
        if model_name in self.config["models"]:
            return self.config["models"][model_name]["local_path"]
        return None
    
    def get_output_dir(self):
        """获取输出目录"""
        return self.config["paths"]["output_dir"]
    
    def get_audio_path(self, filename):
        """获取音频文件路径"""
        input_dir = self.config["paths"]["input_dir"]
        return os.path.join(input_dir, filename)
    
    def _ensure_dirs(self):
        """确保必要的目录存在"""
        for k in ("input_dir", "output_dir", "temp_dir", "models_cache", "generated_images_dir"):
            d = self.config["paths"].get(k)
            if d and not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
    
    def get_generated_images_dir(self):
        return self.config["paths"].get("generated_images_dir", "generated_images")
    
    def get_image_cfg(self, key="i2i"):
        return self.config.get("image_models", {}).get(key, {})

    def get_secret(self, name="doubao_api_key_env"):
        env_name = self.config.get("secrets", {}).get(name)
        return os.environ.get(env_name) if env_name else None
