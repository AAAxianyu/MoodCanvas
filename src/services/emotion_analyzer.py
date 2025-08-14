"""
三阶段多模型情感分析服务
"""
import os
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import time
import logging

from src.models.emotion.text_emotion import TextEmotionModel
from src.models.emotion.audio_emotion import AudioEmotionModel
from src.models.asr.paraformer import ParaformerModel
from src.models.image.text2image import ImageGenerator
from src.models.image.image2image import ImageEditor
from src.core.config_manager import ConfigManager
from src.core.exceptions import EmotionAnalysisError, AudioProcessingError, GenerationError
from src.services.text_generator import TextGenerator

logger = logging.getLogger(__name__)

class MultiModelEmotionAnalyzer:
    """三阶段多模型情感分析系统"""
    
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
        self.image_generator = ImageGenerator(config_manager)
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
            
            # 优先使用model_id，如果没有则使用name
            model_id = paraformer_config.get("model_id", paraformer_config.get("name"))
            if model_id:
                paraformer_config["model_id"] = model_id
            
            self.asr_model = ParaformerModel(paraformer_config)
            # 检查模型是否有load_model方法，如果没有则跳过
            if hasattr(self.asr_model, 'load_model'):
                if self.asr_model.load_model():
                    print("✅ 阶段1: Paraformer-zh ASR 模型加载成功")
                else:
                    print("❌ 阶段1: Paraformer-zh ASR 模型加载失败")
            else:
                print("⚠️  阶段1: Paraformer-zh ASR 模型初始化完成（无load_model方法）")
        except Exception as e:
            print(f"❌ 阶段1: Paraformer-zh ASR 模型初始化失败: {e}")
            self.asr_model = None
        
        # 阶段2: 文本情感分类
        try:
            text_emotion_config = self.config_manager.config.get("models", {}).get("text_emotion", {})
            text_emotion_config["use_local_models"] = use_local
            
            # 优先使用model_id，如果没有则使用name
            model_id = text_emotion_config.get("model_id", text_emotion_config.get("name"))
            if model_id:
                text_emotion_config["model_id"] = model_id
            
            self.text_emotion_model = TextEmotionModel(text_emotion_config)
            if hasattr(self.text_emotion_model, 'load_model'):
                if self.text_emotion_model.load_model():
                    print("✅ 阶段2: 文本情感分类模型加载成功")
                else:
                    print("❌ 阶段2: 文本情感分类模型加载失败")
            else:
                print("⚠️  阶段2: 文本情感分类模型初始化完成（无load_model方法）")
        except Exception as e:
            print(f"❌ 阶段2: 文本情感分类模型初始化失败: {e}")
            self.text_emotion_model = None
        
        # 阶段3: emotion2vec 声学情感分析
        try:
            audio_emotion_config = self.config_manager.config.get("models", {}).get("emotion2vec", {})
            audio_emotion_config["use_local_models"] = use_local
            
            # 优先使用model_id，如果没有则使用name
            model_id = audio_emotion_config.get("model_id", audio_emotion_config.get("name"))
            if model_id:
                audio_emotion_config["model_id"] = model_id
            
            self.audio_emotion_model = AudioEmotionModel(audio_emotion_config)
            if hasattr(self.audio_emotion_model, 'load_model'):
                if self.audio_emotion_model.load_model():
                    print("✅ 阶段3: emotion2vec 声学情感分析模型加载成功")
                else:
                    print("❌ 阶段3: emotion2vec 声学情感分析模型初始化失败")
            else:
                print("⚠️  阶段3: emotion2vec 声学情感分析模型初始化完成（无load_model方法）")
        except Exception as e:
            print(f"❌ 阶段3: emotion2vec 声学情感分析模型初始化失败: {e}")
            self.audio_emotion_model = None

    def _load_models(self):
        """加载所有模型（兼容性方法）"""
        try:
            if self.text_emotion_model and hasattr(self.text_emotion_model, 'load_model'):
                if not self.text_emotion_model.load_model():
                    logger.warning("文本情感分析模型加载失败")
            if self.audio_emotion_model and hasattr(self.audio_emotion_model, 'load_model'):
                if not self.audio_emotion_model.load_model():
                    logger.warning("音频情感分析模型加载失败")
            if self.asr_model and hasattr(self.asr_model, 'load_model'):
                if not self.asr_model.load_model():
                    logger.warning("ASR模型加载失败")
            logger.info("模型加载完成")
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
    
    async def process_text_service(self, text: str, language: str = "zh", style_preference: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        try:
            logger.info(f"开始处理文字情感分析，输入长度: {len(text)}")
            if not self.text_emotion_model:
                raise EmotionAnalysisError("文本情感分析模型未初始化")
            
            emotion_result = self.text_emotion_model.analyze(text)
            if not emotion_result:
                raise EmotionAnalysisError("文本情感分析失败，未获得有效结果")
            
            emotion_tags = self._extract_text_emotion_tags(emotion_result)
            confidence = self._extract_confidence(emotion_result)
            generated_text = await self._generate_text_with_llm(text, emotion_tags, style_preference, language)
            
            image_path = None
            if self.image_generator:
                try:
                    image_prompt = self._build_image_prompt(text, emotion_tags, generated_text)
                    image_result = self.image_generator.generate(prompt=image_prompt, save_local=True)
                    image_path = image_result['local_paths'][0] if image_result and image_result.get('local_paths') else None
                except Exception as e:
                    logger.warning(f"图片生成失败: {e}")
            
            processing_time = time.time() - start_time
            # 构建完整的图片URL
            image_url = None
            if image_path:
                static_prefix = "/static/generated"
                try:
                    # 处理绝对路径和相对路径
                    abs_image_path = Path(image_path).resolve()
                    abs_gen_dir = Path("data/generated_images").resolve()
                    rel_path = abs_image_path.relative_to(abs_gen_dir)
                    image_url = f"{static_prefix}/{str(rel_path).replace('\\', '/')}"
                except ValueError as e:
                    logger.warning(f"图片路径转换失败: {e}")
                    image_url = None

            result = {
                'text': text,
                'emotion_tags': emotion_tags,
                'emotion_confidence': confidence,
                'generated_content': {
                    'text': generated_text,
                    'image_path': image_path,
                    'image_url': image_url,
                    'style': style_preference or 'default',
                    'metadata': {
                        'language': language,
                        'style_preference': style_preference,
                        'generation_timestamp': datetime.now(timezone.utc).isoformat()
                    }
                },
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
            
            if not self.asr_model:
                raise AudioProcessingError("ASR模型未初始化")
            
            transcribed_text = self.asr_model.transcribe(temp_audio_path)
            if not transcribed_text:
                raise AudioProcessingError("语音识别失败")
            
            audio_emotion_tags = ['neutral']  # 默认值
            if self.audio_emotion_model:
                try:
                    audio_emotion_result = self.audio_emotion_model.analyze(temp_audio_path)
                    audio_emotion_tags = self._extract_audio_emotion_tags(audio_emotion_result)
                except Exception as e:
                    logger.warning(f"音频情感分析失败: {e}")
            
            text_emotion_tags = ['neutral']  # 默认值
            if self.text_emotion_model:
                try:
                    text_emotion_result = self.text_emotion_model.analyze(transcribed_text)
                    text_emotion_tags = self._extract_text_emotion_tags(text_emotion_result)
                except Exception as e:
                    logger.warning(f"文本情感分析失败: {e}")
            
            merged_emotion = self._fuse_emotions(audio_emotion_tags, text_emotion_tags, fusion_strategy)
            generated_text = await self._generate_text_with_llm(transcribed_text, merged_emotion, None, language)
            
            image_path = None
            if self.image_generator:
                try:
                    image_prompt = self._build_image_prompt(transcribed_text, merged_emotion, generated_text)
                    image_result = self.image_generator.generate(prompt=image_prompt, save_local=True)
                    image_path = image_result['local_paths'][0] if image_result and image_result.get('local_paths') else None
                except Exception as e:
                    logger.warning(f"图片生成失败: {e}")
            
            processing_time = time.time() - start_time
            # 构建完整的图片URL
            image_url = None
            if image_path:
                static_prefix = "/static/generated"
                try:
                    # 处理绝对路径和相对路径
                    abs_image_path = Path(image_path).resolve()
                    abs_gen_dir = Path("data/generated_images").resolve()
                    rel_path = abs_image_path.relative_to(abs_gen_dir)
                    image_url = f"{static_prefix}/{str(rel_path).replace('\\', '/')}"
                except ValueError as e:
                    logger.warning(f"图片路径转换失败: {e}")
                    image_url = None

            result = {
                'transcribed_text': transcribed_text,
                'emotion_analysis': {
                    'audio_emotion': audio_emotion_tags,
                    'text_emotion': text_emotion_tags,
                    'merged_emotion': merged_emotion,
                    'fusion_rules': fusion_strategy
                },
                'generated_content': {
                    'text': generated_text,
                    'image_path': image_path,
                    'image_url': image_url,
                    'style': 'default',
                    'metadata': {
                        'language': language,
                        'dual_analysis': enable_dual_analysis,
                        'fusion_strategy': fusion_strategy,
                        'generation_timestamp': datetime.now(timezone.utc).isoformat()
                    }
                },
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
            text_emotion_tags = ['neutral']  # 默认值
            if self.text_emotion_model:
                try:
                    text_emotion_result = self.text_emotion_model.analyze(transcribed_text)
                    text_emotion_tags = self._extract_text_emotion_tags(text_emotion_result)
                except Exception as e:
                    logger.warning(f"文本情感分析失败: {e}")
            
            # 阶段3: 音频情感分析
            audio_emotion_tags = ['neutral']  # 默认值
            if self.audio_emotion_model:
                try:
                    audio_emotion_result = self.audio_emotion_model.analyze(audio_path)
                    audio_emotion_tags = self._extract_audio_emotion_tags(audio_emotion_result)
                except Exception as e:
                    logger.warning(f"音频情感分析失败: {e}")
            
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
            
            # 构建完整的图片URL
            image_url = None
            if image_path:
                static_prefix = "/static/generated"
                try:
                    # 处理绝对路径和相对路径
                    abs_image_path = Path(image_path).resolve()
                    abs_gen_dir = Path("data/generated_images").resolve()
                    rel_path = abs_image_path.relative_to(abs_gen_dir)
                    image_url = f"{static_prefix}/{str(rel_path).replace('\\', '/')}"
                except ValueError as e:
                    logger.warning(f"图片路径转换失败: {e}")
                    image_url = None

            return {
                'text': generated_text,
                'image_path': image_path,
                'image_url': image_url,
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
