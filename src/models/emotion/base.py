"""
情感分析模型基类
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pathlib import Path

class BaseEmotionModel(ABC):
    """情感分析模型基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None
        self.is_loaded = False
    
    @abstractmethod
    def load_model(self) -> bool:
        """加载模型"""
        pass
    
    @abstractmethod
    def analyze(self, input_data: Any) -> List[Dict[str, Any]]:
        """分析情感"""
        pass
    
    def is_model_ready(self) -> bool:
        """检查模型是否已加载"""
        return self.is_loaded
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "type": "emotion",
            "loaded": self.is_loaded,
            "config": self.config
        }
