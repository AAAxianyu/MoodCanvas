"""
Paraformer ASR模型实现
"""
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.asr.base import BaseASRModel
from funasr import AutoModel

class ParaformerModel(BaseASRModel):
    """Paraformer-zh ASR模型"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "paraformer"
        self.model_path = config.get("local_path")
        self.use_local = config.get("use_local_models", True)
    
    def load_model(self) -> bool:
        """加载Paraformer模型"""
        try:
            if self.use_local and self.model_path:
                # 使用本地模型
                model_abs_path = os.path.abspath(self.model_path)
                self.model = AutoModel(model=model_abs_path)
            else:
                # 使用在线模型
                self.model = AutoModel(
                    model="iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"
                )
            
            self.is_loaded = True
            return True
        except Exception as e:
            print(f"Paraformer模型加载失败: {e}")
            return False
    
    def transcribe(self, audio_path: str) -> Optional[str]:
        """转录音频文件"""
        if not self.is_model_ready():
            if not self.load_model():
                return None
        
        try:
            result = self.model.generate(
                audio_path,
                output_dir="./data/temp",
                batch_size=1
            )
            
            if result and len(result) > 0:
                transcription = result[0].get('text', '').strip()
                return transcription if transcription else None
            
            return None
        except Exception as e:
            print(f"ASR转录失败: {e}")
            return None
