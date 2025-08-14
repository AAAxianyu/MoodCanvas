"""
文本情感分析模型
"""
import os
from typing import List, Dict, Any
from src.models.emotion.base import BaseEmotionModel
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

class TextEmotionModel(BaseEmotionModel):
    """文本情感分析模型"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "text_emotion"
        self.model_path = config.get("local_path")
        self.use_local = config.get("use_local_models", True)
        self.tokenizer = None
        self.model = None
        self.pipeline = None

    def load_model(self) -> bool:
        """加载文本情感分析模型"""
        try:
            if self.use_local and self.model_path:
                # 使用本地模型
                model_abs_path = os.path.abspath(self.model_path)
                self.tokenizer = AutoTokenizer.from_pretrained(model_abs_path)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_abs_path)
            else:
                # 使用在线模型
                model_name = "uer/roberta-base-finetuned-jd-binary-chinese"
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

            # 创建pipeline
            self.pipeline = pipeline(
                "text-classification",
                model=self.model,
                tokenizer=self.tokenizer
            )

            self.is_loaded = True
            return True
        except Exception as e:
            print(f"文本情感分析模型加载失败: {e}")
            return False

    def analyze(self, text: str) -> List[Dict[str, Any]]:
        """分析文本情感"""
        if not self.is_model_ready():
            if not self.load_model():
                return []

        try:
            result = self.pipeline(text)
            
            # 标准化输出格式
            if isinstance(result, list):
                return result
            elif isinstance(result, dict):
                return [result]
            else:
                return []
        except Exception as e:
            print(f"文本情感分析失败: {e}")
            return []
