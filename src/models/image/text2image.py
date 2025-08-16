# moodcanvas/text2image_t2i.py
from pathlib import Path
from typing import Optional, List
import uuid
import os
from volcenginesdkarkruntime import Ark
import requests
from src.core.config_manager import ConfigManager
from src.models.image.base import BaseImageModel

class ImageGenerator(BaseImageModel):
    """
    Doubao-Seedream-3.0-t2i（Ark API）文生图
    """

    def __init__(self, config_manager):
        self.cfg = config_manager.get_image_cfg("t2i") or {}
        super().__init__(self.cfg)
        self.out_dir = Path(config_manager.get_generated_images_dir())
        self.out_dir.mkdir(parents=True, exist_ok=True)

        api = self.cfg.get("api", {})
        self.base_url = api.get("base_url", "https://ark.cn-beijing.volces.com/api/v3")
        
        # 从配置管理器获取API密钥
        self.api_key = config_manager.get_model_api_key("t2i")
        if not self.api_key:
            raise RuntimeError("豆包API密钥未设置，请在环境变量中设置 ARK_API_KEY")

        raw_model = self.cfg.get("model_name", "doubao-seedream-3-0-t2i-250415")
        self.model_name = raw_model

        dft = self.cfg.get("defaults", {})
        self.dft_guidance_scale = float(dft.get("guidance_scale", 7.5))
        self.dft_size = dft.get("size", "1024x1024")   # t2i 用具体分辨率
        self.dft_num_images = int(dft.get("num_images", 1))
        self.dft_watermark = bool(dft.get("watermark", True))

        self.client = Ark(base_url=self.base_url, api_key=self.api_key)
        self.is_loaded = True

    def load_model(self) -> bool:
        """加载模型（API模型，无需本地加载）"""
        return True

    def _gen_name(self, idx: int, suffix=".png") -> Path:
        return self.out_dir / f"t2i_{uuid.uuid4().hex}_{idx}{suffix}"

    def _one_call(self, prompt: str, guidance_scale: float, size: str,
                  seed: Optional[int], watermark: bool):
        # 有的 SDK 不支持 n 参数；稳妥：单次只取一张
        try:
            resp = self.client.images.generate(
                model=self.model_name,
                prompt=prompt,
                seed=seed,
                guidance_scale=guidance_scale,
                size=size,
                watermark=watermark
            )
        except Exception as e:
            raise RuntimeError(f"Ark API 调用异常: {e}")

        # 解析 URL
        try:
            return resp.data[0].url
        except Exception as e:
            # 把 resp 展开以便排错
            detail = getattr(resp, "__dict__", str(resp))
            raise RuntimeError(f"Ark API 响应解析失败: {e}. resp={detail}")

    def generate(
        self,
        prompt: str,
        guidance_scale: Optional[float] = None,
        size: Optional[str] = None,
        seed: Optional[int] = None,
        num_images: Optional[int] = None,
        watermark: Optional[bool] = None,
        save_local: bool = False
    ) -> dict:
        guidance_scale = float(guidance_scale or self.dft_guidance_scale)
        size = size or self.dft_size
        watermark = self.dft_watermark if watermark is None else bool(watermark)
        n = int(num_images or self.dft_num_images)

        remote_urls: List[str] = []
        for _ in range(max(1, n)):
            url = self._one_call(prompt, guidance_scale, size, seed, watermark)
            remote_urls.append(url)

        result = {"remote_urls": remote_urls}

        if save_local:
            local_paths: List[str] = []
            for i, url in enumerate(remote_urls):
                out_path = self._gen_name(i, ".png")
                r = requests.get(url, timeout=60)
                r.raise_for_status()
                out_path.write_bytes(r.content)
                local_paths.append(str(out_path.resolve()))
            result["local_paths"] = local_paths

        return result