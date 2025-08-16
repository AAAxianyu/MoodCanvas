import pytest
import os
from unittest.mock import patch, mock_open
from pathlib import Path
from datetime import datetime
from src.utils.audio_utils import convert_audio_format, get_audio_duration
from src.utils.file_utils import ensure_dir, save_file, load_file
from src.utils.response_utils import success_response, error_response

class TestAudioUtils:
    """测试音频工具函数"""
    
    @patch("src.utils.audio_utils.AudioSegment.from_file")
    def test_convert_audio_format(self, mock_audio_segment, tmp_path):
        """测试音频格式转换"""
        mock_audio = mock_audio_segment.return_value
        mock_audio.export.return_value = None
        
        input_file = tmp_path / "input.wav"
        output_file = tmp_path / "output.mp3"
        
        result = convert_audio_format(str(input_file), str(output_file))
        
        assert result == str(output_file)
        mock_audio_segment.assert_called_once_with(str(input_file))
        mock_audio.export.assert_called_once_with(str(output_file), format="mp3")
    
    @patch("src.utils.audio_utils.AudioSegment.from_file")
    def test_get_audio_duration(self, mock_audio_segment):
        """测试获取音频时长"""
        mock_audio = mock_audio_segment.return_value
        mock_audio.duration_seconds = 10.5
        
        duration = get_audio_duration("test.wav")
        
        assert duration == 10.5
        mock_audio_segment.assert_called_once_with("test.wav")

class TestFileUtils:
    """测试文件工具函数"""
    
    def test_ensure_dir(self, tmp_path):
        """测试确保目录存在"""
        test_dir = tmp_path / "test_dir"
        
        # 目录不存在时创建
        assert not test_dir.exists()
        ensure_dir(str(test_dir))
        assert test_dir.exists()
        
        # 目录已存在时不报错
        ensure_dir(str(test_dir))
    
    def test_save_and_load_file(self, tmp_path):
        """测试文件保存和加载"""
        test_file = tmp_path / "test.txt"
        test_data = b"test data"
        
        # 测试保存文件
        save_file(str(test_file), test_data)
        assert test_file.read_bytes() == test_data
        
        # 测试加载文件
        loaded_data = load_file(str(test_file))
        assert loaded_data == test_data
    
    def test_save_file_failure(self):
        """测试文件保存失败"""
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = IOError("写入失败")
            with pytest.raises(IOError, match="写入失败"):
                save_file("test.txt", b"data")
    
    def test_load_file_failure(self):
        """测试文件加载失败"""
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = IOError("读取失败")
            with pytest.raises(IOError, match="读取失败"):
                load_file("test.txt")

class TestResponseUtils:
    """测试响应工具函数"""
    
    def test_success_response(self):
        """测试成功响应"""
        data = {"key": "value"}
        response = success_response(data)
        
        assert response["status"] == "success"
        assert response["data"] == data
        assert "timestamp" in response
    
    def test_error_response(self):
        """测试错误响应"""
        error_msg = "测试错误"
        status_code = 400
        response = error_response(error_msg, status_code)
        
        assert response["status"] == "error"
        assert response["message"] == error_msg
        assert response["code"] == status_code
        assert "timestamp" in response
    
    def test_response_timestamp(self):
        """测试响应时间戳"""
        test_time = datetime(2023, 1, 1, 12, 0, 0)
        
        with patch("src.utils.response_utils.datetime") as mock_datetime:
            mock_datetime.now.return_value = test_time
            response = success_response({})
            
            assert response["timestamp"] == test_time.isoformat()
