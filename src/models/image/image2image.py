import os
import logging
import mimetypes
import socket
import shutil
import base64
import requests
from pathlib import Path
from volcenginesdkarkruntime import Ark
import uuid
from typing import Optional
from src.core.config_manager import ConfigManager
from src.models.image.base import BaseImageModel

# 设置日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # 让本模块的 INFO 可见

class ImageEditor(BaseImageModel):
    '''
    基于 Doubao-SeedEdit-3.0-i2i 的图像编辑封装：
    - 输入：原图路径 + prompt
    - 输出：编辑后图片路径
    '''
    def __init__(self, config_manager):
        logger.info("初始化ImageEditor")
        self.cfg = config_manager.get_image_cfg('i2i') or {}
        logger.info(f"获取到图像配置: {self.cfg}")
        
        super().__init__(self.cfg)
        self.out_dir = Path(config_manager.get_generated_images_dir())
        self.out_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"输出目录: {self.out_dir}")

        api = self.cfg.get("api", {})
        self.base_url = api.get("base_url", "https://ark.cn-beijing.volces.com/api/v3")
        
        # 从配置管理器获取API密钥
        self.api_key = config_manager.get_model_api_key("i2i")
        if not self.api_key:
            error_msg = "豆包API密钥未设置，请在环境变量中设置 ARK_API_KEY。请检查：1) 是否存在.env文件 2) .env文件中是否包含ARK_API_KEY=your_actual_key 3) 环境变量是否正确加载"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        logger.info(f"API密钥已获取，base_url: {self.base_url}")
        
        self.model_name = self.cfg.get("model_name", "doubao-seedit-3.0-i2i")
        dft = self.cfg.get("defaults", {})
        self.dft_guidance_scale = float(dft.get("guidance_scale", 5.5))
        self.dft_size = dft.get("size", "adaptive")
        self.dft_watermark = bool(dft.get("watermark", True))
        
        logger.info(f"模型名称: {self.model_name}, 默认参数: guidance_scale={self.dft_guidance_scale}, size={self.dft_size}, watermark={self.dft_watermark}")

        "sdk"
        self.client = Ark(base_url=self.base_url, api_key=self.api_key)
        self.is_loaded = True
        logger.info("ImageEditor初始化完成")
    
    def load_model(self) -> bool:
        """加载模型（API模型，无需本地加载）"""
        return True
    
    def _gen_name(self, suffix=".png") -> Path:
        return self.out_dir / f"edit_{uuid.uuid4().hex}{suffix}"

    @staticmethod
    def _guess_mime(p: Path) -> str:
        mime, _ = mimetypes.guess_type(p.name)
        return mime or "image/png"

    def _get_local_ip(self) -> str:
        # 更可靠的本机内网 IP 获取（不会真的发包）
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
    
    def _get_public_base_url(self) -> tuple[str, bool]:
        """
        返回 (base_url, is_loopback)
        优先使用环境变量：
        PUBLIC_BASE_URL (例如 http://myhost:8000)
        PUBLIC_HOST / PUBLIC_PORT 组合
        否则使用本机内网 IP + 端口（默认 8000）
        """
        env_url = os.getenv("PUBLIC_BASE_URL")
        if env_url:
            hostpart = env_url.split("://", 1)[-1].split("/", 1)[0]
            is_loopback = hostpart.startswith("127.0.0.1") or hostpart.startswith("localhost")
            return env_url.rstrip("/"), is_loopback

        host = os.getenv("PUBLIC_HOST") or self._get_local_ip()
        port = os.getenv("PUBLIC_PORT") or os.getenv("PORT") or os.getenv("UVICORN_PORT") or "8000"
        base = f"http://{host}:{port}"
        is_loopback = host in ("127.0.0.1", "localhost")
        return base, is_loopback
    
    def _ensure_under_static(self, src: Path, static_root: Path) -> Path:
        """
        确保文件位于静态目录下；若不在，则复制进去并返回目标路径
        """
        try:
            src_rel = src.resolve().relative_to(static_root.resolve())
            # 已在静态目录
            return src
        except Exception:
            static_root.mkdir(parents=True, exist_ok=True)
            dst = static_root / src.name
            # 避免重名覆盖，简单去重
            i = 1
            stem, suf = dst.stem, dst.suffix
            while dst.exists():
                dst = static_root / f"{stem}_{i}{suf}"
                i += 1
            shutil.copy2(src, dst)
            return dst
    
    def _to_data_url(self, p: Path) -> str:
        mime = self._guess_mime(p)
        b64 = base64.b64encode(p.read_bytes()).decode("ascii")
        return f"data:{mime};base64,{b64}"
    
    def _build_data_url_from_source(self, src_path: Optional[Path] = None, src_url: Optional[str] = None) -> str:
        """
        将本地文件或远程 URL 转为 data URL（data:image/<fmt>;base64,...）
        优先使用 src_path，其次 src_url。
        会检查 10MB 限制。
        """
        if src_path and src_path.exists():
            data = src_path.read_bytes()
            mime = self._guess_mime(src_path)
        elif src_url:
            resp = requests.get(src_url, timeout=20)
            resp.raise_for_status()
            data = resp.content
            ct = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            mime = ct if ct.startswith("image/") else "image/png"
        else:
            raise ValueError("既没有有效的本地路径，也没有可用的 URL，无法构建 base64。")

        if len(data) > 10 * 1024 * 1024:
            raise ValueError("回退到 base64 失败：图片超过 10MB 限制")

        b64 = base64.b64encode(data).decode("ascii")
        return f"data:{mime};base64,{b64}"
    
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
        规则：
        * 如果是本地路径 -> 优先转换为本机IP静态URL；若 base_url 是 127.0.0.1/localhost，则转成 base64 data URL
        * 如果是 URL -> 直接透传
        需要配置（可选）：
        self.static_root: 静态文件物理根目录（Path 或 str），默认 "static"
        self.static_mount: 静态路由前缀（如 "/static"），默认 "/static"
        """

        input_path_or_url = str(input_path_or_url)  # 统一为 str
        logger.info(f"开始图片编辑，输入: {input_path_or_url}, 提示词: {prompt}")

        guidance_scale = float(guidance_scale or self.dft_guidance_scale)
        size = size or self.dft_size
        watermark = self.dft_watermark if watermark is None else bool(watermark)

        logger.info(f"使用参数: guidance_scale={guidance_scale}, size={size}, watermark={watermark}")

        # 静态目录与 mount（若未设置则给默认）
        static_root = Path(getattr(self, "static_root", "static"))
        static_mount = getattr(self, "static_mount", "/static").rstrip("/")

        is_url = input_path_or_url.lower().startswith(("http://", "https://"))

        src_path: Optional[Path] = None
        src_url: Optional[str] = None

        # 计算 image 参数（只能是 URL 或 base64 字符串）
        if is_url:
            logger.info(f"处理URL图片: {input_path_or_url}")
            image_param = input_path_or_url
            src_url = image_param  # 记录原始 URL，供回退使用
        else:
            p = Path(input_path_or_url)
            if not (p.exists() and p.is_file()):
                error_msg = f"Input image not found: {p}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

            # 1) 先把本地文件确保放进静态目录
            p_in_static = self._ensure_under_static(p, static_root)

            # 2) 构造可访问的静态 URL（无论 base_url 是公网还是本机/私网，都先尝试 URL）
            base_url, _ = self._get_public_base_url()
            base_url = (base_url or "").rstrip("/")

            rel = p_in_static.resolve().relative_to(static_root.resolve()).as_posix()
            image_param = f"{base_url}{static_mount}/{rel}"

            # 记录回退源：优先用本地静态文件，必要时也用该 URL
            src_path = p_in_static
            src_url = image_param

            logger.info(f"本地图片已放入静态目录并构造 URL: {image_param}")

        first_error = None
        for attempt in (1, 2):
            try:
                logger.info(f"调用Ark API（第 {attempt} 次），模型: {self.model_name}")
                resp = self.client.images.generate(
                    model=self.model_name,
                    prompt=prompt,
                    image=image_param,   # 第一次用 URL 或 data URL；必要时回退替换为 base64 再重试
                    seed=seed,
                    guidance_scale=guidance_scale,
                    size=size,
                    watermark=watermark
                )
                logger.info("Ark API调用成功")
                break  # 成功，跳出循环

            except Exception as e:
                err_text = str(e)
                first_error = first_error or e

                # 仅当：第 1 次 + 当前 image_param 是 URL + 错误看起来是“远端下载失败/超时” → 回退为 base64
                retryable = (
                    attempt == 1
                    and isinstance(image_param, str)
                    and image_param.lower().startswith(("http://", "https://"))
                    and any(kw in err_text for kw in [
                        "Timeout while downloading url",
                        "download",                 # 泛化匹配
                        "InvalidParameter",         # Ark 常见错误码（含下载失败）
                        "cannot be accessed",       # 防御性匹配
                    ])
                )
                if retryable:
                    try:
                        logger.warning("远端无法下载该 URL，回退为 base64 data URL 并重试一次")
                        image_param = self._build_data_url_from_source(src_path=src_path, src_url=src_url)
                        continue
                    except Exception as conv_err:
                        logger.error(f"构建 base64 data URL 失败：{conv_err}")
                        raise first_error

                # 非可重试场景或已重试过：抛出最初的错误，便于观测
                logger.error(f"图片编辑过程中发生错误（第 {attempt} 次）: {err_text}", exc_info=True)
                raise first_error

        # —— 解析返回 —— #
        try:
            remote_url = resp.data[0].url
            logger.info(f"获取到远程URL: {remote_url}")
        except Exception as e:
            error_msg = f"Ark API 响应解析失败: {str(e)}"
            try:
                error_msg += f", resp={str(getattr(resp, '__dict__', '无法获取响应详情'))}"
            except Exception:
                pass
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        result = {"remote_url": remote_url}

        if save_local:
            logger.info("开始下载图片到本地")
            r = requests.get(remote_url, timeout=60)
            r.raise_for_status()
            out_path = self._gen_name(".png")
            Path(out_path).write_bytes(r.content)
            result["output_path"] = str(Path(out_path).resolve())
            logger.info(f"图片已保存到本地: {result['output_path']}")

        logger.info("图片编辑完成")
        return result
    
    def generate(self, **kwargs) -> dict:
        """实现基类的generate方法"""
        return self.edit_image(**kwargs)