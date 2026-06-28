"""
配置管理模块 - Popin
保存和加载用户设置
"""

import json
import os
from pathlib import Path


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file="popin_config.json"):
        # 使用用户目录存储配置，避免权限问题
        appdata_dir = Path(os.getenv('APPDATA', os.path.expanduser('~'))) / 'Popin'
        appdata_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = appdata_dir / config_file
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置"""
        default_config = {
            # 应用设置
            "app": {
                "language": "zh_CN"  # zh_CN, en_US, ja_JP
            },
            
            # 字幕样式设置
            "subtitle": {
                "font_size": 10,
                "font_name": "Arial",
                "font_path": "",  # 自定义字体路径
                "margin_v": 25,
                "margin_h": 0,
                "bold": False,
                "italic": False,
                "primary_color": "#FFFFFF",  # 主颜色（白色）
                "outline_color": "#000000",  # 描边颜色（黑色）
                "outline_width": 2,
                "outline_enabled": True,
                "shadow": False,
                "shadow_offset": 2
            },
            
            # 翻译设置
            "translation": {
                "enabled": False,
                "target_language": "中文",
                "display_mode": "双行显示（原文+翻译）",
                "translation_on_top": True
            },
            
            # Whisper 设置
            "whisper": {
                "language": "请选择语言 ⚠",
                "gpu_backend": "Vulkan",
                "threads": 4,
                "embed_subtitles": True,
                "audio_preprocessing": True,
                "parallel_count": 2  # 并行处理数量
            },
            
            # AI 配置
            "ai": {
                "api_url": "https://api.openai.com/v1",
                "api_key": "",
                "model": "gpt-5-4-mini"
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # 合并配置，保留默认值
                    for key in default_config:
                        if key in loaded:
                            default_config[key].update(loaded[key])
                    return default_config
            except Exception as e:
                print(f"加载配置失败: {e}，使用默认配置")
                return default_config
        
        return default_config
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get(self, category, key, default=None):
        """获取配置值"""
        try:
            return self.config.get(category, {}).get(key, default)
        except:
            return default
    
    def set(self, category, key, value):
        """设置配置值"""
        if category not in self.config:
            self.config[category] = {}
        self.config[category][key] = value
    
    def get_category(self, category):
        """获取整个类别的配置"""
        return self.config.get(category, {})
    
    def set_category(self, category, values):
        """设置整个类别的配置"""
        self.config[category] = values
