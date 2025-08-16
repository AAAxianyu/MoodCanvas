"""
三阶段多模型情感分析服务
"""
import os
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from PIL import Image
from clip_interrogator import Config as CIConfig, Interrogator
import io

import logging
from datetime import datetime, timezone
import time
import base64
import requests

from src.models.emotion.text_emotion import TextEmotionModel
from src.models.emotion.audio_emotion import AudioEmotionModel
from src.models.image.image2image import ImageEditor
from src.models.image.text2image import ImageGenerator
from src.models.asr.paraformer import ParaformerModel
from src.utils.file_utils import save_upload_file

from src.core.config_manager import ConfigManager
from src.core.exceptions import EmotionAnalysisError, AudioProcessingError, GenerationError, ImageProcessingError, FileValidationError
from src.services.text_generator import TextGenerator
from src.utils.image_utils import validate_image_file

logger = logging.getLogger(__name__)

class MultiModelEmotionAnalyzer:
    """三阶段多模型情感分析系统"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.asr_model = None
        self.text_emotion_model = None
        self.audio_emotion_model = None
        self.setup_models()
    
    def setup_models(self):
        """初始化三个模型"""
        print("🚀 正在初始化三阶段情感分析模型...")
        use_local = self.config_manager.config.get("settings", {}).get("use_local_models", True)
        
        # 阶段1: Paraformer-zh ASR
        try:
            paraformer_config = self.config_manager.config.get("models", {}).get("paraformer", {})
            paraformer_config["use_local_models"] = use_local
            self.asr_model = ParaformerModel(paraformer_config)
            if self.asr_model.load_model():
                print("✅ 阶段1: Paraformer-zh ASR 模型加载成功")
            else:
                print("❌ 阶段1: Paraformer-zh ASR 模型加载失败")
        except Exception as e:
            print(f"❌ 阶段1: Paraformer-zh ASR 模型初始化失败: {e}")
            self.asr_model = None
        
        # 阶段2: 文本情感分类
        try:
            text_emotion_config = self.config_manager.config.get("models", {}).get("text_emotion", {})
            text_emotion_config["use_local_models"] = use_local
            self.text_emotion_model = TextEmotionModel(text_emotion_config)
            if self.text_emotion_model.load_model():
                print("✅ 阶段2: 文本情感分类模型加载成功")
            else:
                print("❌ 阶段2: 文本情感分类模型加载失败")
        except Exception as e:
            print(f"❌ 阶段2: 文本情感分类模型初始化失败: {e}")
            self.text_emotion_model = None
        
        # 阶段3: emotion2vec 声学情感分析
        try:
            audio_emotion_config = self.config_manager.config.get("models", {}).get("emotion2vec", {})
            audio_emotion_config["use_local_models"] = use_local
            self.audio_emotion_model = AudioEmotionModel(audio_emotion_config)
            if self.audio_emotion_model.load_model():
                print("✅ 阶段3: emotion2vec 声学情感分析模型加载成功")
            else:
                print("❌ 阶段3: emotion2vec 声学情感分析模型初始化失败")
        except Exception as e:
            print(f"❌ 阶段3: emotion2vec 声学情感分析模型初始化失败: {e}")
            self.audio_emotion_model = None

class EmotionAnalyzerService:
    EMOTION2VEC_LABELS = {0: "angry",1: "disgusted",2: "fearful",3: "happy",4: "neutral",5: "other",6: "sad",7: "surprised",8: "unknown"}
    TEXT_EMOTION_LABELS = {
        0: "admiration", 1: "amusement", 2: "anger", 3: "annoyance", 4: "approval",
        5: "caring", 6: "confusion", 7: "curiosity", 8: "desire", 9: "disappointment",
        10: "disapproval", 11: "disgust", 12: "embarrassment", 13: "excitement", 14: "fear",
        15: "gratitude", 16: "grief", 17: "joy", 18: "love", 19: "nervousness",
        20: "optimism", 21: "pride", 22: "realization", 23: "relief", 24: "remorse",
        25: "sadness", 26: "surprise", 27: "neutral"
    }

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.asr_model = None
        self.text_emotion_model = None
        self.audio_emotion_model = None
        self.image_generator = None
        self.image_editor = None
        self.text_generator = None
        self.setup_models()
    
    def setup_models(self):
        """初始化三个模型"""
        print("🚀 正在初始化三阶段情感分析模型...")
        use_local = self.config_manager.config.get("settings", {}).get("use_local_models", True)
        
        # 阶段1: Paraformer-zh ASR
        try:
            paraformer_config = self.config_manager.config.get("models", {}).get("paraformer", {})
            paraformer_config["use_local_models"] = use_local
            self.asr_model = ParaformerModel(paraformer_config)
            if self.asr_model.load_model():
                print("✅ 阶段1: Paraformer-zh ASR 模型加载成功")
            else:
                print("❌ 阶段1: Paraformer-zh ASR 模型加载失败")
        except Exception as e:
            print(f"❌ 阶段1: Paraformer-zh ASR 模型初始化失败: {e}")
            self.asr_model = None
        
        # 阶段2: 文本情感分类
        try:
            text_emotion_config = self.config_manager.config.get("models", {}).get("text_emotion", {})
            text_emotion_config["use_local_models"] = use_local
            self.text_emotion_model = TextEmotionModel(text_emotion_config)
            if self.text_emotion_model.load_model():
                print("✅ 阶段2: 文本情感分类模型加载成功")
            else:
                print("❌ 阶段2: 文本情感分类模型加载失败")
        except Exception as e:
            print(f"❌ 阶段2: 文本情感分类模型初始化失败: {e}")
            self.text_emotion_model = None
        
        # 阶段3: emotion2vec 声学情感分析
        try:
            audio_emotion_config = self.config_manager.config.get("models", {}).get("emotion2vec", {})
            audio_emotion_config["use_local_models"] = use_local
            self.audio_emotion_model = AudioEmotionModel(audio_emotion_config)
            if self.audio_emotion_model.load_model():
                print("✅ 阶段3: emotion2vec 声学情感分析模型加载成功")
            else:
                print("❌ 阶段3: emotion2vec 声学情感分析模型初始化失败")
        except Exception as e:
            print(f"❌ 阶段3: emotion2vec 声学情感分析模型初始化失败: {e}")
            self.audio_emotion_model = None

    def _load_models(self):
        try:
            if not self.text_emotion_model.load_model():
                logger.warning("文本情感分析模型加载失败")
            if not self.audio_emotion_model.load_model():
                logger.warning("音频情感分析模型加载失败")
            if not self.asr_model.load_model():
                logger.warning("ASR模型加载失败")
            logger.info("模型加载完成")
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
    
    async def process_text_service(self, text: str, language: str = "zh", style_preference: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        try:
            logger.info(f"开始处理文字情感分析，输入长度: {len(text)}")
            emotion_result = self.text_emotion_model.analyze(text)
            if not emotion_result:
                raise EmotionAnalysisError("文本情感分析失败，未获得有效结果")
            emotion_tags = self._extract_text_emotion_tags(emotion_result)
            confidence = self._extract_confidence(emotion_result)
            generated_text = await self._generate_text_with_llm(text, emotion_tags, style_preference, language)
            image_prompt = self._build_image_prompt(text, emotion_tags, generated_text)
            image_result = self.image_generator.generate(prompt=image_prompt, save_local=True)
            image_path = image_result['local_paths'][0] if image_result and image_result.get('local_paths') else None
            processing_time = time.time() - start_time
            result = {
                'text': text,
                'emotion_tags': emotion_tags,
                'emotion_confidence': confidence,
                'generated_content': {'text': generated_text, 'image_path': image_path, 'style': style_preference or 'default', 'metadata': {'language': language,'style_preference': style_preference,'generation_timestamp': datetime.utcnow().isoformat()}},
                'processing_time': round(processing_time, 3),
                'status': 'success'
            }
            return result
        except Exception as e:
            logger.error(f"文字处理服务失败: {str(e)}", exc_info=True)
            raise EmotionAnalysisError(f"文字处理失败: {str(e)}")
    
    async def process_audio_service(self, audio_data: bytes, language: str = "zh", enable_dual_analysis: bool = True, fusion_strategy: str = "weighted") -> Dict[str, Any]:
        start_time = time.time()
        temp_audio_path = None
        try:
            temp_audio_path = self._save_temp_audio(audio_data)
            transcribed_text = self.asr_model.transcribe(temp_audio_path)
            if not transcribed_text:
                raise AudioProcessingError("语音识别失败")
            audio_emotion_result = self.audio_emotion_model.analyze(temp_audio_path)
            audio_emotion_tags = self._extract_audio_emotion_tags(audio_emotion_result)
            text_emotion_result = self.text_emotion_model.analyze(transcribed_text)
            text_emotion_tags = self._extract_text_emotion_tags(text_emotion_result)
            merged_emotion = self._fuse_emotions(audio_emotion_tags, text_emotion_tags, fusion_strategy)
            generated_text = await self._generate_text_with_llm(transcribed_text, merged_emotion, None, language)
            image_prompt = self._build_image_prompt(transcribed_text, merged_emotion, generated_text)
            image_result = self.image_generator.generate(prompt=image_prompt, save_local=True)
            image_path = image_result['local_paths'][0] if image_result and image_result.get('local_paths') else None
            processing_time = time.time() - start_time
            result = {
                'transcribed_text': transcribed_text,
                'emotion_analysis': {'audio_emotion': audio_emotion_tags,'text_emotion': text_emotion_tags,'merged_emotion': merged_emotion,'fusion_rules': fusion_strategy},
                'generated_content': {'text': generated_text,'image_path': image_path,'style': 'default','metadata': {'language': language,'dual_analysis': enable_dual_analysis,'fusion_strategy': fusion_strategy,'generation_timestamp': datetime.utcnow().isoformat()}},
                'processing_time': round(processing_time, 3),
                'status': 'success'
            }
            return result
        except Exception as e:
            logger.error(f"音频处理服务失败: {str(e)}", exc_info=True)
            raise AudioProcessingError(f"音频处理失败: {str(e)}")
        finally:
            if temp_audio_path and os.path.exists(temp_audio_path):
                self._cleanup_temp_file(temp_audio_path)

    def _extract_audio_emotion_tags(self, emotion_result: List[Dict[str, Any]]) -> List[str]:
        tags = []
        try:
            for item in emotion_result:
                if isinstance(item, dict) and 'raw_result' in item:
                    raw = item['raw_result']
                    if isinstance(raw, dict):
                        if 'emotion' in raw:
                            emotion_id = raw['emotion']
                            if isinstance(emotion_id, int) and emotion_id in self.EMOTION2VEC_LABELS:
                                tags.append(self.EMOTION2VEC_LABELS[emotion_id])
                        elif 'emotions' in raw:
                            emotions = raw['emotions']
                            if isinstance(emotions, list):
                                for emotion in emotions[:3]:
                                    if isinstance(emotion, dict) and 'emotion' in emotion:
                                        emotion_id = emotion['emotion']
                                        if isinstance(emotion_id, int) and emotion_id in self.EMOTION2VEC_LABELS:
                                            tags.append(self.EMOTION2VEC_LABELS[emotion_id])
        except Exception as e:
            logger.warning(f"提取音频情感标签失败: {str(e)}")
        return tags[:3] if tags else ['neutral']

    def _extract_text_emotion_tags(self, emotion_result: List[Dict[str, Any]]) -> List[str]:
        tags = []
        try:
            for item in emotion_result:
                if isinstance(item, dict):
                    if 'label' in item:
                        label = item['label']
                        if label in self.TEXT_EMOTION_LABELS.values():
                            tags.append(label)
                    elif 'emotion' in item:
                        emotion = item['emotion']
                        if emotion in self.TEXT_EMOTION_LABELS.values():
                            tags.append(emotion)
        except Exception as e:
            logger.warning(f"提取文本情感标签失败: {str(e)}")
        return tags[:3] if tags else ['neutral']

    def _extract_confidence(self, emotion_result: List[Dict[str, Any]]) -> float:
        try:
            for item in emotion_result:
                if isinstance(item, dict) and 'score' in item:
                    return float(item['score'])
        except Exception:
            pass
        return 0.8

    def _build_image_prompt(self, text: str, emotion_tags: List[str], generated_text: str) -> str:
        emotion_desc = ", ".join(emotion_tags)
        return f"基于文字'{text}'和情感'{emotion_desc}'，生成与文案'{generated_text}'相匹配的图片"

    def _fuse_emotions(self, audio_emotions: List[str], text_emotions: List[str], strategy: str) -> List[str]:
        if strategy == "max":
            return audio_emotions if len(audio_emotions) > len(text_emotions) else text_emotions
        elif strategy == "average":
            intersection = set(audio_emotions) & set(text_emotions)
            if intersection:
                return list(intersection)
            else:
                return list(set(audio_emotions + text_emotions))
        else:  # weighted
            all_emotions = audio_emotions + text_emotions
            emotion_count = {}
            for emotion in all_emotions:
                if emotion in audio_emotions and emotion in text_emotions:
                    emotion_count[emotion] = emotion_count.get(emotion, 0) + 2
                else:
                    emotion_count[emotion] = emotion_count.get(emotion, 0) + 1
            sorted_emotions = sorted(emotion_count.items(), key=lambda x: x[1], reverse=True)
            return [emotion for emotion, _ in sorted_emotions[:3]]
    async def _generate_text_with_llm(self, text: str, emotion_tags: List[str], style: Optional[str], language: str) -> str:
        emotion_desc = ", ".join(emotion_tags)
        style_desc = f"风格：{style}" if style else ""
        return f"基于您的情感'{emotion_desc}'，我为'{text}'创作了这段文案：在{emotion_desc}的旋律中，{text}仿佛有了新的生命..."

    def _save_temp_audio(self, audio_data: bytes) -> str:
        import tempfile
        temp_dir = "data/temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, suffix=".wav", delete=False)
        temp_file.write(audio_data)
        temp_file.close()
        return temp_file.name

    def _cleanup_temp_file(self, file_path: str):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"临时文件已清理: {file_path}")
        except Exception as e:
            logger.warning(f"清理临时文件失败: {str(e)}")

    async def run_three_stage_analysis(self, audio_path: str) -> Dict[str, Any]:
        """运行三阶段情感分析"""
        start_time = time.time()
        try:
            # 阶段1: ASR转录
            if not self.asr_model:
                raise AudioProcessingError("ASR模型未初始化")
            
            transcribed_text = self.asr_model.transcribe(audio_path)
            if not transcribed_text:
                raise AudioProcessingError("语音识别失败")
            
            # 阶段2: 文本情感分析
            if not self.text_emotion_model:
                raise EmotionAnalysisError("文本情感分析模型未初始化")
            
            text_emotion_result = self.text_emotion_model.analyze(transcribed_text)
            text_emotion_tags = self._extract_text_emotion_tags(text_emotion_result)
            
            # 阶段3: 音频情感分析
            if not self.audio_emotion_model:
                raise EmotionAnalysisError("音频情感分析模型未初始化")
            
            audio_emotion_result = self.audio_emotion_model.analyze(audio_path)
            audio_emotion_tags = self._extract_audio_emotion_tags(audio_emotion_result)
            
            # 融合情感标签
            merged_emotion = self._fuse_emotions(audio_emotion_tags, text_emotion_tags, "weighted")
            
            # 生成文案和图片
            generated_content = await self._generate_content(transcribed_text, merged_emotion)
            
            processing_time = time.time() - start_time
            
            return {
                'transcribed_text': transcribed_text,
                'emotion_analysis': {
                    'audio_emotion': audio_emotion_tags,
                    'text_emotion': text_emotion_tags,
                    'merged_emotion': merged_emotion,
                    'fusion_strategy': 'weighted'
                },
                'generated_content': generated_content,
                'processing_time': round(processing_time, 3),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"三阶段情感分析失败: {str(e)}", exc_info=True)
            raise EmotionAnalysisError(f"情感分析失败: {str(e)}")

    async def run_text_emotion_analysis(self, text: str) -> Dict[str, Any]:
        """运行纯文本情感分析"""
        start_time = time.time()
        try:
            # 文本情感分析
            if not self.text_emotion_model:
                raise EmotionAnalysisError("文本情感分析模型未初始化")
            
            text_emotion_result = self.text_emotion_model.analyze(text)
            text_emotion_tags = self._extract_text_emotion_tags(text_emotion_result)
            
            # 生成文案和图片
            generated_content = await self._generate_content(text, text_emotion_tags)
            
            processing_time = time.time() - start_time
            
            return {
                'input_text': text,
                'emotion_analysis': {
                    'text_emotion': text_emotion_tags,
                    'confidence': self._extract_confidence(text_emotion_result)
                },
                'generated_content': generated_content,
                'processing_time': round(processing_time, 3),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"文本情感分析失败: {str(e)}", exc_info=True)
            raise EmotionAnalysisError(f"文本情感分析失败: {str(e)}")

    async def _generate_content(self, text: str, emotion_tags: List[str]) -> Dict[str, Any]:
        """生成文案和图片内容"""
        try:
            # 生成文案
            generated_text = ""
            if self.text_generator:
                try:
                    generated_text = await self.text_generator.generate_text(text, emotion_tags)
                except Exception as e:
                    logger.warning(f"文案生成失败: {e}")
                    generated_text = f"基于'{text}'的情感'{', '.join(emotion_tags)}'，我为您创作了这段文案：在{', '.join(emotion_tags)}的旋律中，{text}仿佛有了新的生命..."
            else:
                generated_text = f"基于'{text}'的情感'{', '.join(emotion_tags)}'，我为您创作了这段文案：在{', '.join(emotion_tags)}的旋律中，{text}仿佛有了新的生命..."
            
            # 生成图片
            image_path = None
            if self.image_generator:
                try:
                    image_prompt = self._build_image_prompt(text, emotion_tags, generated_text)
                    image_result = self.image_generator.generate(prompt=image_prompt, save_local=True)
                    image_path = image_result['local_paths'][0] if image_result and image_result.get('local_paths') else None
                except Exception as e:
                    logger.warning(f"图片生成失败: {e}")
            
            return {
                'text': generated_text,
                'image_path': image_path,
                'style': 'default',
                'metadata': {
                    'generation_timestamp': datetime.now(timezone.utc).isoformat(),
                    'emotion_tags': emotion_tags
                }
            }
            
        except Exception as e:
            logger.error(f"内容生成失败: {str(e)}")
            return {
                'text': f"基于'{text}'的情感分析结果生成文案失败",
                'image_path': None,
                'style': 'default',
                'metadata': {
                    'generation_timestamp': datetime.now(timezone.utc).isoformat(),
                    'emotion_tags': emotion_tags,
                    'error': str(e)
                }
            }




class DoubaoVLMClient:
    """
    轻量 HTTP 客户端：调用豆包多模态 chat/completions 接口做图像理解
    - 读取 ConfigManager 里的 vlm 配置（base_url/api_key_env/model_name）
    - 返回结构化 JSON（caption/objects/styles/suggestions/edit_prompt/negative_prompt）
    """

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.provider: str = "doubao"
        self.model: str = "doubao-1.5-vision-lite-250315"
        self.base_url: str = ""
        self.api_key: Optional[str] = None
        self.completions_url: str = ""
        self._setup_client()

    def _setup_client(self) -> None:
        """对齐式初始化：从 config_manager 读取配置并完成必需字段准备"""
        try:
            models_cfg = (self.config_manager.config or {}).get("image_models", {}) or {}
            vlm_cfg = models_cfg.get("vlm", {}) or {}


            # use_api 关掉就直接拒绝
            if vlm_cfg.get("use_api", True) is not True:
                raise RuntimeError("DoubaoVLMClient: 当前配置未启用 VLM API（models.vlm.use_api != true）")

            # 2) 基本字段
            self.provider = vlm_cfg.get("provider", "doubao")
            self.model = vlm_cfg.get("model_name", "doubao-1.5-vision-lite-250315")

            api_conf = vlm_cfg.get("api", {}) or {}
            base_url_raw = api_conf.get("base_url", "")
            if not base_url_raw:
                raise RuntimeError("DoubaoVLMClient: 缺少 models.vlm.api.base_url")

            self.base_url = base_url_raw.rstrip("/")

            # 3) API Key：优先环境变量，其次支持在配置中直填
            key_env = api_conf.get("api_key_env", "ARK_API_KEY")
            self.api_key = os.getenv(key_env) or api_conf.get("api_key")
            if not self.api_key:
                raise RuntimeError(
                    f"DoubaoVLMClient: 未找到 API Key，请设置环境变量 {key_env} 或在 models.vlm.api.api_key 中直填"
                )

            # 4) 终端点（OpenAI 兼容）
            self.completions_url = f"{self.base_url}/chat/completions"
            logger.info("DoubaoVLMClient 初始化完成: provider=%s, model=%s, base_url=%s", self.provider, self.model, self.base_url)

        except Exception as e:
            logger.error("DoubaoVLMClient 初始化失败: %s", e, exc_info=True)
            raise
    
    @staticmethod
    def _guess_mime(image_bytes: bytes) -> Tuple[str, str]:
        """简单判断 mime（便于多模态上传）"""
        try:
            with Image.open(io.BytesIO(image_bytes)) as im:
                fmt = (im.format or "PNG").upper()
                if fmt == "JPG":
                    fmt = "JPEG"
                mime = f"image/{fmt.lower()}"
                ext = fmt.lower()
                return mime, ext
        except Exception:
            return "image/png", "png"


    def analyze_image(
        self,
        image_bytes: bytes,
        intent: str = "enhance",           # 例如 enhance / replace_bg / recolor ...
        style_preset: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        让模型“看图+给编辑建议+生成编辑 prompt”。要求模型输出 JSON。
        返回字段：
          caption / objects / styles / colors / suggestions / edit_prompt / negative_prompt
        """
        # 准备图片（base64）
        mime, ext = DoubaoVLMClient._guess_mime(image_bytes)
        b64 = base64.b64encode(image_bytes).decode("utf-8")

        system_prompt = (
            "你是资深视觉设计师和修图指导，擅长从图片中提取关键信息并生成适合图像编辑模型的指令。\n"
            "严格以 JSON 返回，键包括：caption, objects, styles, colors, suggestions, edit_prompt, negative_prompt。"
        )
        user_instruction = (
            f"请分析这张图片，任务意图：{intent}；"
            f"风格预设（可选）：{style_preset or '无'}。"
            "要求：\n"
            "1) caption：一句话描述图片主体与场景；\n"
            "2) objects：最多5个关键对象及其属性（名称/颜色/材质/可见特征）；\n"
            "3) styles：提取3~6个风格标签（如 cinematic、neon、portrait 等）；\n"
            "4) colors：2~5个主色；\n"
            "5) suggestions：3条可执行的编辑建议（面向 i2i 模型）；\n"
            "6) edit_prompt：综合以上信息，生成可直接用于图像编辑模型的英文指令（描述清晰、避免主观词、包含光照/质感/层次等）；\n"
            "7) negative_prompt：常见伪影/不期望效果。\n"
            "只输出 JSON，不要额外解释。"
        )

        data_url = f"data:{mime};base64,{b64}"

        # 按 OpenAI 多模态风格组织消息（豆包 ark v3 基本兼容；如有差异仅需微调字段名）
        messages = [
        # system 建议直接用纯字符串，更兼容
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": data_url}},
            {"type": "text", "text": user_instruction}
        ]}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "response_format": {"type": "json_object"}  # 要求走 JSON
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            resp = requests.post(self.completions_url, headers=headers, data=json.dumps(payload), timeout=60)
            resp.raise_for_status()
            data = resp.json()
            # 适配常见返回：choices[0].message.content
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            result = json.loads(content) if content else {}
            # 基本兜底
            result.setdefault("caption", "")
            result.setdefault("objects", [])
            result.setdefault("styles", [])
            result.setdefault("colors", [])
            result.setdefault("suggestions", [])
            result.setdefault("edit_prompt", result.get("caption", ""))
            result.setdefault("negative_prompt", "low-res, blurry, artifacts, oversaturated, watermark")
            return result
        except Exception as e:
            logger.error(f"DoubaoVLMClient.analyze_image 失败: {e}", exc_info=True)
            raise ImageProcessingError(f"豆包多模态分析失败: {e}")




