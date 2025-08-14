"""
工具函数测试
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from typing import Dict, Any

# 导入工具函数
from src.utils.file_utils import (
    validate_image_file, save_uploaded_file, get_file_hash, 
    get_file_size_mb, cleanup_file, ensure_directory_exists,
    get_file_extension, is_valid_file_size
)
from src.utils.audio_utils import (
    validate_audio_file, get_audio_info, is_valid_audio_size,
    get_audio_duration_estimate, validate_wav_format, get_audio_metadata
)
from src.utils.response_utils import (
    create_success_response, create_error_response, handle_moodcanvas_error,
    handle_generic_error, create_paginated_response, create_file_response,
    create_processing_status_response, validate_response_data, sanitize_response_data,
    create_health_check_response, format_uptime
)

class TestFileUtils:
    """文件工具函数测试"""
    
    def test_validate_image_file_png(self):
        """测试PNG图片文件验证"""
        # PNG文件头: 89 50 4E 47 0D 0A 1A 0A
        png_data = b'\x89PNG\r\n\x1a\n' + b'fake_png_data'
        assert validate_image_file(png_data) == True
    
    def test_validate_image_file_jpeg(self):
        """测试JPEG图片文件验证"""
        # JPEG文件头: FF D8 FF
        jpeg_data = b'\xff\xd8\xff' + b'fake_jpeg_data'
        assert validate_image_file(jpeg_data) == True
    
    def test_validate_image_file_webp(self):
        """测试WebP图片文件验证"""
        # WebP文件头: RIFF ... WEBP
        webp_data = b'RIFF' + b'\x00\x00\x00\x00' + b'WEBP' + b'fake_webp_data'
        assert validate_image_file(webp_data) == True
    
    def test_validate_image_file_gif(self):
        """测试GIF图片文件验证"""
        # GIF文件头: GIF87a 或 GIF89a
        gif_data = b'GIF87a' + b'fake_gif_data'
        assert validate_image_file(gif_data) == True
        
        gif_data = b'GIF89a' + b'fake_gif_data'
        assert validate_image_file(gif_data) == True
    
    def test_validate_image_file_invalid(self):
        """测试无效图片文件验证"""
        invalid_data = b'invalid_image_data'
        assert validate_image_file(invalid_data) == False
        
        # 测试空数据
        assert validate_image_file(b'') == False
        
        # 测试过短数据
        assert validate_image_file(b'123') == False
    
    def test_save_uploaded_file(self):
        """测试文件保存"""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test.txt")
            file_data = b"test content"
            
            result = save_uploaded_file(file_data, file_path)
            assert result == True
            
            # 验证文件是否保存成功
            assert os.path.exists(file_path)
            with open(file_path, 'rb') as f:
                assert f.read() == file_data
    
    def test_save_uploaded_file_create_directory(self):
        """测试文件保存时创建目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "subdir", "test.txt")
            file_data = b"test content"
            
            result = save_uploaded_file(file_data, file_path)
            assert result == True
            
            # 验证目录和文件是否创建成功
            assert os.path.exists(file_path)
    
    def test_get_file_hash(self):
        """测试文件哈希计算"""
        file_data = b"test content"
        hash_value = get_file_hash(file_data)
        
        # 验证哈希值格式（MD5是32位十六进制）
        assert len(hash_value) == 32
        assert all(c in '0123456789abcdef' for c in hash_value)
    
    def test_get_file_size_mb(self):
        """测试文件大小计算"""
        file_data = b"test content"
        size_mb = get_file_size_mb(file_data)
        
        # 验证大小计算
        expected_size = len(file_data) / (1024 * 1024)
        assert size_mb == expected_size
    
    def test_cleanup_file(self):
        """测试文件清理"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(b"test content")
        
        # 验证文件存在
        assert os.path.exists(temp_path)
        
        # 清理文件
        result = cleanup_file(temp_path)
        assert result == True
        
        # 验证文件已被删除
        assert not os.path.exists(temp_path)
    
    def test_cleanup_file_not_exists(self):
        """测试清理不存在的文件"""
        result = cleanup_file("/nonexistent/file")
        assert result == False
    
    def test_ensure_directory_exists(self):
        """测试目录创建"""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "new_subdir")
            
            result = ensure_directory_exists(new_dir)
            assert result == True
            
            # 验证目录是否创建成功
            assert os.path.exists(new_dir)
            assert os.path.isdir(new_dir)
    
    def test_get_file_extension(self):
        """测试文件扩展名获取"""
        # 测试各种文件路径
        assert get_file_extension("test.txt") == "txt"
        assert get_file_extension("image.png") == "png"
        assert get_file_extension("document.pdf") == "pdf"
        assert get_file_extension("no_extension") == None
        assert get_file_extension(".hidden") == None
    
    def test_is_valid_file_size(self):
        """测试文件大小验证"""
        file_data = b"test content"
        
        # 测试有效大小
        assert is_valid_file_size(file_data, max_size_mb=1.0) == True
        
        # 测试超出限制
        large_data = b"x" * (2 * 1024 * 1024)  # 2MB
        assert is_valid_file_size(large_data, max_size_mb=1.0) == False

class TestAudioUtils:
    """音频工具函数测试"""
    
    def test_validate_audio_file_wav(self):
        """测试WAV音频文件验证"""
        # WAV文件头: RIFF
        wav_data = b'RIFF' + b'fake_wav_data'
        assert validate_audio_file(wav_data) == True
    
    def test_validate_audio_file_mp3(self):
        """测试MP3音频文件验证"""
        # MP3文件头: FF FB 或 FF F3 或 FF F2
        mp3_data = b'\xff\xfb' + b'fake_mp3_data'
        assert validate_audio_file(mp3_data) == True
        
        mp3_data = b'\xff\xf3' + b'fake_mp3_data'
        assert validate_audio_file(mp3_data) == True
    
    def test_validate_audio_file_m4a(self):
        """测试M4A音频文件验证"""
        # M4A文件头
        m4a_data = b'\x00\x00\x00\x20ftypM4A' + b'fake_m4a_data'
        assert validate_audio_file(m4a_data) == True
    
    def test_validate_audio_file_flac(self):
        """测试FLAC音频文件验证"""
        # FLAC文件头: fLaC
        flac_data = b'fLaC' + b'fake_flac_data'
        assert validate_audio_file(flac_data) == True
    
    def test_validate_audio_file_invalid(self):
        """测试无效音频文件验证"""
        invalid_data = b'invalid_audio_data'
        assert validate_audio_file(invalid_data) == False
        
        # 测试空数据
        assert validate_audio_file(b'') == False
        
        # 测试过短数据
        assert validate_audio_file(b'123') == False
    
    def test_is_valid_audio_size(self):
        """测试音频文件大小验证"""
        audio_data = b"test audio content"
        
        # 测试有效大小
        assert is_valid_audio_size(audio_data, max_size_mb=1.0) == True
        
        # 测试超出限制
        large_data = b"x" * (100 * 1024 * 1024)  # 100MB
        assert is_valid_audio_size(large_data, max_size_mb=50.0) == False
    
    def test_get_audio_duration_estimate(self):
        """测试音频时长估算"""
        # 测试WAV文件
        wav_data = b'RIFF' + b'\x00\x00\x00\x00' + b'WAVE' + b'fake_wav_data'
        duration = get_audio_duration_estimate(wav_data)
        assert duration is not None
        assert duration > 0
    
    def test_validate_wav_format(self):
        """测试WAV格式验证"""
        # 有效的WAV文件头
        wav_data = b'RIFF' + b'\x00\x00\x00\x08' + b'WAVE' + b'fake_wav_data'
        is_valid, error_msg = validate_wav_format(wav_data)
        assert is_valid == True
        assert error_msg is None
        
        # 无效的WAV文件头
        invalid_wav = b'INVALID' + b'fake_data'
        is_valid, error_msg = validate_wav_format(invalid_wav)
        assert is_valid == False
        assert error_msg is not None
    
    def test_get_audio_metadata(self):
        """测试音频元数据获取"""
        wav_data = b'RIFF' + b'\x00\x00\x00\x08' + b'WAVE' + b'fake_wav_data'
        metadata = get_audio_metadata(wav_data)
        
        assert metadata['format'] == 'WAV'
        assert metadata['valid'] == True
        assert 'file_size_bytes' in metadata
        assert 'file_size_mb' in metadata

class TestResponseUtils:
    """响应工具函数测试"""
    
    def test_create_success_response(self):
        """测试成功响应创建"""
        data = {"key": "value"}
        response = create_success_response(data, "操作成功", 200)
        
        assert response['success'] == True
        assert response['message'] == "操作成功"
        assert response['data'] == data
        assert response['status_code'] == 200
        assert 'timestamp' in response
    
    def test_create_error_response(self):
        """测试错误响应创建"""
        response = create_error_response("错误信息", "ERROR_CODE", 400, {"detail": "详细信息"})
        
        assert response['success'] == False
        assert response['error']['message'] == "错误信息"
        assert response['error']['code'] == "ERROR_CODE"
        assert response['error']['status_code'] == 400
        assert response['error']['details'] == {"detail": "详细信息"}
        assert 'timestamp' in response
    
    def test_create_paginated_response(self):
        """测试分页响应创建"""
        data = [{"id": 1}, {"id": 2}]
        response = create_paginated_response(data, 100, 1, 10, "查询成功")
        
        assert response['success'] == True
        assert response['data']['items'] == data
        assert response['data']['pagination']['page'] == 1
        assert response['data']['pagination']['page_size'] == 10
        assert response['data']['pagination']['total'] == 100
        assert response['data']['pagination']['total_pages'] == 10
    
    def test_create_file_response(self):
        """测试文件响应创建"""
        response = create_file_response("/path/file.txt", "file.txt", 1024, "text/plain")
        
        assert response['success'] == True
        assert response['data']['file_path'] == "/path/file.txt"
        assert response['data']['file_name'] == "file.txt"
        assert response['data']['file_size'] == 1024
        assert response['data']['mime_type'] == "text/plain"
        assert 'download_url' in response['data']
    
    def test_create_processing_status_response(self):
        """测试处理状态响应创建"""
        response = create_processing_status_response("task_123", "processing", 50.0, 30.0)
        
        assert response['success'] == True
        assert response['data']['task_id'] == "task_123"
        assert response['data']['status'] == "processing"
        assert response['data']['progress'] == 50.0
        assert response['data']['estimated_time_remaining'] == 30.0
    
    def test_validate_response_data(self):
        """测试响应数据验证"""
        data = {"field1": "value1", "field2": "value2"}
        required_fields = ["field1", "field2"]
        
        assert validate_response_data(data, required_fields) == True
        
        # 测试缺少字段
        assert validate_response_data(data, ["field1", "field2", "field3"]) == False
        
        # 测试非字典数据
        assert validate_response_data("not_dict", required_fields) == False
    
    def test_sanitize_response_data(self):
        """测试响应数据清理"""
        # 测试包含敏感字段的数据
        data = {
            "username": "user123",
            "password": "secret123",
            "api_key": "key123",
            "normal_field": "value"
        }
        
        cleaned = sanitize_response_data(data)
        
        assert "username" in cleaned
        assert "normal_field" in cleaned
        assert "password" not in cleaned
        assert "api_key" not in cleaned
    
    def test_create_health_check_response(self):
        """测试健康检查响应创建"""
        response = create_health_check_response("test_service", "healthy", "1.0.0", 3600)
        
        assert response['success'] == True
        assert response['data']['service'] == "test_service"
        assert response['data']['status'] == "healthy"
        assert response['data']['version'] == "1.0.0"
        assert response['data']['uptime_seconds'] == 3600
        assert response['data']['uptime_formatted'] == "1.0小时"
    
    def test_format_uptime(self):
        """测试运行时间格式化"""
        assert format_uptime(30) == "30.0秒"
        assert format_uptime(90) == "1.5分钟"
        assert format_uptime(7200) == "2.0小时"
        assert format_uptime(172800) == "2.0天"

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])



