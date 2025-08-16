import os
import logging
from pathlib import Path
from volcenginesdkarkruntime import Ark
import uuid
from typing import Optional
from src.core.config_manager import ConfigManager
from src.models.image.base import BaseImageModel

# 设置日志记录器
logger = logging.getLogger(__name__)

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
        logger.info(f"开始图片编辑，输入: {input_path_or_url}, 提示词: {prompt}")
        
        guidance_scale = float(guidance_scale or self.dft_guidance_scale)
        size = size or self.dft_size
        watermark = self.dft_watermark if watermark is None else bool(watermark)
        
        logger.info(f"使用参数: guidance_scale={guidance_scale}, size={size}, watermark={watermark}")

        image_param = None
        file_handle = None
        is_url = input_path_or_url.lower().startswith(("http://", "https://"))
        
        try:
            if is_url:
                logger.info(f"处理URL图片: {input_path_or_url}")
                image_param = input_path_or_url
            else:
                logger.info(f"处理本地图片: {input_path_or_url}")
                if not os.path.exists(input_path_or_url):
                    error_msg = f"Input image not found: {input_path_or_url}"
                    logger.error(error_msg)
                    raise FileNotFoundError(error_msg)
                file_handle = open(input_path_or_url, "rb")
                image_param = file_handle
                logger.info("本地图片文件已打开")

            logger.info(f"调用Ark API，模型: {self.model_name}")
            resp = self.client.images.generate(
                model=self.model_name,
                prompt=prompt,
                image=image_param,
                seed=seed,
                guidance_scale=guidance_scale,
                size=size,
                watermark=watermark
            )
            logger.info("Ark API调用成功")

            # 解析 URL
            try:
                remote_url = resp.data[0].url
                logger.info(f"获取到远程URL: {remote_url}")
            except Exception as e:
                # 确保异常信息不包含不可序列化的对象
                error_msg = f"Ark API 响应解析失败: {str(e)}"
                if hasattr(resp, '__dict__'):
                    try:
                        resp_info = str(resp.__dict__)
                    except:
                        resp_info = "无法获取响应详情"
                    error_msg += f", resp={resp_info}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            result = {"remote_url": remote_url}

            if save_local:
                logger.info("开始下载图片到本地")
                import requests
                out_path = self._gen_name(".png")
                r = requests.get(remote_url, timeout=60)
                r.raise_for_status()
                out_path.write_bytes(r.content)
                result["local_path"] = str(out_path.resolve())
                logger.info(f"图片已保存到本地: {result['local_path']}")

            logger.info("图片编辑完成")
            return result
            
        except Exception as e:
            logger.error(f"图片编辑过程中发生错误: {str(e)}", exc_info=True)
            # 重新抛出异常，确保不包含文件对象信息
            if file_handle is not None:
                try:
                    file_handle.close()
                except:
                    pass
                file_handle = None
            raise e
        finally:
            # 确保文件句柄被正确关闭
            if file_handle is not None:
                try:
                    file_handle.close()
                    logger.info("文件句柄已关闭")
                except Exception:
                    logger.warning("关闭文件句柄时发生错误")
                file_handle = None
    
    def generate(self, **kwargs) -> dict:
        """实现基类的generate方法"""
        return self.edit_image(**kwargs)