class ImageEmotionAnalyzerService:
    """
    改造版：使用豆包 VLM 做图像理解 + 产出编辑 prompt；
    然后可选直接调用 Doubao i2i（通过你的 ImageEditor 适配器）做修图。
    """

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.vlm = None           # DoubaoVLMClient
        self.image_editor = None  # 你已有的 i2i 模型适配器
        self.defaults: Dict[str, Any] = {}
        self._setup()

    def _setup(self):
        conf = self.config_manager.config.get("models", {}).get("vlm", {})
        if not conf.get("use_api", True):
            raise RuntimeError("当前配置未启用 VLM API")
        
        self.vlm = DoubaoVLMClient(self.config_manager)

        # 读取 i2i 默认值（走你已有的 doubao i2i 模型）
        img_defaults = conf.get("defaults", {})
        self.defaults = {
            "guidance_scale": float(img_defaults.get("guidance_scale", 7.5)),
            "num_images": int(img_defaults.get("num_images", 1)),
            "size": img_defaults.get("size", "1024x1024"),
            "watermark": bool(img_defaults.get("watermark", True)),
            "save_local": True,
        }
        # 你的 ImageEditor 已经集成豆包 i2i：直接初始化即可
        self.image_editor = ImageEditor(self.config_manager)
        logger.info("ImageEmotionAnalyzer(Doubao) 初始化完成")

    # ========== 对外 API ==========

    def analyze_image_bytes(
        self,
        image_bytes: bytes,
        intent: str = "enhance",
        style_preset: Optional[str] = None,
        auto_edit: bool = False
    ) -> Dict[str, Any]:
        """bytes 入口：返回分析结果；可选直接自动修图。"""
        if not validate_image_file(image_bytes):
            raise FileValidationError("无效的图片文件")
        # 分析
        analysis = self.vlm.analyze_image(image_bytes, intent=intent, style_preset=style_preset)

        result: Dict[str, Any] = {
            "analysis": analysis,  # caption/objects/styles/colors/suggestions/...
            "status": "ok"
        }

        if auto_edit:
            # 将原图先落盘到 temp，便于 i2i 调用
            temp_dir = self.config_manager.config.get("paths", {}).get("temp_dir", "data/temp")
            os.makedirs(temp_dir, exist_ok=True)
            tmp_path = os.path.join(temp_dir, "i2i_input.png")
            save_upload_file(image_bytes, tmp_path)

            edit_prompt = analysis.get("edit_prompt") or analysis.get("caption") or ""
            neg = analysis.get("negative_prompt", "")
            # 组装 i2i 参数（你 ImageEditor 的 edit_image(...) 可能有不同签名，这里按你之前示例改）
            params = {
                "input_path_or_url": tmp_path,
                "prompt": edit_prompt,
                "negative_prompt": neg,
                "guidance_scale": self.defaults["guidance_scale"],
                "save_local": True
            }
            try:
                out = self.image_editor.edit_image(**params)
                result["auto_edit"] = {
                    "prompt": edit_prompt,
                    "negative_prompt": neg,
                    "output": out
                }
            except Exception as e:
                logger.warning(f"自动修图失败: {e}")
                result["auto_edit"] = {"error": str(e)}
        return result

    def analyze_image_path(
        self,
        image_path: str,
        intent: str = "enhance",
        style_preset: Optional[str] = None,
        auto_edit: bool = False
    ) -> Dict[str, Any]:
        """文件路径入口：读取为 bytes 后复用逻辑"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(image_path)
        with open(image_path, "rb") as f:
            return self.analyze_image_bytes(
                f.read(),
                intent=intent,
                style_preset=style_preset,
                auto_edit=auto_edit
            )



        """
        图片内容：{image_content},
        当前情感：{}，
        none
        修改意见：你是一个小红书xxxxx
        """
# class ImageEmotionAnalyzer:

#     def __init__(self, config_manager: ConfigManager):
#         self.config_manager = config_manager
#         self.vlm_model: Optional[Interrogator] = None
#         self.vlm_cfg: Optional[CIConfig] = None
#         self.setup_models()

#     # ---------------------------
#     # 初始化与模型装载
#     # ---------------------------
#     def setup_models(self):
#         """初始化 clip_interrogator"""
#         print("🚀 正在初始化 Image → Prompt 分析器（clip_interrogator）...")
#         try:
#             ci_conf = self._build_ci_config()
#             self.vlm_cfg = ci_conf
#             self.vlm_model = Interrogator(ci_conf)
#             # 轻量 VRAM 优化（可选）
#             if self._get_bool("apply_low_vram_defaults", default=True):
#                 self.vlm_model.config.apply_low_vram_defaults()

#             print(f"✅ clip_interrogator 加载成功，CLIP: {self.vlm_model.config.clip_model_name}")
#         except Exception as e:
#             print(f"❌ clip_interrogator 初始化失败: {e}")
#             logger.exception("clip_interrogator 初始化失败")
#             self.vlm_model = None

#     def _build_ci_config(self) -> CIConfig:
#         """
#         从项目配置构建 clip_interrogator 的 Config
#         期望的配置示例：
#         {
#           "models": {
#             "clip_interrogator": {
#               "clip_model_name": "ViT-L-14/openai",
#               "blip_model": "blip-base",     # 可不填
#               "cache_path": "./data/ci_cache",
#               "device": "cuda:0",            # 或 "cpu"
#               "chunk_size": 2048
#             }
#           },
#           "settings": {
#             "use_local_models": True,
#             "apply_low_vram_defaults": True
#           }
#         }
#         """
#         ci_cfg = self.config_manager.config.get("models", {}).get("clip_interrogator", {})
#         clip_model_name = ci_cfg.get("clip_model_name", "ViT-L-14/openai")
#         cache_path = ci_cfg.get("cache_path")  # None = 默认
#         device = ci_cfg.get("device")          # None = 自动
#         chunk_size = ci_cfg.get("chunk_size")  # None = 默认

