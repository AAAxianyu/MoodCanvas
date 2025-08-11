import os
import json
import datetime
from pathlib import Path

# 阶段1: ASR (Paraformer-zh)
from funasr import AutoModel

# 阶段2: 文本情感分类 (PyTorch)
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# 阶段3: 声学情感分析 (emotion2vec)
# from funasr import AutoModel  # 已在上面导入

class MultiModelEmotionAnalyzer:
    """三阶段多模型情感分析系统"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.setup_models()
    
    def setup_models(self):
        """初始化三个模型"""
        print("🚀 正在初始化三阶段情感分析模型...")
        
        # 调试信息：显示配置状态
        print(f"🔧 配置状态: use_local_models = {self.config_manager.config['settings']['use_local_models']}")
        print(f"🔧 Paraformer 本地路径: {self.config_manager.get_model_path('paraformer')}")
        print(f"🔧 emotion2vec 本地路径: {self.config_manager.get_model_path('emotion2vec')}")
        
        # 阶段1: Paraformer-zh ASR
        try:
            paraformer_path = self.config_manager.get_model_path("paraformer")
            if self.config_manager.config["settings"]["use_local_models"]:
                # 使用本地模型 - 转换为绝对路径
                import os
                paraformer_abs_path = os.path.abspath(paraformer_path)
                print(f"🔄 尝试加载本地模型: {paraformer_abs_path}")
                self.paraformer_model = AutoModel(model=paraformer_abs_path)
                print("✅ 阶段1: Paraformer-zh 本地模型加载成功")
            else:
                # 使用在线模型 - 使用正确的模型名称
                print("🔄 尝试加载在线模型")
                self.paraformer_model = AutoModel(model="iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch")
                print("✅ 阶段1: Paraformer-zh 在线模型加载成功")
        except Exception as e:
            print(f"❌ 阶段1: Paraformer-zh ASR 模型加载失败: {e}")
            self.paraformer_model = None
        
        # 阶段2: 中文文本情感分类
        try:
            if self.config_manager.config["settings"]["use_local_models"]:
                # 使用本地中文情感分类模型
                local_text_model_path = "distilbert-base-uncased-go-emotions-student"
                print(f"🔄 尝试加载本地中文情感分类模型: {local_text_model_path}")
                self.text_tokenizer = AutoTokenizer.from_pretrained(local_text_model_path)
                self.text_model = AutoModelForSequenceClassification.from_pretrained(local_text_model_path)
            else:
                # 使用在线中文情感分类模型
                model_name = "uer/roberta-base-finetuned-jd-binary-chinese"
                print(f"🔄 尝试加载在线中文情感分类模型: {model_name}")
                self.text_tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.text_model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            self.text_pipeline = pipeline(
                "text-classification", 
                model=self.text_model, 
                tokenizer=self.text_tokenizer
            )
            print("✅ 阶段2: 中文文本情感分类模型加载成功")
        except Exception as e:
            print(f"❌ 阶段2: 中文文本情感分类模型加载失败: {e}")
            self.text_pipeline = None
        
        # 阶段3: emotion2vec 声学情感分析
        try:
            emotion2vec_path = self.config_manager.get_model_path("emotion2vec")
            if self.config_manager.config["settings"]["use_local_models"]:
                # 使用本地模型
                self.emotion2vec_model = AutoModel(model=emotion2vec_path)
                print("✅ 阶段3: emotion2vec 本地模型加载成功")
            else:
                # 使用在线模型
                self.emotion2vec_model = AutoModel(model="iic/emotion2vec_plus_large")
                print("✅ 阶段3: emotion2vec 在线模型加载成功")
        except Exception as e:
            print(f"❌ 阶段3: emotion2vec 声学情感分析模型加载失败: {e}")
            self.emotion2vec_model = None
    
    def stage1_asr_transcription(self, audio_path):
        """阶段1: Paraformer-zh ASR 语音转文字"""
        if not self.paraformer_model:
            return None, "Paraformer-zh 模型未加载"
        
        try:
            # 使用 Paraformer-zh 进行语音识别
            print(f"🔄 开始转录音频: {audio_path}")
            result = self.paraformer_model.generate(
                audio_path,
                output_dir="./temp_outputs",
                batch_size=1
            )
            
            # 调试信息：显示原始输出
            print(f"🔍 ASR 原始输出: {result}")
            print(f"🔍 输出类型: {type(result)}")
            if result:
                print(f"🔍 输出长度: {len(result)}")
                if len(result) > 0:
                    print(f"🔍 第一个元素: {result[0]}")
                    print(f"🔍 第一个元素类型: {type(result[0])}")
            
            # 提取转录文本
            if result and len(result) > 0:
                transcription = result[0].get('text', '').strip()
                if transcription:
                    return transcription, None
                else:
                    return None, "ASR 转录结果为空"
            else:
                return None, "ASR 转录结果为空"
        except Exception as e:
            return None, f"ASR 转录失败: {e}"
    
    def stage2_text_emotion(self, text):
        """阶段2: 中文文本情感分类"""
        if not self.text_pipeline:
            return None, "文本情感分类模型未加载"
        
        try:
            # 中文情感分类
            result = self.text_pipeline(text)
            if result and len(result) > 0:
                # 提取情感标签和置信度
                emotions = []
                for item in result:
                    emotions.append({
                        "label": item["label"],
                        "confidence": item["score"]
                    })
                return emotions, None
            else:
                return None, "文本情感分析结果为空"
        except Exception as e:
            return None, f"文本情感分析失败: {e}"
    
    def stage3_audio_emotion(self, audio_path):
        """阶段3: emotion2vec 声学情感分析"""
        if not self.emotion2vec_model:
            return None, "emotion2vec 模型未加载"
        
        try:
            # 声学情感分析
            result = self.emotion2vec_model.generate(
                audio_path,
                output_dir="./temp_outputs",
                granularity="utterance",
                extract_embedding=False
            )
            
            # 解析 emotion2vec 输出 - 支持多种输出格式
            emotions = []
            
            if isinstance(result, list) and len(result) > 0:
                # 如果是列表格式
                for item in result:
                    if isinstance(item, dict):
                        if "emotion" in item:
                            # 新格式
                            for emotion_item in item["emotion"]:
                                emotions.append({
                                    "label": emotion_item.get("label", "unknown"),
                                    "confidence": emotion_item.get("score", 0.0)
                                })
                        elif "scores" in item:
                            # 旧格式 - 使用预定义的情感标签
                            emotion_labels = ['生气/angry', '厌恶/disgusted', '恐惧/fearful', '开心/happy', 
                                           '中立/neutral', '其他/other', '难过/sad', '吃惊/surprised', '<unk>']
                            scores = item["scores"]
                            for i, score in enumerate(scores):
                                if i < len(emotion_labels):
                                    emotions.append({
                                        "label": emotion_labels[i],
                                        "confidence": score
                                    })
            elif isinstance(result, dict):
                # 如果是字典格式
                if "emotion" in result:
                    for emotion_item in result["emotion"]:
                        emotions.append({
                            "label": emotion_item.get("label", "unknown"),
                            "confidence": emotion_item.get("score", 0.0)
                        })
                elif "scores" in result:
                    emotion_labels = ['生气/angry', '厌恶/disgusted', '恐惧/fearful', '开心/happy', 
                                   '中立/neutral', '其他/other', '难过/sad', '吃惊/surprised', '<unk>']
                    scores = result["scores"]
                    for i, score in enumerate(scores):
                        if i < len(emotion_labels):
                            emotions.append({
                                "label": emotion_labels[i],
                                "confidence": score
                            })
            
            if emotions:
                # 按置信度排序
                emotions.sort(key=lambda x: x["confidence"], reverse=True)
                return emotions, None
            else:
                return None, "无法解析 emotion2vec 输出格式"
                
        except Exception as e:
            return None, f"声学情感分析失败: {e}"
    
    def run_three_stage_analysis(self, audio_path):
        """运行三阶段情感分析"""
        print(f"\n🎵 开始分析音频文件: {audio_path}")
        print("=" * 60)
        
        results = {
            "audio_file": audio_path,
            "timestamp": datetime.datetime.now().isoformat(),
            "stages": {}
        }
        
        # 阶段1: ASR 转录
        print("📝 阶段1: 语音转文字 (Paraformer-zh)...")
        transcription, error = self.stage1_asr_transcription(audio_path)
        if error:
            print(f"❌ 转录失败: {error}")
            results["stages"]["asr"] = {"status": "failed", "error": error}
        else:
            print(f"✅ 转录成功: {transcription}")
            results["stages"]["asr"] = {
                "status": "success", 
                "transcription": transcription
            }
        
        # 阶段2: 文本情感分析
        if transcription:
            print("💭 阶段2: 文本情感分析 (中文情感分类)...")
            text_emotions, error = self.stage2_text_emotion(transcription)
            if error:
                print(f"❌ 文本情感分析失败: {error}")
                results["stages"]["text_emotion"] = {"status": "failed", "error": error}
            else:
                print(f"✅ 文本情感分析成功: {text_emotions}")
                results["stages"]["text_emotion"] = {
                    "status": "success", 
                    "emotions": text_emotions
                }
        
        # 阶段3: 声学情感分析
        print("🎵 阶段3: 声学情感分析 (emotion2vec)...")
        audio_emotions, error = self.stage3_audio_emotion(audio_path)
        if error:
            print(f"❌ 声学情感分析失败: {error}")
            results["stages"]["audio_emotion"] = {"status": "failed", "error": error}
        else:
            print(f"✅ 声学情感分析成功: {audio_emotions}")
            results["stages"]["audio_emotion"] = {
                "status": "success", 
                "emotions": audio_emotions
            }
        
        # 综合分析结果
        results["summary"] = self.generate_summary(results)
        
        return results
    
    def generate_summary(self, results):
        """生成综合分析摘要"""
        summary = {
            "overall_status": "success",
            "key_findings": [],
            "recommendations": []
        }
        
        # 检查各阶段状态
        failed_stages = []
        for stage_name, stage_result in results["stages"].items():
            if stage_result.get("status") == "failed":
                failed_stages.append(stage_name)
        
        if failed_stages:
            summary["overall_status"] = "partial_success"
            summary["key_findings"].append(f"部分阶段失败: {', '.join(failed_stages)}")
        
        # 提取关键信息
        if "asr" in results["stages"] and results["stages"]["asr"]["status"] == "success":
            transcription = results["stages"]["asr"]["transcription"]
            summary["key_findings"].append(f"语音内容: {transcription}")
        
        # 情感分析对比
        text_emotions = results["stages"].get("text_emotion", {}).get("emotions", [])
        audio_emotions = results["stages"].get("audio_emotion", {}).get("emotions", [])
        
        if text_emotions and audio_emotions:
            summary["key_findings"].append("文本与声学情感分析结果对比")
            summary["recommendations"].append("建议结合两种分析结果进行综合判断")
        
        return summary
    
    def save_results(self, results):
        """保存分析结果到文件"""
        output_dir = self.config_manager.get_output_dir()
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"emotion_analysis_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # 保存结果
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 分析结果已保存到: {filepath}")
        return filepath

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.setup_environment()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self.get_default_config()
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            "paths": {
                "input_dir": "input",
                "output_dir": "outputs",
                "temp_dir": "temp_outputs",
                "models_cache": "./models_cache"
            },
            "models": {
                "emotion2vec": {
                    "name": "iic/emotion2vec_plus_large",
                    "type": "funasr",
                    "local_path": "emotion2vec_plus_large"
                },
                "paraformer": {
                    "name": "paraformer-zh",
                    "type": "funasr",
                    "local_path": "paraformer-zh"
                }
            },
            "settings": {
                "use_local_models": True,
                "download_to_project": True
            },
            "audio_files": {
                "default": "asr_example.wav",
                "available": ["asr_example.wav", "example.wav"]
            }
        }
    
    def setup_environment(self):
        """设置环境变量"""
        cache_dir = self.config["paths"]["models_cache"]
        os.environ['HF_HOME'] = cache_dir
        os.environ['MODELSCOPE_CACHE'] = cache_dir
    
    def get_model_path(self, model_name):
        """获取模型路径"""
        if model_name in self.config["models"]:
            return self.config["models"][model_name]["local_path"]
        return None
    
    def get_output_dir(self):
        """获取输出目录"""
        return self.config["paths"]["output_dir"]
    
    def get_audio_path(self, filename):
        """获取音频文件路径"""
        input_dir = self.config["paths"]["input_dir"]
        return os.path.join(input_dir, filename)

def main():
    """主函数"""
    print("🎭 三阶段多模型情感分析系统")
    print("=" * 50)
    
    # 初始化配置管理器
    config_manager = ConfigManager()
    
    # 初始化情感分析器
    analyzer = MultiModelEmotionAnalyzer(config_manager)
    
    # 获取音频文件路径 - 使用配置文件中的默认文件
    audio_file = config_manager.config["audio_files"]["default"]
    audio_path = config_manager.get_audio_path(audio_file)
    
    print(f"🎵 使用音频文件: {audio_file}")
    print(f"🎵 完整路径: {audio_path}")
    
    if not os.path.exists(audio_path):
        print(f"❌ 音频文件不存在: {audio_path}")
        print(f"📁 可用的音频文件: {config_manager.config['audio_files']['available']}")
        return
    
    # 运行三阶段分析
    results = analyzer.run_three_stage_analysis(audio_path)
    
    # 保存结果
    output_file = analyzer.save_results(results)
    
    # 打印摘要
    print("\n📊 分析摘要:")
    print("-" * 30)
    summary = results["summary"]
    print(f"整体状态: {summary['overall_status']}")
    for finding in summary["key_findings"]:
        print(f"• {finding}")
    for recommendation in summary["recommendations"]:
        print(f"💡 {recommendation}")

if __name__ == "__main__":
    main()