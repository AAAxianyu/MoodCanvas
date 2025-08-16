"""
图像服务
"""
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import time

from src.models.image.image2image import ImageEditor
from src.models.image.text2image import ImageGenerator
from src.core.config_manager import ConfigManager
from src.utils.file_utils import validate_image_file, save_uploaded_file
from src.core.exceptions import ImageProcessingError, FileValidationError

logger = logging.getLogger(__name__)

class ImageService:
    """图片服务，处理图片编辑和生成相关任务"""
    
    def __init__(self):
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 初始化图片编辑模型
        self.image_editor = ImageEditor(self.config_manager)
        
        # 初始化图片生成模型
        self.image_generator = ImageGenerator(self.config_manager)

        # 配置图片存储路径
        self.output_dir = "data/generated_images"
        self.temp_dir = "data/temp"
        
        # 确保目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        logger.info("图片服务初始化完成")
    
    async def edit_image_service(
        self,
        original_image_data: bytes,
        new_prompt: str,
        edit_style: Optional[str] = None,
        preserve_original: bool = True,
        strength: float = 0.7
    ) -> Dict[str, Any]:
        """
        场景3：图片编辑 → 基于原图 + 新提示词 → 生成新图片
        
        Args:
            original_image_data: 原始图片数据
            new_prompt: 新的文字提示词
            edit_style: 编辑风格
            preserve_original: 是否保持原图风格特征
            strength: 编辑强度
            
        Returns:
            包含图片编辑结果的字典
        """
        start_time = time.time()
        
        try:
            logger.info(f"开始处理图片编辑，提示词: {new_prompt}")
            
            # 1. 验证和保存原始图片
            logger.info("验证原始图片...")
            if not validate_image_file(original_image_data):
                raise FileValidationError("无效的图片文件格式")
            
            # 生成唯一文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_filename = f"original_{timestamp}.png"
            original_path = os.path.join(self.temp_dir, original_filename)
            
            # 保存原始图片
            save_uploaded_file(original_image_data, original_path)
            logger.info(f"原始图片已保存到: {original_path}")
            
            # 2. 构建编辑参数
            edit_params = {
                'input_path_or_url': original_path,
                'prompt': new_prompt,
                'guidance_scale': self._calculate_guidance_scale(strength),
                'save_local': True
            }
            
            logger.info(f"编辑参数: {edit_params}")
            
            # 3. 执行图片编辑
            logger.info("开始执行图片编辑...")
            edit_result = self.image_editor.edit_image(**edit_params)
            
            if not edit_result or not edit_result.get('local_path'):
                raise ImageProcessingError("图片编辑失败，未获得有效结果")
            
            edited_image_path = edit_result['local_path']
            remote_url = edit_result.get('remote_url', '')
            
            logger.info(f"图片编辑完成，输出路径: {edited_image_path}")
            
            # 4. 组装结果
            processing_time = time.time() - start_time
            
            result = {
                'edit_result': {
                    'original_image_path': original_path,
                    'edited_image_path': edited_image_path,
                    'remote_url': remote_url,
                    'changes_applied': f"根据提示词'{new_prompt}'对图片进行了编辑",
                    'edit_metadata': {
                        'edit_style': edit_style,
                        'preserve_original': preserve_original,
                        'strength': strength,
                        'guidance_scale': edit_params['guidance_scale'],
                        'edit_timestamp': datetime.now(timezone.utc).isoformat(),
                        'model_info': {
                            'model_name': 'doubao-seedit-3.0-i2i',
                            'provider': 'doubao'
                        }
                    }
                },
                'new_prompt': new_prompt,
                'processing_time': round(processing_time, 3),
                'status': 'success'
            }
            
            logger.info(f"图片编辑服务完成，总耗时: {processing_time:.3f}秒")
            return result
            
        except FileValidationError as e:
            logger.error(f"文件验证错误: {str(e)}")
            raise
        except ImageProcessingError as e:
            logger.error(f"图片处理错误: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"图片编辑服务未知错误: {str(e)}", exc_info=True)
            raise ImageProcessingError(f"图片编辑失败: {str(e)}")

    async def generate_image_service(
            self,
            prompt: str,
            style: Optional[str] = None,
            strength: float = 0.7,
            num_images: Optional[int] = 1,
            save_local: bool = True
    ) -> Dict[str, Any]:
        """
        场景4：图片生成 → 根据提示词生成新图片
    ):
        """
        start_time = time.time()

        try:
            logger.info(f"开始生成图片，提示词: {prompt}")

            # 1. 验证提示词
            if not prompt or len(prompt.strip()) == 0:
                raise ValueError("提示词不能为空")
            
            # 2. 构建生成参数
            generation_params = {
                'prompt': prompt,
                'guidance_scale': self._calculate_guidance_scale(strength),
                'size': '1024x1024',
                'num_images': num_images,
                'watermark': True,
                'save_local': save_local
            }

            logger.info(f"生成参数: {generation_params}")

            # 3. 执行图片生成
            logger.info("开始执行图片生成...")  
            generation_result = self.image_generator.generate(**generation_params)

            if not generation_result or not generation_result.get('local_paths'):
                raise ImageProcessingError("图片生成失败，未获得有效结果")
            
            generated_image_paths = generation_result['local_paths']
            remote_urls = generation_result.get('remote_urls', '')

            logger.info(f"图片生成完成，输出路径: {generated_image_paths}")

            # 4. 组装结果
            processing_time = time.time() - start_time

            result = {
                'generation_result': {
                    'image_paths': generated_image_paths,
                    'remote_urls': remote_urls,
                    'prompt': prompt,
                    'guidance_scale': generation_params['guidance_scale'],
                    'num_images': num_images,
                    'watermark': True,
                    'save_local': save_local
                },
                'new_prompt': prompt,
                'processing_time': round(processing_time, 3),
                'status': 'success'
            }

            logger.info(f"图片生成服务完成，总耗时: {processing_time:.3f}秒")
            return result
        
        except ValueError as e:
            logger.error(f"参数验证错误: {str(e)}")
            raise
        except ImageProcessingError as e:
            logger.error(f"图片处理错误: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"图片生成服务未知错误: {str(e)}", exc_info=True)
            raise ImageProcessingError(f"图片生成失败: {str(e)}")
        
    # ???

    def _calculate_guidance_scale(self, strength: float) -> float:
        """根据编辑强度计算guidance_scale参数"""
        # strength: 0.0-1.0, guidance_scale: 1.0-20.0
        # 强度越高，guidance_scale越大，编辑效果越明显
        base_scale = 5.5  # 默认值
        min_scale = 1.0
        max_scale = 20.0
        
        # 线性映射：strength 0.0 -> min_scale, strength 1.0 -> max_scale
        guidance_scale = min_scale + (max_scale - min_scale) * strength
        
        # 确保在合理范围内
        return max(min_scale, min(max_scale, guidance_scale))
    
    async def batch_edit_images(
        self,
        image_edit_tasks: list
    ) -> Dict[str, Any]:
        """
        批量图片编辑服务
        
        Args:
            image_edit_tasks: 图片编辑任务列表
            
        Returns:
            批量编辑结果
        """
        start_time = time.time()
        results = []
        failed_tasks = []
        
        try:
            logger.info(f"开始批量图片编辑，任务数量: {len(image_edit_tasks)}")
            
            for i, task in enumerate(image_edit_tasks):
                try:
                    logger.info(f"处理第 {i+1} 个任务...")
                    
                    # 验证任务参数
                    if not all(key in task for key in ['original_image_data', 'new_prompt']):
                        raise ValueError(f"任务 {i+1} 缺少必要参数")
                    
                    # 执行单个编辑任务
                    edit_result = await self.edit_image_service(
                        original_image_data=task['original_image_data'],
                        new_prompt=task['new_prompt'],
                        edit_style=task.get('edit_style'),
                        preserve_original=task.get('preserve_original', True),
                        strength=task.get('strength', 0.7)
                    )
                    
                    results.append({
                        'task_id': i,
                        'status': 'success',
                        'result': edit_result
                    })
                    
                    logger.info(f"任务 {i+1} 完成")
                    
                except Exception as e:
                    logger.error(f"任务 {i+1} 失败: {str(e)}")
                    failed_tasks.append({
                        'task_id': i,
                        'error': str(e),
                        'task_data': task
                    })
                    
                    results.append({
                        'task_id': i,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            # 组装批量结果
            total_time = time.time() - start_time
            success_count = len([r for r in results if r['status'] == 'success'])
            failed_count = len(failed_tasks)
            
            batch_result = {
                'total_tasks': len(image_edit_tasks),
                'successful_tasks': success_count,
                'failed_tasks': failed_count,
                'results': results,
                'failed_tasks_details': failed_tasks,
                'total_processing_time': round(total_time, 3),
                'status': 'completed'
            }
            
            logger.info(f"批量图片编辑完成，成功: {success_count}, 失败: {failed_count}")
            return batch_result
            
        except Exception as e:
            logger.error(f"批量图片编辑服务错误: {str(e)}", exc_info=True)
            raise ImageProcessingError(f"批量图片编辑失败: {str(e)}")
    
    def cleanup_temp_files(self, file_paths: list = None):
        """
        清理临时文件
        
        Args:
            file_paths: 要清理的文件路径列表，如果为None则清理整个temp目录
        """
        try:
            if file_paths:
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"已删除临时文件: {file_path}")
            else:
                # 清理整个temp目录
                for filename in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        logger.info(f"已删除临时文件: {file_path}")
                        
        except Exception as e:
            logger.warning(f"清理临时文件时出错: {str(e)}")
    
    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """
        获取图片信息
        
        Args:
            image_path: 图片路径
            
        Returns:
            图片信息字典
        """
        try:
            if not os.path.exists(image_path):
                return {'error': '图片文件不存在'}
            
            file_size = os.path.getsize(image_path)
            file_stat = os.stat(image_path)
            
            return {
                'file_path': image_path,
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'created_time': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                'exists': True
            }
            
        except Exception as e:
            logger.error(f"获取图片信息失败: {str(e)}")
            return {'error': str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        try:
            return {
                'model_name': 'doubao-seedit-3.0-i2i',
                'provider': 'doubao',
                'type': 'image-to-image',
                'capabilities': ['image_editing', 'style_transfer'],
                'supported_formats': ['PNG', 'JPEG', 'WebP'],
                'max_image_size': '10MB',
                'status': 'ready'
            }
        except Exception as e:
            logger.error(f"获取模型信息失败: {str(e)}")
            return {'error': str(e)}