#         conf = CIConfig(clip_model_name=clip_model_name)
#         if cache_path:
#             conf.cache_path = cache_path
#         if device:
#             conf.device = device
#         if chunk_size:
#             conf.chunk_size = int(chunk_size)
#         # 其余可根据需要继续映射（例如: blip_model 等）
#         return conf

#     def _get_bool(self, key: str, default: bool) -> bool:
#         return bool(self.config_manager.config.get("settings", {}).get(key, default))

#     # # ---------------------------
#     # # 对外主接口
#     # # ---------------------------
#     # def analyze_image_bytes(
#     #     self,
#     #     image_bytes: bytes,
#     #     intent: str = "enhance",
#     #     style_preset: Optional[str] = None,
#     #     need_negative: bool = True,
#     # ) -> Dict[str, Any]:
#     #     """
#     #     输入：原始图像 bytes
#     #     输出：可直接用于 T2I / I2I 的 prompt 及结构化信息
#     #     """
#     #     if not self.vlm_model:
#     #         raise ImageProcessingError("clip_interrogator 未初始化")

#     #     if not validate_image_file(image_bytes):
#     #         raise FileValidationError("无效的图片文件格式")

#     #     try:
#     #         img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#     #         return self._analyze_pil_image(
#     #             img,
#     #             intent=intent,
#     #             style_preset=style_preset,
#     #             need_negative=need_negative,
#     #         )
#     #     except Exception as e:
#     #         logger.exception("analyze_image_bytes 失败")
#     #         raise ImageProcessingError(f"图像分析失败: {e}")

