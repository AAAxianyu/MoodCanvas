"""
音频情感分析模型
"""
import os
from typing import List, Dict, Any
from src.models.emotion.base import BaseEmotionModel
from funasr import AutoModel

class AudioEmotionModel(BaseEmotionModel):
    """emotion2vec音频情感分析模型"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "emotion2vec"
        self.model_path = config.get("local_path")
        self.use_local = config.get("use_local_models", True)
    
    def load_model(self) -> bool:
        """加载emotion2vec模型"""
        try:
            if self.use_local and self.model_path:
                # 使用本地模型
                model_abs_path = os.path.abspath(self.model_path)
                self.model = AutoModel(model=model_abs_path)
            else:
                # 使用在线模型
                self.model = AutoModel(model="iic/emotion2vec_plus_large")
            
            self.is_loaded = True
            return True
        except Exception as e:
            print(f"emotion2vec模型加载失败: {e}")
            return False
    
    def analyze(self, audio_path: str) -> List[Dict[str, Any]]:
        """分析音频情感"""
        if not self.is_model_ready():
            if not self.load_model():
                return []
        
        try:
            result = self.model.generate(
                audio_path,
                output_dir="./data/temp",
                granularity="utterance",
                extract_embedding=False
            )
            
            # 返回原始结果，让调用者处理
            return [{"raw_result": result}] if result else []
        except Exception as e:
            print(f"音频情感分析失败: {e}")
            return []
