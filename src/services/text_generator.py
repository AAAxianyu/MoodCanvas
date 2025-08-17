"""
文案生成服务 - 使用官方OpenAI SDK调用DeepSeek API
"""
import os
from typing import List, Optional
from openai import AsyncOpenAI
from src.core.config_manager import ConfigManager
import logging

logger = logging.getLogger(__name__)

class TextGenerator:
    """文案生成服务（纯API版本，无降级方案）"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        初始化生成器
        :param config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.api_config = self.config_manager.config.get("text_generation", {})
        self._client = None  # 延迟初始化的API客户端

    @property
    def client(self) -> AsyncOpenAI:
        """获取线程安全的异步OpenAI客户端"""
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self._get_api_key(),
                base_url=self.api_config.get("base_url", "https://api.deepseek.com"),
                timeout=self.api_config.get("timeout", 30.0))
        return self._client

    def _get_api_key(self) -> str:
        """从环境变量获取API密钥"""
        # 直接从配置中获取环境变量名
        key_env_var = self.api_config.get("api", {}).get("api_key_env", "DEEPSEEK_API_KEY")
        
        # 尝试从环境变量获取
        api_key = os.getenv(key_env_var)
        if not api_key:
            # 如果环境变量不存在，尝试从配置中直接获取密钥
            api_key = self.api_config.get("api", {}).get("api_key")
            if not api_key:
                raise ValueError(f"无法获取DeepSeek API密钥，请检查环境变量 {key_env_var} 或配置文件中的api_key设置")
        
        # 验证密钥格式
        if not api_key.startswith("sk-"):
            raise ValueError("API密钥格式不正确，应以'sk-'开头")
            
        return api_key

    async def generate_text(
        self,
        text: str,
        emotion_tags: List[str],
        style: Optional[str] = None,
        image_content: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        生成基于情感标签的文案
        
        :param text: 原始文字内容
        :param emotion_tags: 情感标签列表
        :param style: 文案风格（可选）
        :param image_content: 图片内容描述（可选）
        :param custom_prompt: 自定义提示词（覆盖自动生成）
        :return: 生成的文案内容
        :raises: 当API调用失败时抛出原始异常
        """
        prompt = self._build_prompt(
            text=text,
            emotion_tags=emotion_tags,
            style=style,
            image_content=image_content,
            custom_prompt=custom_prompt
        )

        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的PLOG创作助手，拥有3年社交媒体文案策划经验，擅长根据情感标签创作富有感染力的文案。"
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=300,
            stream=False
        )
        
        generated_text = response.choices[0].message.content
        logger.debug(f"生成文案成功，长度: {len(generated_text)}")
        return generated_text.strip()

    def _build_prompt(
        self,
        text: str,
        emotion_tags: List[str],
        style: Optional[str],
        image_content: Optional[str],
        custom_prompt: Optional[str]
    ) -> str:
        """
        构建API请求的提示词
        
        :return: 完整构造的提示词字符串
        """
        if custom_prompt:
            return custom_prompt

        components = [
            f"原始文字：{text}",
            f"情感标签：{', '.join(emotion_tags)}"
        ]
        
        if style:
            components.append(f"风格要求：{style}")
        if image_content:
            components.append(f"关联图片内容：{image_content}")
            
        prompt = "基于以下信息生成文案：\n\n" + "\n".join(components) + """
            
要求：
1. 准确体现情感标签特点
2. 语言优美且富有感染力
3. 长度控制在100-200字之间
4. 保持与原始内容的关联性
5. 将普通生活场景转化为富有感染力的故事
6. 精准把握[情感标签]的细微差别并视觉化表达
4. 运用修辞手法增强文案记忆点
5. 保持口语化同时提升文字质感

请遵循以下创作原则：
1. 使用「感官描写法」激活读者五感
2. 采用「悬念结构」提升完读率
3. 适当加入「金句」增强传播性
4. 保持[品牌调性]的一致性
5. 控制文案在120-180个汉字之间
6. 避免使用陈词滥调和过于大众化的表达
7. 可以选择性使用少量颜文字提高活泼感

8. 大幅提高文案和图片的关联性
9. 输出文案的时候不要附带分析，直接输出文案
请直接输出生成文案："""
        return prompt