#     def analyze_image_path(
#         self,
#         image_path: str,
#         intent: str = "enhance",
#         style_preset: Optional[str] = None,
#         need_negative: bool = True,
#     ) -> Dict[str, Any]:
#         """输入：图片路径"""
#         if not self.vlm_model:
#             raise ImageProcessingError("clip_interrogator 未初始化")
#         try:
#             img = Image.open(image_path).convert("RGB")
#             return self._analyze_pil_image(
#                 img,
#                 intent=intent,
#                 style_preset=style_preset,
#                 need_negative=need_negative,
#             )
#         except Exception as e:
#             logger.exception("analyze_image_path 失败")
#             raise ImageProcessingError(f"图像分析失败: {e}")

#     # ---------------------------
#     # 内部：核心分析与 Prompt 组装
#     # ---------------------------
#     def _analyze_pil_image(
#         self,
#         img: Image.Image,
#         intent: str,
#         style_preset: Optional[str],
#         need_negative: bool,
#     ) -> Dict[str, Any]:
#         """
#         用 CI 生成基础描述，再拼成适合编辑/生成的 prompt（可直接接你的 ImageService）
#         """
#         # 1) 基础描述（CI 的一句话 prompt）
#         ci_prompt = (self.vlm_model.generate_caption(img)
#              if hasattr(self.vlm_model, "generate_caption")
#              else self.vlm_model.caption(img))
        
