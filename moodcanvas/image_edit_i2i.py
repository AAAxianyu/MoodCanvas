import os
from pathlib import Path
from volcenginesdkarkruntime import Ark
import uuid
from typing import Optional

class ImageEditor:
    '''
    基于 Doubao-SeedEdit-3.0-i2i 的图像编辑封装：
    - 输入：原图路径 + prompt
    - 输出：编辑后图片路径
    '''
    def __init__(self, config_manager):
        self.cfg = config_manager.get_image_cfg('i2i') or {}
        self.out_dir = Path(config_manager.get_generated_images_dir())
        self.out_dir.mkdir(parents=True, exist_ok=True)

        api = self.cfg.get("api", {})
        self.base_url = api.get("base_url", "https://ark.cn-beijing.volces.com/api/v3")
        self.api_key = os.environ.get(api.get("api_key_env", "ARK_API_KEY"))
        if not self.api_key:
            self.api_key = config_manager.get_secret("doubao_api_key_env")
        if not self.api_key:
            raise RuntimeError("API key for Doubao is not set in environment variables没设置.")
        
        self.model_name = self.cfg.get("model_name", "doubao-seedit-3.0-i2i")
        dft = self.cfg.get("default", {})
        self.dft_guidance_scale = float(dft.get("guidance_scale", 5.5))
        self.dft_size = dft.get("size", "adaptive")
        self.dft_watermark = bool(dft.get("watermark", True))

        "sdk"
        self.client = Ark(base_url=self.base_url, api_key=self.api_key)
    
    def _gen_name(self, suffix=".png") -> Path:
        return self.out_dir / f"edit_{uuid.uuid4().hex}{suffix}"

    def edit_image(
        self,
        input_path_or_url: str,
        prompt: str,
        guidance_scale: Optional[float] = None,
        size: Optional[str] = None,
        seed: Optional[int] = None,
        watermark: Optional[bool] = None,
        save_local: bool = False
    ) -> dict:
    
        """
        - input_path_or_url: 本地路径或公网URL（推荐URL，最稳定）
        - prompt: 文本编辑指令
        - guidance_scale/size/seed/watermark: 覆盖默认参数
        - save_local: 是否下载远端图片到本地 static 目录
        """
        guidance_scale = float(guidance_scale or self.dft_guidance_scale)
        size = size or self.dft_size
        watermark = self.dft_watermark if watermark is None else bool(watermark)

        image_param = None
        is_url = input_path_or_url.lower().startswith(("http://", "https://"))
        if is_url:
            image_param = input_path_or_url
        else:
            if not os.path.exists(input_path_or_url):
                raise FileNotFoundError(f"Input image not found: {input_path_or_url}")
            image_param = open(input_path_or_url, "rb")

        try:
            resp = self.client.images.generate(
                model=self.model_name,
                prompt=prompt,
                image=image_param,
                seed=seed,
                guidance_scale=guidance_scale,
                size=size,
                watermark=watermark
            )
        finally:
            # 关闭文件句柄（如果是本地文件）
            if not is_url and hasattr(image_param, "close"):
                image_param.close()

        # 解析 URL
        try:
            remote_url = resp.data[0].url
        except Exception as e:
            raise RuntimeError(f"Ark API 响应解析失败: {e}, resp={getattr(resp,'__dict__',resp)}")

        result = {"remote_url": remote_url}

        if save_local:
            import requests
            out_path = self._gen_name(".png")
            r = requests.get(remote_url, timeout=60)
            r.raise_for_status()
            out_path.write_bytes(r.content)
            result["local_path"] = str(out_path.resolve())

        return result