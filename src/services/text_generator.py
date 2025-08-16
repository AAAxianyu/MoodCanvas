"""
文案生成服务 - 调用第三方API
"""
import os
import json
import requests
from typing import Dict, Any, Optional
from src.core.config_manager import ConfigManager
import logging

logger = logging.getLogger(__name__)

class TextGenerator:
    """文案生成服务"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.api_config = self.config_manager.config.get("text_generation", {})
        key = self.config_manager.get_secret("deepseek_api_key_env")
        self.api_key = os.getenv(key)
        
    async def generate_text(self, text: str, 
                            emotion_tags: list, 
                            style: Optional[str] = None,
                            image_content: str = None,
                            custom_prompt: str = None
                            ) -> str:
        """
        生成基于情感标签的文案
        
        Args:
            text: 原始文字
            emotion_tags: 情感标签列表
            style: 文案风格
            
        Returns:
            生成的文案
        """
        try:
            # 构建提示词
            emotion_desc = ", ".join(emotion_tags)
            style_desc = f"，风格：{style}" if style else ""
            
            prompt = f"""基于以下信息生成一段富有情感和冲击力的文案：

原始文字：{text}
情感标签：{emotion_desc}{style_desc}

要求：
1. 文案要体现情感标签的特点
2. 语言优美，富有感染力
3. 长度控制在100-200字
4. 保持与原始文字的关联性

请生成文案："""

            # 调用DeepSeek API
            if self.api_key:
                try:
                    result = await self._call_deepseek_api(prompt)
                    if result and len(result) > 10:  # 简单验证返回结果有效性
                        return result
                    return self._generate_fallback_text(text, emotion_tags, style)
                except Exception as api_error:
                    logger.error(f"DeepSeek API调用失败: {str(api_error)}")
                    return self._generate_fallback_text(text, emotion_tags, style)
            else:
                # 如果没有API密钥，返回模拟文案
                return self._generate_fallback_text(text, emotion_tags, style)
                
        except Exception as e:
            logger.error(f"文案生成失败: {str(e)}")
            return self._generate_fallback_text(text, emotion_tags, style)
    
    async def _call_deepseek_api(self, prompt: str) -> str:
        """调用DeepSeek API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个专业的文案创作助手，擅长根据情感标签创作富有感染力的文案。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 300,
                "temperature": 0.8
            }
            
            response = requests.post(
                f"{self.api_config['api']['base_url']}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                raise Exception(f"API调用失败: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"DeepSeek API调用失败: {str(e)}")
    
    def _generate_fallback_text(self, text: str, emotion_tags: list, style: Optional[str] = None) -> str:
        """生成备用文案（当API不可用时）"""
        emotion_desc = ", ".join(emotion_tags)
        style_desc = f"，{style}风格" if style else ""
        
        # 根据情感标签生成不同的文案模板
        templates = {
            "happy": f"在{emotion_desc}的温暖中，{text}绽放出新的光彩{style_desc}。让我们一起感受这份美好，让快乐在心中流淌。",
            "sad": f"当{emotion_desc}的思绪涌上心头，{text}仿佛也有了淡淡的忧伤{style_desc}。但请记住，每一个低谷都是新生的开始。",
            "angry": f"面对{emotion_desc}的挑战，{text}激发出内心的力量{style_desc}。让我们将这份情绪转化为前进的动力。",
            "neutral": f"在{emotion_desc}的平静中，{text}展现出最真实的一面{style_desc}。有时候，简单就是最美的表达。"
        }
        
        # 匹配情感标签
        for emotion in emotion_tags:
            if emotion in templates:
                return templates[emotion]
        
        # 默认模板
        return f"基于'{text}'的情感'{emotion_desc}'，我为您创作了这段文案：在{emotion_desc}的旋律中，{text}仿佛有了新的生命{style_desc}。"