#         # 2) 额外信号（可选：tags / 强风格词；这里用简单启发式）
#         tags = self._extract_style_tags(ci_prompt)

#         # 3) 组装最终可用 prompt
#         prompt, negative = self._compose_prompt(
#             base_caption=ci_prompt,
#             intent=intent,
#             style_preset=style_preset,
#             tags=tags,
#             need_negative=need_negative,
#         )

#         result: Dict[str, Any] = {
#             "prompt": prompt,
#             "negative_prompt": negative if need_negative else "",
#             "meta": {
#                 "caption": ci_prompt,
#                 "tags": tags,
#                 "intent": intent,
#                 "style_preset": style_preset,
#                 "model_info": self.get_model_info(),
#             }
#         }
#         return result

#     @staticmethod
#     def _extract_style_tags(ci_prompt: str) -> List[str]:
#         """
#         非严格：基于关键字的轻量风格词抽取
#         你也可以维护一个词典/正则或把这一步交给更强的文本模型做清洗
#         """
#         vocab = {
#             "cinematic": ["cinematic", "film", "movie", "anamorphic"],
#             "vintage": ["vintage", "retro", "film grain"],
#             "neon": ["neon", "cyberpunk", "glow"],
#             "portrait": ["portrait", "headshot", "bokeh"],
#             "macro": ["macro", "close-up"],
#             "studio": ["studio", "softbox", "rim light", "key light"],
#             "fantasy": ["fantasy", "mythical", "epic"],
#             "watercolor": ["watercolor", "ink", "gouache"],
#             "3d": ["3d", "render", "octane", "unreal"],
#         }
#         tags: List[str] = []
#         low = ci_prompt.lower()
#         for tag, kws in vocab.items():
#             if any(k in low for k in kws):
#                 tags.append(tag)
#         return tags[:6]

