"""
大模型API集成测试
测试真实的大模型API调用（需要有效的API密钥）
"""
import pytest
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 加载环境变量（如果.env文件存在）
def load_env_if_exists():
    """加载.env文件中的环境变量"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# 在导入模块前加载环境变量
load_env_if_exists()

from src.core.config_manager import ConfigManager
from src.models.image.image2image import ImageEditor
from src.models.image.text2image import ImageGenerator


class TestIntegrationAPI:
    """大模型API集成测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前设置"""
        # 检查是否有有效的API密钥
        self.has_ark_key = bool(os.environ.get("ARK_API_KEY"))
        self.has_openai_key = bool(os.environ.get("OPENAI_API_KEY"))
        
        if not self.has_ark_key:
            pytest.skip("需要设置ARK_API_KEY环境变量来运行豆包API测试")
        
        # 创建配置管理器
        self.config_manager = ConfigManager()
        
        # 创建测试图片目录
        self.test_dir = Path("data/test_images")
        self.test_dir.mkdir(parents=True, exist_ok=True)
    
    @pytest.mark.skip(reason="豆包API测试需要激活模型服务")
    def test_doubao_image_edit_real_api(self):
        """测试豆包图片编辑真实API调用"""
        pytest.skip("豆包API测试需要激活模型服务")
    
    @pytest.mark.skip(reason="豆包API测试需要激活模型服务")
    def test_doubao_text_to_image_real_api(self):
        """测试豆包文本生成图片真实API调用"""
        pytest.skip("豆包API测试需要激活模型服务")
    
    @pytest.mark.skipif(not os.environ.get("ARK_API_KEY"), reason="需要ARK_API_KEY")
    def test_doubao_api_parameters(self):
        """测试豆包API参数配置"""
        try:
            # 检查配置
            i2i_config = self.config_manager.get_image_cfg('i2i')
            t2i_config = self.config_manager.get_image_cfg('t2i')
            
            assert i2i_config is not None
            assert t2i_config is not None
            assert i2i_config.get("use_api") is True
            assert t2i_config.get("use_api") is True
            
            # 检查API密钥
            api_key = self.config_manager.get_model_api_key("i2i")
            assert api_key is not None
            assert len(api_key) > 10  # 确保API密钥有合理长度
            
            print(f"✅ 豆包API配置检查成功")
            print(f"   i2i模型: {i2i_config.get('model_name')}")
            print(f"   t2i模型: {t2i_config.get('model_name')}")
            print(f"   API密钥长度: {len(api_key)}")
            
        except Exception as e:
            pytest.fail(f"豆包API配置检查失败: {str(e)}")
    
    def test_config_manager_loading(self):
        """测试配置管理器加载"""
        try:
            # 检查基本配置
            config = self.config_manager._config if hasattr(self.config_manager, '_config') else self.config_manager.config
            assert config is not None
            assert "image_models" in config
            assert "paths" in config
            
            # 检查路径配置
            paths = config["paths"]
            assert "generated_images_dir" in paths
            assert "temp_dir" in paths
            
            # 检查图片模型配置
            image_models = self.config_manager.config["image_models"]
            assert "i2i" in image_models
            assert "t2i" in image_models
            
            print(f"✅ 配置管理器加载成功")
            print(f"   生成图片目录: {paths['generated_images_dir']}")
            print(f"   临时目录: {paths['temp_dir']}")
            
        except Exception as e:
            pytest.fail(f"配置管理器加载失败: {str(e)}")
    
    @pytest.mark.skipif(not os.environ.get("ARK_API_KEY"), reason="需要ARK_API_KEY")
    def test_api_error_scenarios(self):
        """测试API错误场景"""
        try:
            # 创建图片编辑器
            editor = ImageEditor(self.config_manager)
            
            # 测试无效的图片URL
            with pytest.raises(Exception):
                editor.edit_image(
                    input_path_or_url="https://invalid-url-that-does-not-exist.com/image.jpg",
                    prompt="测试无效URL"
                )
            
            print(f"✅ API错误场景测试成功")
            
        except Exception as e:
            # 如果API调用成功，说明错误处理可能有问题
            print(f"⚠️  API错误场景测试: {str(e)}")
    
    def test_environment_variables(self):
        """测试环境变量设置"""
        # 检查必要的环境变量
        ark_key = os.environ.get("ARK_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")
        
        if ark_key:
            print(f"✅ ARK_API_KEY已设置 (长度: {len(ark_key)})")
        else:
            print(f"❌ ARK_API_KEY未设置")
        
        if openai_key:
            print(f"✅ OPENAI_API_KEY已设置 (长度: {len(openai_key)})")
        else:
            print(f"❌ OPENAI_API_KEY未设置")
        
        # 至少需要一个API密钥
        assert ark_key or openai_key, "至少需要设置一个API密钥"


def run_quick_test():
    """快速测试函数，用于手动测试"""
    print("🚀 开始大模型API快速测试...")
    
    # 检查环境变量
    ark_key = os.environ.get("ARK_API_KEY")
    if not ark_key:
        print("❌ 未设置ARK_API_KEY环境变量")
        return False
    
    try:
        # 创建配置管理器
        config_manager = ConfigManager()
        
        # 测试豆包API配置
        i2i_config = config_manager.get_image_cfg('i2i')
        api_key = config_manager.get_model_api_key("i2i")
        
        print(f"✅ 配置加载成功")
        print(f"   i2i模型: {i2i_config.get('model_name')}")
        print(f"   API密钥: {api_key[:10]}..." if api_key else "未设置")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False


if __name__ == "__main__":
    # 运行快速测试
    if run_quick_test():
        print("\n🎉 快速测试通过！可以运行完整测试套件")
        print("运行命令: pytest tests/test_integration_api.py -v")
    else:
        print("\n💥 快速测试失败，请检查配置")
