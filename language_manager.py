"""
语言管理模块
支持中文、英文、日文的多语言切换
"""

import json
from pathlib import Path


class LanguageManager:
    """语言管理器"""
    
    SUPPORTED_LANGUAGES = {
        'zh_CN': '中文',
        'en_US': 'English',
        'ja_JP': '日本語'
    }
    
    def __init__(self, language='zh_CN'):
        """
        初始化语言管理器
        
        Args:
            language: 语言代码 (zh_CN, en_US, ja_JP)
        """
        self.current_language = language
        self.translations = {}
        self.load_language(language)
    
    def load_language(self, language):
        """加载语言文件"""
        locale_file = Path('locales') / f'{language}.json'
        
        if not locale_file.exists():
            print(f"Warning: Language file {locale_file} not found, falling back to zh_CN")
            locale_file = Path('locales') / 'zh_CN.json'
            language = 'zh_CN'
        
        try:
            with open(locale_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
            self.current_language = language
            print(f"Loaded language: {language}")
        except Exception as e:
            print(f"Error loading language file: {e}")
            self.translations = {}
    
    def get(self, key, default=None, **kwargs):
        """
        获取翻译文本
        
        Args:
            key: 键名，支持点分隔的路径，如 'tabs.subtitle'
            default: 默认值
            **kwargs: 格式化参数
        
        Returns:
            str: 翻译后的文本
        """
        keys = key.split('.')
        value = self.translations
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                value = None
                break
        
        if value is None:
            value = default if default is not None else key
        
        # 支持格式化
        if kwargs and isinstance(value, str):
            try:
                value = value.format(**kwargs)
            except:
                pass
        
        return value
    
    def t(self, key, default=None, **kwargs):
        """get() 的简写形式"""
        return self.get(key, default, **kwargs)
    
    def change_language(self, language):
        """切换语言"""
        if language in self.SUPPORTED_LANGUAGES:
            self.load_language(language)
            return True
        return False
    
    def get_available_languages(self):
        """获取可用的语言列表"""
        return self.SUPPORTED_LANGUAGES.copy()


# 全局语言管理器实例
_lang_manager = None


def get_language_manager():
    """获取全局语言管理器实例"""
    global _lang_manager
    if _lang_manager is None:
        # 尝试从配置文件加载语言设置
        try:
            from config_manager import ConfigManager
            config = ConfigManager()
            language = config.get('app', 'language', 'zh_CN')
        except:
            language = 'zh_CN'
        
        _lang_manager = LanguageManager(language)
    return _lang_manager


def t(key, default=None, **kwargs):
    """全局翻译函数"""
    return get_language_manager().get(key, default, **kwargs)