#     @staticmethod
#     def _compose_prompt(
#         base_caption: str,
#         intent: str,
#         style_preset: Optional[str],
#         tags: List[str],
#         need_negative: bool,
#     ) -> Tuple[str, str]:
#         """
#         最终 prompt 组合策略（尽量“即插即用”）
#         - base_caption：CI 产出的描述
#         - intent：对齐你的业务目标，如 enhance / replace_bg / recolor / upstyle / anime 等
#         - style_preset：外部传入风格预设（覆盖或追加）
#         """
#         parts: List[str] = [base_caption.strip()]

#         # 根据意图补一些常用的“编辑友好修饰词”
#         intent_snippets = {
#             "enhance": "high detail, natural lighting, realistic shading, finely textured",
#             "replace_bg": "clean subject separation, seamless background blending, consistent lighting",
#             "recolor": "color-consistent, natural hue transitions, texture preserved",
#             "anime": "anime style, clean lines, vibrant colors, high contrast",
#             "sketch": "pencil sketch, cross-hatching, monochrome shading",
#         }
#         if intent in intent_snippets:
#             parts.append(intent_snippets[intent])

#         # 标签词
#         if tags:
#             parts.append(", ".join(tags))

#         # 风格预设
#         if style_preset:
#             parts.append(style_preset)

#         prompt = ", ".join([p for p in parts if p])

#         # Negative prompt（按需）
#         negative = ""
#         if need_negative:
#             negative = (
#                 "low-res, blurry, artifacts, overexposed, oversaturated, "
#                 "extra limbs, duplicated objects, distorted proportions, watermark, text artifacts"
#             )
#         return prompt, negative

#     # ---------------------------
#     # 辅助：模型信息
#     # ---------------------------
#     def get_model_info(self) -> Dict[str, Any]:
#         clip_name = self.vlm_cfg.clip_model_name if self.vlm_cfg else "unknown"
#         device = getattr(self.vlm_cfg, "device", "auto") if self.vlm_cfg else "auto"
#         return {
#             "backend": "clip_interrogator",
#             "clip_model": clip_name,
#             "device": device,
#         }

    