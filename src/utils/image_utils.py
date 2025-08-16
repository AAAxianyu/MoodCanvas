# src/utils/file_utils.py
# -*- coding: utf-8 -*-
import io
import os
from typing import Iterable
from PIL import Image


def validate_image_file(
    image_bytes: bytes,
    *,
    allowed_formats: Iterable[str] = ("PNG", "JPEG", "JPG", "WEBP"),
    max_mb: int = 10,
    min_width: int = 16,
    min_height: int = 16,
    max_width: int = 8192,
    max_height: int = 8192,
) -> bool:
    """
    轻量图片校验：
      - 非空与大小限制
      - 能被 Pillow 打开且 verify 通过
      - 格式在允许清单内（PNG/JPEG/WebP 等）
      - 尺寸在给定范围内

    返回:
        True  通过校验
        False 未通过（原因见代码各分支，外层通常抛 FileValidationError）
    """
    # 1) 基础检查
    if not image_bytes or not isinstance(image_bytes, (bytes, bytearray)):
        return False

    max_bytes = max_mb * 1024 * 1024
    if len(image_bytes) > max_bytes:
        return False

    # 2) 使用 Pillow 进行完整性与格式校验
    try:
        bio = io.BytesIO(image_bytes)

        # 先 verify() 做完整性检查（文件尾/损坏等）
        with Image.open(bio) as im:
            im.verify()

        # verify() 会把文件指针移到末尾，需重置再打开一次读取信息
        bio.seek(0)
        with Image.open(bio) as im:
            fmt = (im.format or "").upper()
            if fmt == "JPG":
                fmt = "JPEG"

            if fmt not in {f.upper() for f in allowed_formats}:
                return False

            w, h = im.size
            if w < min_width or h < min_height:
                return False
            if w > max_width or h > max_height:
                return False

    except Exception:
        # 任何异常都视为验证失败
        return False

    return True


def save_uploaded_file(image_bytes: bytes, target_path: str) -> None:
    """
    将内存中的图片字节保存到磁盘。
    - 自动创建上级目录
    - 原子写入（先写临时文件再替换）

    注意：调用前请先用 validate_image_file 校验通过。
    """
    directory = os.path.dirname(os.path.abspath(target_path))
    os.makedirs(directory, exist_ok=True)

    tmp_path = f"{target_path}.part"
    with open(tmp_path, "wb") as f:
        f.write(image_bytes)

    # 原子替换，避免并发读到不完整文件
    os.replace(tmp_path, target_path)