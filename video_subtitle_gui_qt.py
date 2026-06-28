import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox,
                             QSpinBox, QCheckBox, QGroupBox, QFileDialog, QMessageBox,
                             QProgressBar, QRadioButton, QButtonGroup, QDialog, QTabWidget,
                             QColorDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QPainterPath, QRegion
import requests

from video_subtitle_generator_cpp import VideoSubtitleGeneratorCpp
from config_manager import ConfigManager
from language_manager import get_language_manager


def load_ai_config():
    """加载AI配置（全局函数）"""
    config_file = Path("ai_config.json")
    default_config = {
        "api_url": "https://api.openai.com/v1",
        "api_key": "",
        "model": "gpt-5-4-mini"
    }
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default_config
    return default_config


class AIConfigDialog(QDialog):
    """AI配置对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI 翻译配置")
        self.setFixedSize(600, 420)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        
        # 加载配置
        self.config = self.load_config()
        
        self.init_ui()
        self.apply_styles()
    
    def load_config(self):
        """加载配置文件"""
        config_file = Path("ai_config.json")
        default_config = {
            "api_url": "https://api.openai.com/v1",
            "api_key": "",
            "model": "gpt-5-4-mini",
            "api_format": "openai"  # openai, anthropic, custom
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 确保有 api_format 字段
                    if 'api_format' not in loaded_config:
                        loaded_config['api_format'] = 'openai'
                    return loaded_config
            except:
                return default_config
        return default_config
    
    def save_config(self):
        """保存配置到文件"""
        config = {
            "api_url": self.api_url_input.text().strip(),
            "api_key": self.api_key_input.text().strip(),
            "model": self.model_input.text().strip(),
            "api_format": self.get_api_format()
        }
        
        try:
            with open("ai_config.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败:\n{str(e)}")
            return False
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title = QLabel("AI 翻译 API 配置")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 说明
        desc = QLabel("配置 OpenAI 或 Anthropic 兼容的 API 用于字幕翻译\n配置会自动保存到 ai_config.json")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #666666; font-size: 10pt;")
        layout.addWidget(desc)
        
        layout.addSpacing(15)
        
        # API 格式选择（选项卡样式 - 最顶部）
        format_layout = QHBoxLayout()
        format_layout.addStretch()
        
        self.format_button_group = QButtonGroup()
        self.openai_radio = QRadioButton("OpenAI")
        self.anthropic_radio = QRadioButton("Anthropic")
        self.custom_radio = QRadioButton("自定义")
        
        # 设置按钮样式使其看起来像选项卡
        for btn in [self.openai_radio, self.anthropic_radio, self.custom_radio]:
            btn.setFixedHeight(40)
            btn.setFixedWidth(120)
        
        self.format_button_group.addButton(self.openai_radio, 0)
        self.format_button_group.addButton(self.anthropic_radio, 1)
        self.format_button_group.addButton(self.custom_radio, 2)
        
        format_layout.addWidget(self.openai_radio)
        format_layout.addWidget(self.anthropic_radio)
        format_layout.addWidget(self.custom_radio)
        format_layout.addStretch()
        
        # 根据配置设置默认选中
        api_format = self.config.get("api_format", "openai")
        if api_format == "anthropic":
            self.anthropic_radio.setChecked(True)
        elif api_format == "custom":
            self.custom_radio.setChecked(True)
        else:
            self.openai_radio.setChecked(True)
        
        # 连接信号
        self.format_button_group.buttonClicked.connect(self.on_format_changed)
        
        layout.addLayout(format_layout)
        
        layout.addSpacing(20)
        
        # API 地址
        api_url_layout = QHBoxLayout()
        api_url_label = QLabel("API 地址:")
        api_url_label.setFixedWidth(80)
        api_url_layout.addWidget(api_url_label)
        self.api_url_input = QLineEdit(self.config.get("api_url", "https://api.openai.com/v1"))
        api_url_layout.addWidget(self.api_url_input)
        layout.addLayout(api_url_layout)
        
        # API Key
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel("API Key:")
        api_key_label.setFixedWidth(80)
        api_key_layout.addWidget(api_key_label)
        self.api_key_input = QLineEdit(self.config.get("api_key", ""))
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("输入您的 API Key")
        api_key_layout.addWidget(self.api_key_input)
        
        # 显示/隐藏按钮
        self.show_key_btn = QPushButton("👁")
        self.show_key_btn.setFixedWidth(40)
        self.show_key_btn.setCheckable(True)
        self.show_key_btn.clicked.connect(self.toggle_key_visibility)
        api_key_layout.addWidget(self.show_key_btn)
        layout.addLayout(api_key_layout)
        
        # 模型名称
        model_layout = QHBoxLayout()
        model_label = QLabel("模型名称:")
        model_label.setFixedWidth(80)
        model_layout.addWidget(model_label)
        self.model_input = QLineEdit(self.config.get("model", "gpt-5-4-mini"))
        self.model_input.setPlaceholderText("如: gpt-5-4-mini, claude-4-5-sonnet, deepseek-v4-flash")
        model_layout.addWidget(self.model_input)
        layout.addLayout(model_layout)
        
        layout.addSpacing(30)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        test_btn = QPushButton("测试连接")
        test_btn.setFixedWidth(120)
        test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(test_btn)
        
        save_btn = QPushButton("保存配置")
        save_btn.setFixedWidth(120)
        save_btn.clicked.connect(self.save_and_close)
        button_layout.addWidget(save_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
    
    def get_api_format(self):
        """获取选中的API格式"""
        if self.openai_radio.isChecked():
            return "openai"
        elif self.anthropic_radio.isChecked():
            return "anthropic"
        else:
            return "custom"
    
    def on_format_changed(self):
        """当API格式改变时，自动更新API地址"""
        api_format = self.get_api_format()
        
        if api_format == "openai":
            self.api_url_input.setText("https://api.openai.com/v1")
            # 如果当前模型是 claude，提示用户更改
            if self.model_input.text().startswith("claude"):
                self.model_input.setText("gpt-5-4-mini")
        elif api_format == "anthropic":
            self.api_url_input.setText("https://api.anthropic.com/v1")
            # 如果当前模型是 gpt，提示用户更改
            if self.model_input.text().startswith("gpt"):
                self.model_input.setText("claude-3-5-sonnet-20241022")
    
    def toggle_key_visibility(self):
        """切换 API Key 可见性"""
        if self.show_key_btn.isChecked():
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_btn.setText("[\]")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_btn.setText("[-]")
    
    def test_connection(self):
        """测试 API 连接"""
        api_url = self.api_url_input.text().strip()
        api_key = self.api_key_input.text().strip()
        model = self.model_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "警告", "请先输入 API Key")
            return
        
        if not model:
            QMessageBox.warning(self, "警告", "请先输入模型名称")
            return
        
        try:
            # 判断是 Anthropic 还是 OpenAI
            api_format = self.get_api_format()
            is_anthropic = api_format == "anthropic" or model.startswith('claude')
            
            if is_anthropic:
                response = requests.post(
                    f"{api_url.rstrip('/')}/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": model,
                        "max_tokens": 10,
                        "messages": [{"role": "user", "content": "Hi"}]
                    },
                    timeout=10
                )
            else:
                response = requests.post(
                    f"{api_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": "Hi"}],
                        "max_tokens": 10
                    },
                    timeout=10
                )
            
            if response.status_code == 200:
                QMessageBox.information(self, "成功", "✓ API 连接测试成功！")
            else:
                QMessageBox.warning(self, "失败", f"API 返回错误:\n状态码 {response.status_code}\n{response.text[:200]}")
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"连接测试失败:\n{str(e)}")
    
    def save_and_close(self):
        """保存并关闭"""
        if self.save_config():
            QMessageBox.information(self, "成功", "配置已保存！")
            self.accept()
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #333333;
                font-family: "Microsoft YaHei";
            }
            QLineEdit {
                border: 2px solid #E3F2FD;
                border-radius: 8px;
                padding: 8px 12px;
                background-color: #FFFFFF;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 2px solid #64B5F6;
            }
            QRadioButton {
                font-size: 11pt;
                font-weight: bold;
                padding: 8px 16px;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                background-color: #F5F5F5;
            }
            QRadioButton:checked {
                background-color: #64B5F6;
                color: white;
                border: 2px solid #64B5F6;
            }
            QRadioButton:hover {
                border: 2px solid #90CAF9;
            }
            QRadioButton::indicator {
                width: 0px;
                height: 0px;
            }
            QPushButton {
                background-color: #64B5F6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
            QPushButton:pressed {
                background-color: #2196F3;
            }
            QPushButton[text="👁"] {
                background-color: #E3F2FD;
                color: #333;
            }
            QPushButton[text="👁"]:checked {
                background-color: #BBDEFB;
            }
        """)


class ProcessThread(QThread):
    """处理视频的后台线程"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, generator, video_paths, language, output_dir, 
                 embed_subtitles, threads, gpu_layers, subtitle_style,
                 translate_enabled, translate_config, use_audio_preprocessing, parallel_count=2):
        super().__init__()
        self.generator = generator
        self.video_paths = video_paths if isinstance(video_paths, list) else [video_paths]
        self.language = language
        self.output_dir = output_dir
        self.embed_subtitles = embed_subtitles
        self.threads = threads
        self.gpu_layers = gpu_layers
        self.subtitle_style = subtitle_style
        self.translate_enabled = translate_enabled
        self.translate_config = translate_config
        self.use_audio_preprocessing = use_audio_preprocessing
        self.parallel_count = parallel_count
    
    def run(self):
        total_videos = len(self.video_paths)
        successful_videos = []
        failed_videos = []
        
        for idx, video_path in enumerate(self.video_paths, 1):
            try:
                from pathlib import Path
                video_name = Path(video_path).name
                
                self.progress.emit(f"正在处理视频 {idx}/{total_videos}: {video_name}")
                
                # 第一步：生成字幕文件（不嵌入视频）
                srt_path = self.generator.process_video(
                    video_path=video_path,
                    language=self.language,
                    output_dir=self.output_dir,
                    embed_subtitles=False,  # 先不嵌入，等翻译后再嵌入
                    threads=self.threads,
                    gpu_layers=self.gpu_layers,
                    subtitle_style=None,  # 暂不需要样式
                    use_audio_preprocessing=self.use_audio_preprocessing,
                    parallel_count=self.parallel_count
                )
                
                # 第二步：如果启用翻译，翻译字幕文件
                if self.translate_enabled and self.translate_config:
                    self.progress.emit(f"正在翻译字幕 ({idx}/{total_videos})...")
                    try:
                        translate_srt(
                            srt_path=srt_path,
                            api_url=self.translate_config['api_url'],
                            api_key=self.translate_config['api_key'],
                            model=self.translate_config['model'],
                            target_language=self.translate_config['target_language'],
                            translation_on_top=self.translate_config['translation_on_top'],
                            translation_mode=self.translate_config.get('translation_mode', 'dual')
                        )
                        self.progress.emit(f"翻译完成 ({idx}/{total_videos})！")
                    except Exception as e:
                        failed_videos.append((video_name, f"翻译失败: {str(e)}"))
                        continue
                
                # 第三步：如果需要嵌入字幕，使用翻译后的字幕嵌入到视频
                if self.embed_subtitles:
                    self.progress.emit(f"正在嵌入字幕到视频 ({idx}/{total_videos})...")
                    try:
                        video_path_obj = Path(video_path)
                        output_dir = Path(self.output_dir) if self.output_dir else video_path_obj.parent
                        output_video = output_dir / f"{video_path_obj.stem}_with_subtitles{video_path_obj.suffix}"
                        
                        # 使用字幕样式嵌入
                        subtitle_style = self.subtitle_style if self.subtitle_style else {}
                        
                        self.generator.add_subtitles_to_video(
                            str(video_path_obj),
                            srt_path,
                            str(output_video),
                            **subtitle_style
                        )
                        self.progress.emit(f"字幕嵌入完成 ({idx}/{total_videos})！")
                    except Exception as e:
                        # 嵌入失败不影响 SRT 文件，继续
                        print(f"警告：嵌入字幕失败: {e}")
                
                successful_videos.append((video_name, srt_path))
                
            except Exception as e:
                failed_videos.append((video_name, str(e)))
        
        # 发送完成信号，附带成功和失败的统计
        if failed_videos:
            error_summary = f"批量处理完成！\n\n成功: {len(successful_videos)}/{total_videos}\n失败: {len(failed_videos)}/{total_videos}\n\n失败列表:\n"
            for name, error in failed_videos:
                error_summary += f"• {name}: {error}\n"
            if successful_videos:
                error_summary += f"\n成功生成的字幕文件:\n"
                for name, srt_path in successful_videos:
                    error_summary += f"• {name}\n"
            self.error.emit(error_summary)
        else:
            # 全部成功
            if len(successful_videos) == 1:
                self.finished.emit(successful_videos[0][1])
            else:
                summary = f"批量处理完成！成功处理 {len(successful_videos)} 个视频\n\n字幕文件:\n"
                for name, srt_path in successful_videos:
                    summary += f"• {name}\n"
                self.finished.emit(summary)


class ModernWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Popin - 智能字幕生成器")
        self.setFixedSize(900, 1000)  # 稍微加宽以容纳更多内容
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 自动检测 whisper.cpp
        self.detected_whisper_cli = None
        self.detected_models = []
        self.auto_detect_whisper_cpp()
        
        self.init_ui()
        self.apply_styles()
        
        # 加载上次的设置
        self.load_settings()
        
        # 设置圆角
        self.set_rounded_corners()
        
        # 用于窗口拖动
        self.dragging = False
        self.drag_position = None
    
    def change_ui_language(self):
        """切换界面语言"""
        # 映射界面显示到语言代码
        lang_display = self.ui_language.currentText()
        lang_map = {'中文': 'zh_CN', 'English': 'en_US', '日本語': 'ja_JP'}
        language_code = lang_map.get(lang_display, 'zh_CN')
        
        # 保存到配置
        self.config_manager.set('app', 'language', language_code)
        self.config_manager.save_config()
        
        # 切换语言管理器的语言
        lang_manager = get_language_manager()
        lang_manager.change_language(language_code)
        
        # 提示用户重启
        QMessageBox.information(
            self, 
            "语言已更改" if language_code == 'zh_CN' else ("Language Changed" if language_code == 'en_US' else "言語が変更されました"),
            "请重启程序以应用新的界面语言。\n\nPlease restart the application to apply the new language.\n\n新しい言語を適用するにはアプリケーションを再起動してください。"
        )
    
    def closeEvent(self, event):
        """窗口关闭事件 - 保存配置"""
        self.save_current_settings()
        event.accept()
    
    def load_ai_config(self):
        """加载AI配置"""
        return load_ai_config()
    
    def set_rounded_corners(self):
        """设置圆角窗口"""
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 用于拖动窗口"""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
        except Exception as e:
            print(f"鼠标事件错误: {e}")
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖动窗口"""
        try:
            if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
                self.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()
        except Exception as e:
            print(f"鼠标移动错误: {e}")
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        try:
            self.dragging = False
        except Exception as e:
            print(f"鼠标释放错误: {e}")
    
    def auto_detect_whisper_cpp(self):
        """自动检测 whisper.cpp 配置"""
        search_paths = [
            Path.cwd() / "whisper.cpp",
            Path.cwd().parent / "whisper.cpp",
        ]
        
        for base_path in search_paths:
            if not base_path.exists():
                continue
            
            # 查找主程序
            possible_cli_paths = [
                base_path / "build" / "bin" / "Release" / "whisper-cli.exe",
                base_path / "whisper-cli.exe",
                base_path / "whisper-cli",
            ]
            
            for cli_path in possible_cli_paths:
                if cli_path.exists():
                    self.detected_whisper_cli = str(cli_path)
                    break
            
            # 查找模型
            models_dir = base_path / "models"
            if models_dir.exists():
                model_files = list(models_dir.glob("ggml-*.bin"))
                self.detected_models = [str(m) for m in sorted(model_files)]
            
            if self.detected_whisper_cli:
                break
    
    def init_ui(self):
        """初始化界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加顶部标题栏（用于拖动和关闭）
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("background-color: transparent;")
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(10, 5, 10, 5)
        
        # 标题
        title_label = QLabel("视频自动字幕生成器")
        title_label.setStyleSheet("color: #64B5F6; font-weight: bold; font-size: 11pt;")
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()
        
        # 最小化按钮
        min_btn = QPushButton("─")
        min_btn.setFixedSize(30, 30)
        min_btn.setStyleSheet("""
            QPushButton {
                background-color: #E3F2FD;
                color: #64B5F6;
                border-radius: 15px;
                font-size: 16pt;
                padding-bottom: 5px;
            }
            QPushButton:hover {
                background-color: #BBDEFB;
            }
        """)
        min_btn.clicked.connect(self.showMinimized)
        title_bar_layout.addWidget(min_btn)
        
        # 关闭按钮
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFEBEE;
                color: #F44336;
                border-radius: 15px;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #F44336;
                color: white;
            }
        """)
        close_btn.clicked.connect(self.close)
        title_bar_layout.addWidget(close_btn)
        
        main_layout.addWidget(title_bar)
        
        # 主标题
        title = QLabel(" 视频自动字幕生成器")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        main_layout.addWidget(title)
        
        # 创建Tab控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #D6EAFF;
                border-radius: 8px;
                background-color: #FFFFFF;
            }
            QTabBar::tab {
                background-color: #F5F9FF;
                color: #333333;
                border: 2px solid #D6EAFF;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px 30px;
                margin-right: 5px;
                font-weight: bold;
                font-size: 11pt;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #64B5F6;
                border-bottom: 2px solid #FFFFFF;
            }
            QTabBar::tab:hover {
                background-color: #E3F2FD;
            }
        """)
        
        # 主界面Tab
        main_tab = QWidget()
        self.init_main_tab(main_tab)
        self.tab_widget.addTab(main_tab, "字幕生成")
        
        # AI 设置Tab
        settings_tab = QWidget()
        self.init_settings_tab(settings_tab)
        self.tab_widget.addTab(settings_tab, "AI 设置")
        
        # 高级配置Tab  
        advanced_tab = QWidget()
        self.init_advanced_tab(advanced_tab)
        self.tab_widget.addTab(advanced_tab, "高级配置")
        
        main_layout.addWidget(self.tab_widget)
    
    def init_main_tab(self, tab_widget):
        """初始化主界面标签页"""
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # whisper.cpp 配置已移至"高级配置"标签页
        
        # 视频配置组
        video_group = QGroupBox("视频配置")
        video_layout = QVBoxLayout()
        
        # 视频文件
        video_file_layout = QHBoxLayout()
        video_file_label = QLabel("视频文件:")
        video_file_label.setFixedWidth(80)
        video_file_layout.addWidget(video_file_label)
        self.video_path = QLineEdit()
        self.video_path.setFixedWidth(600)  # 固定宽度
        video_file_layout.addWidget(self.video_path)
        browse_video = QPushButton("选择文件")
        browse_video.clicked.connect(self.browse_video)
        browse_video.setFixedWidth(120)
        video_file_layout.addWidget(browse_video)
        video_file_layout.addStretch()
        video_layout.addLayout(video_file_layout)
        
        # 输出目录
        output_layout = QHBoxLayout()
        output_label = QLabel("输出目录:")
        output_label.setFixedWidth(80)
        output_layout.addWidget(output_label)
        self.output_dir = QLineEdit()
        self.output_dir.setFixedWidth(600)  # 固定宽度
        output_layout.addWidget(self.output_dir)
        browse_output = QPushButton("选择目录")
        browse_output.clicked.connect(self.browse_output)
        browse_output.setFixedWidth(120)
        output_layout.addWidget(browse_output)
        output_layout.addStretch()
        video_layout.addLayout(output_layout)
        
        # 语言选择（必选）
        lang_layout = QHBoxLayout()
        lang_label = QLabel("语言:")
        lang_label.setStyleSheet("font-weight: bold;")
        lang_label.setFixedWidth(80)
        lang_layout.addWidget(lang_label)
        self.language = QComboBox()
        self.language.addItems([
            "请选择语言 ⚠",
            "中文 (zh)",
            "日语 (ja)",
            "英语 (en)",
            "韩语 (ko)",
            "法语 (fr)",
            "德语 (de)",
            "西班牙语 (es)",
            "俄语 (ru)"
        ])
        self.language.setCurrentIndex(0)
        self.language.setMinimumWidth(200)
        lang_layout.addWidget(self.language)
        warning = QLabel("← 必须选择！")
        warning.setStyleSheet("color: #F44336; font-weight: bold; font-size: 11pt;")
        lang_layout.addWidget(warning)
        lang_layout.addStretch()
        video_layout.addLayout(lang_layout)
        
        # 嵌入字幕
        self.embed_checkbox = QCheckBox("✓ 将字幕嵌入视频（生成新视频文件）")
        self.embed_checkbox.setChecked(True)
        self.embed_checkbox.stateChanged.connect(self.toggle_style_options)
        video_layout.addWidget(self.embed_checkbox)
        
        # 音频预处理选项已移至"高级配置"标签页
        
        video_group.setLayout(video_layout)
        layout.addWidget(video_group)
        
        # 字幕样式组
        self.style_group = QGroupBox("字幕样式")
        style_layout = QVBoxLayout()
        
        # 初始化颜色
        self.primary_color = '#FFFFFF'
        self.outline_color = '#000000'
        
        # 第一行：字体大小和字体选择
        font_row1 = QHBoxLayout()
        font_row1.addWidget(QLabel("字体大小:"))
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        self.font_size.setValue(10)
        self.font_size.setFixedWidth(80)
        font_row1.addWidget(self.font_size)
        
        font_row1.addSpacing(20)
        font_row1.addWidget(QLabel("字体:"))
        self.font_name = QComboBox()
        
        # 默认字体列表
        default_fonts = ["Arial", "Microsoft YaHei", "SimHei", "SimSun"]
        self.font_name.addItems(default_fonts)
        
        # 自动加载 fonts 目录中的字体
        self.load_custom_fonts()
        
        self.font_name.setFixedWidth(150)
        font_row1.addWidget(self.font_name)
        
        # 导入字体按钮
        import_font_btn = QPushButton("导入字体")
        import_font_btn.setFixedWidth(100)
        import_font_btn.clicked.connect(self.import_custom_font)
        font_row1.addWidget(import_font_btn)
        
        font_row1.addStretch()
        style_layout.addLayout(font_row1)
        
        # 第二行：颜色设置
        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("字幕颜色:"))
        self.primary_color_btn = QPushButton()
        self.primary_color_btn.setFixedSize(80, 30)
        self.primary_color_btn.clicked.connect(self.choose_primary_color)
        color_row.addWidget(self.primary_color_btn)
        
        color_row.addSpacing(20)
        
        # 启用描边复选框
        self.outline_enabled_checkbox = QCheckBox("启用描边")
        self.outline_enabled_checkbox.setChecked(True)
        self.outline_enabled_checkbox.stateChanged.connect(self.toggle_outline_controls)
        color_row.addWidget(self.outline_enabled_checkbox)
        
        color_row.addSpacing(10)
        self.outline_color_label = QLabel("描边颜色:")
        color_row.addWidget(self.outline_color_label)
        self.outline_color_btn = QPushButton()
        self.outline_color_btn.setFixedSize(80, 30)
        self.outline_color_btn.clicked.connect(self.choose_outline_color)
        color_row.addWidget(self.outline_color_btn)
        
        color_row.addSpacing(20)
        self.outline_width_label = QLabel("描边宽度:")
        color_row.addWidget(self.outline_width_label)
        self.outline_width = QSpinBox()
        self.outline_width.setRange(1, 5)
        self.outline_width.setValue(2)
        self.outline_width.setFixedWidth(60)
        color_row.addWidget(self.outline_width)
        
        color_row.addStretch()
        style_layout.addLayout(color_row)
        
        # 第三行：边距和样式
        margin_layout = QHBoxLayout()
        margin_layout.addWidget(QLabel("底部边距:"))
        self.margin_v = QSpinBox()
        self.margin_v.setRange(0, 200)
        self.margin_v.setValue(25)
        self.margin_v.setFixedWidth(80)
        margin_layout.addWidget(self.margin_v)
        
        margin_layout.addSpacing(20)
        self.bold_checkbox = QCheckBox("粗体")
        margin_layout.addWidget(self.bold_checkbox)
        
        self.italic_checkbox = QCheckBox("斜体")
        margin_layout.addWidget(self.italic_checkbox)
        
        self.shadow_checkbox = QCheckBox("阴影")
        margin_layout.addWidget(self.shadow_checkbox)
        
        margin_layout.addStretch()
        style_layout.addLayout(margin_layout)
        
        # 预览功能已取消
        
        self.style_group.setLayout(style_layout)
        layout.addWidget(self.style_group)
        
        # 翻译配置组
        translate_group = QGroupBox("字幕翻译 (可选)")
        translate_layout = QVBoxLayout()
        
        # 启用翻译和配置按钮
        top_translate_layout = QHBoxLayout()
        self.translate_checkbox = QCheckBox("✓ 启用字幕翻译")
        self.translate_checkbox.stateChanged.connect(self.toggle_translate_options)
        top_translate_layout.addWidget(self.translate_checkbox)
        
        top_translate_layout.addStretch()
        translate_layout.addLayout(top_translate_layout)
        
        # 加载AI配置
        self.ai_config = self.load_ai_config()
        
        # 显示当前配置状态
        self.config_status_label = QLabel()
        self.update_config_status()
        translate_layout.addWidget(self.config_status_label)
        
        # 翻译设置
        trans_settings_layout = QHBoxLayout()
        trans_settings_layout.addWidget(QLabel("目标语言:"))
        self.target_language = QComboBox()
        self.target_language.addItems(["中文", "英语", "日语", "韩语", "法语", "德语", "西班牙语", "俄语"])
        self.target_language.setFixedWidth(150)
        trans_settings_layout.addWidget(self.target_language)
        
        trans_settings_layout.addSpacing(30)
        trans_settings_layout.addWidget(QLabel("显示模式:"))
        self.translation_mode = QComboBox()
        self.translation_mode.addItems(["双行显示（原文+翻译）", "只显示翻译", "只显示原文"])
        self.translation_mode.setFixedWidth(200)
        self.translation_mode.currentIndexChanged.connect(self.toggle_translation_position)
        trans_settings_layout.addWidget(self.translation_mode)
        trans_settings_layout.addStretch()
        translate_layout.addLayout(trans_settings_layout)
        
        # 显示顺序（仅在双行模式下显示）
        self.position_layout = QHBoxLayout()
        self.position_layout.addWidget(QLabel("显示顺序:"))
        self.translation_position = QComboBox()
        self.translation_position.addItems(["翻译在上，原文在下", "原文在上，翻译在下"])
        self.translation_position.setFixedWidth(200)
        self.position_layout.addWidget(self.translation_position)
        self.position_layout.addStretch()
        translate_layout.addLayout(self.position_layout)
        
        translate_group.setLayout(translate_layout)
        self.translate_group = translate_group
        layout.addWidget(translate_group)
        self.toggle_translate_options()  # 初始隐藏
        
        # 开始按钮
        self.start_btn = QPushButton("开始生成字幕")
        self.start_btn.setFixedHeight(50)
        self.start_btn.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self.start_btn.clicked.connect(self.start_processing)
        layout.addWidget(self.start_btn)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
    
    def init_settings_tab(self, tab_widget):
        """初始化设置标签页"""
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title = QLabel("AI 翻译 API 配置")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 说明
        desc = QLabel("配置 OpenAI 或 Anthropic 兼容的 API 用于字幕翻译\n配置会自动保存到 ai_config.json")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #666666;")
        layout.addWidget(desc)
        
        layout.addSpacing(20)
        
        # API 地址
        api_url_layout = QHBoxLayout()
        api_url_label = QLabel("API 地址:")
        api_url_label.setFixedWidth(100)
        api_url_layout.addWidget(api_url_label)
        self.settings_api_url = QLineEdit()
        api_url_layout.addWidget(self.settings_api_url)
        layout.addLayout(api_url_layout)
        
        # API Key
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel("API Key:")
        api_key_label.setFixedWidth(100)
        api_key_layout.addWidget(api_key_label)
        self.settings_api_key = QLineEdit()
        self.settings_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.settings_api_key.setPlaceholderText("输入您的 API Key")
        api_key_layout.addWidget(self.settings_api_key)
        
        # 显示/隐藏按钮
        self.show_key_btn = QPushButton("👁")
        self.show_key_btn.setFixedWidth(40)
        self.show_key_btn.setCheckable(True)
        self.show_key_btn.clicked.connect(self.toggle_key_visibility)
        api_key_layout.addWidget(self.show_key_btn)
        layout.addLayout(api_key_layout)
        
        # 模型选择 - 使用选项卡
        model_group = QGroupBox("选择模型")
        model_group_layout = QVBoxLayout()
        
        self.model_tabs = QTabWidget()
        self.model_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #E3F2FD;
                border-radius: 6px;
                background-color: #FFFFFF;
                padding: 10px;
            }
            QTabBar::tab {
                background-color: #F5F9FF;
                color: #666666;
                border: 2px solid #E3F2FD;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 20px;
                margin-right: 3px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #64B5F6;
                border-bottom: 2px solid #FFFFFF;
            }
            QTabBar::tab:hover {
                background-color: #E3F2FD;
            }
        """)
        
        # OpenAI 选项卡
        openai_tab = QWidget()
        openai_layout = QVBoxLayout(openai_tab)
        openai_layout.setContentsMargins(10, 10, 10, 10)
        
        self.openai_models = QComboBox()
        self.openai_models.addItems([
            "gpt-5-4-mini)",
            "gpt-5-4",
            "gpt-5-5"
        ])
        openai_layout.addWidget(QLabel("选择 OpenAI 模型:"))
        openai_layout.addWidget(self.openai_models)
        openai_layout.addStretch()
        
        # Anthropic 选项卡
        anthropic_tab = QWidget()
        anthropic_layout = QVBoxLayout(anthropic_tab)
        anthropic_layout.setContentsMargins(10, 10, 10, 10)
        
        self.anthropic_models = QComboBox()
        self.anthropic_models.addItems([
            "claude-4-5-sonnet (推荐)",
            "claude-4-5-haiku"
        ])
        anthropic_layout.addWidget(QLabel("选择 Claude 模型:"))
        anthropic_layout.addWidget(self.anthropic_models)
        anthropic_layout.addStretch()
        
        # 自定义选项卡
        custom_tab = QWidget()
        custom_layout = QVBoxLayout(custom_tab)
        custom_layout.setContentsMargins(10, 10, 10, 10)
        
        self.custom_model = QLineEdit()
        self.custom_model.setPlaceholderText("输入自定义模型名称，如: deepseek-chat")
        custom_layout.addWidget(QLabel("自定义模型:"))
        custom_layout.addWidget(self.custom_model)
        custom_layout.addStretch()
        
        self.model_tabs.addTab(openai_tab, "OpenAI")
        self.model_tabs.addTab(anthropic_tab, "Anthropic")
        self.model_tabs.addTab(custom_tab, "自定义")
        
        model_group_layout.addWidget(self.model_tabs)
        model_group.setLayout(model_group_layout)
        layout.addWidget(model_group)
        
        layout.addSpacing(20)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        test_btn = QPushButton("测试连接")
        test_btn.setFixedWidth(140)
        test_btn.clicked.connect(self.test_api_connection)
        button_layout.addWidget(test_btn)
        
        save_btn = QPushButton("保存配置")
        save_btn.setFixedWidth(140)
        save_btn.clicked.connect(self.save_ai_config)
        button_layout.addWidget(save_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
        
        # 加载配置
        self.load_settings_values()
    
    def load_settings_values(self):
        """加载配置值到设置页面"""
        config = self.load_ai_config()
        self.settings_api_url.setText(config.get("api_url", "https://api.openai.com/v1"))
        self.settings_api_key.setText(config.get("api_key", ""))
        
        model = config.get("model", "gpt-5-4-mini")
        
        # 根据模型名称设置对应的选项卡和下拉菜单
        if model.startswith("gpt-"):
            self.model_tabs.setCurrentIndex(0)  # OpenAI
            # 查找并设置模型
            for i in range(self.openai_models.count()):
                if model in self.openai_models.itemText(i):
                    self.openai_models.setCurrentIndex(i)
                    break
        elif model.startswith("claude-"):
            self.model_tabs.setCurrentIndex(1)  # Anthropic
            # 查找并设置模型
            for i in range(self.anthropic_models.count()):
                if model in self.anthropic_models.itemText(i):
                    self.anthropic_models.setCurrentIndex(i)
                    break
        else:
            self.model_tabs.setCurrentIndex(2)  # 自定义
            self.custom_model.setText(model)
    
    def get_selected_model(self):
        """获取当前选择的模型"""
        current_tab = self.model_tabs.currentIndex()
        
        if current_tab == 0:  # OpenAI
            model_text = self.openai_models.currentText()
            # 提取模型名称（去掉括号说明）
            return model_text.split(" ")[0]
        elif current_tab == 1:  # Anthropic
            model_text = self.anthropic_models.currentText()
            return model_text.split(" ")[0]
        else:  # 自定义
            return self.custom_model.text().strip()
    
    def toggle_key_visibility(self):
        """切换 API Key 可见性"""
        if self.show_key_btn.isChecked():
            self.settings_api_key.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_btn.setText("[\]")
        else:
            self.settings_api_key.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_btn.setText("[-]")
    
    def test_api_connection(self):
        """测试 API 连接"""
        api_url = self.settings_api_url.text().strip()
        api_key = self.settings_api_key.text().strip()
        model = self.get_selected_model()
        
        if not api_key:
            QMessageBox.warning(self, "警告", "请先输入 API Key")
            return
        
        if not model:
            QMessageBox.warning(self, "警告", "请选择或输入模型名称")
            return
        
        try:
            # 判断是 Anthropic 还是 OpenAI
            is_anthropic = 'anthropic' in api_url.lower() or model.startswith('claude')
            
            if is_anthropic:
                response = requests.post(
                    f"{api_url.rstrip('/')}/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": model,
                        "max_tokens": 10,
                        "messages": [{"role": "user", "content": "Hi"}]
                    },
                    timeout=10
                )
            else:
                response = requests.post(
                    f"{api_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": "Hi"}],
                        "max_tokens": 10
                    },
                    timeout=10
                )
            
            if response.status_code == 200:
                QMessageBox.information(self, "成功", "✓ API 连接测试成功！")
            else:
                QMessageBox.warning(self, "失败", f"API 返回错误:\n状态码 {response.status_code}\n{response.text[:200]}")
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"连接测试失败:\n{str(e)}")
    
    def save_ai_config(self):
        """保存AI配置"""
        model = self.get_selected_model()
        
        if not model:
            QMessageBox.warning(self, "警告", "请选择或输入模型名称")
            return
        
        config = {
            "api_url": self.settings_api_url.text().strip(),
            "api_key": self.settings_api_key.text().strip(),
            "model": model
        }
        
        try:
            with open("ai_config.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # 重新加载配置
            self.ai_config = self.load_ai_config()
            self.update_config_status()
            
            QMessageBox.information(self, "成功", "✓ 配置已保存！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败:\n{str(e)}")
    
    def apply_styles(self):
        """应用现代化样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
                border: 2px solid #D6EAFF;
            }
            QWidget {
                background-color: #FFFFFF;
                color: #333333;
                font-family: "Microsoft YaHei";
                font-size: 10pt;
            }
            QGroupBox {
                background-color: #F5F9FF;
                border: 2px solid #D6EAFF;
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #64B5F6;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                background-color: #FFFFFF;
            }
            QPushButton {
                background-color: #64B5F6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
            QPushButton:pressed {
                background-color: #2196F3;
            }
            QPushButton:disabled {
                background-color: #BBDEFB;
                color: #90CAF9;
            }
            QLineEdit, QComboBox, QSpinBox {
                border: 2px solid #E3F2FD;
                border-radius: 8px;
                padding: 6px 10px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 2px solid #64B5F6;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #64B5F6;
                margin-right: 10px;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #B3D9FF;
                background-color: #FFFFFF;
            }
            QCheckBox::indicator:checked {
                background-color: #64B5F6;
                border-color: #64B5F6;
                image: none;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0px;
                border: none;
            }
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #E3F2FD;
            }
            QProgressBar::chunk {
                background-color: #64B5F6;
                border-radius: 4px;
            }
            QLabel {
                color: #333333;
            }
        """)
    
    def toggle_style_options(self):
        """切换样式选项显示"""
        self.style_group.setVisible(self.embed_checkbox.isChecked())
    
    def update_config_status(self):
        """更新配置状态显示"""
        if self.ai_config.get('api_key'):
            masked_key = self.ai_config['api_key'][:8] + "..." if len(self.ai_config['api_key']) > 8 else "***"
            status_text = f"✓ 已配置 | 模型: {self.ai_config.get('model', 'N/A')}"
            self.config_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            status_text = "⚠ 未配置 API Key，请切换到 'AI 设置' 标签页进行配置"
            self.config_status_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        self.config_status_label.setText(status_text)
    
    def toggle_translate_options(self):
        """切换翻译选项显示"""
        enabled = self.translate_checkbox.isChecked()
        self.target_language.setEnabled(enabled)
        self.translation_mode.setEnabled(enabled)
        self.translation_position.setEnabled(enabled)
        # 初始化时根据模式设置顺序选项的可见性
        if enabled:
            self.toggle_translation_position()
    
    def toggle_translation_position(self):
        """根据显示模式切换显示顺序选项"""
        mode = self.translation_mode.currentText()
        # 只有在"双行显示"模式下才显示顺序选项
        is_dual = mode == "双行显示（原文+翻译）"
        
        # 隐藏或显示所有position_layout中的控件
        for i in range(self.position_layout.count()):
            widget = self.position_layout.itemAt(i).widget()
            if widget:
                widget.setVisible(is_dual)
    
    def get_translation_mode(self):
        """获取翻译模式"""
        mode_text = self.translation_mode.currentText()
        if "只显示翻译" in mode_text:
            return "translation_only"
        elif "只显示原文" in mode_text:
            return "original_only"
        else:
            return "dual"
    
    def browse_whisper_cpp(self):
        """选择 whisper.cpp 主程序"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "选择 whisper.cpp 主程序", "",
            "可执行文件 (*.exe);;所有文件 (*)"
        )
        if file_name:
            self.whisper_path.setText(file_name)
    
    def browse_model(self):
        """选择模型文件"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "选择模型文件", "",
            "模型文件 (*.bin);;所有文件 (*)"
        )
        if file_name:
            self.model_path.setCurrentText(file_name)
    
    def browse_video(self):
        """选择视频文件（支持多选）"""
        file_names, _ = QFileDialog.getOpenFileNames(
            self, "选择视频文件（可多选）", "",
            "视频文件 (*.mp4 *.avi *.mkv *.mov);;所有文件 (*)"
        )
        if file_names:
            # 如果选择了多个文件，用分号分隔
            if len(file_names) > 1:
                self.video_path.setText("; ".join(file_names))
                # 显示提示
                QMessageBox.information(
                    self, 
                    "批量处理", 
                    f"已选择 {len(file_names)} 个视频文件\n将依次处理每个文件"
                )
            else:
                self.video_path.setText(file_names[0])
            
            # 设置输出目录为第一个文件的父目录
            if not self.output_dir.text():
                self.output_dir.setText(str(Path(file_names[0]).parent))
    
    def browse_output(self):
        """选择输出目录"""
        dir_name = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_name:
            self.output_dir.setText(dir_name)
    
    def preview_subtitle(self):
        """预览字幕"""
        video_path = self.video_path.text()
        if not video_path or not Path(video_path).exists():
            QMessageBox.warning(self, "警告", "请先选择有效的视频文件")
            return
        
        output_dir = self.output_dir.text() or str(Path(video_path).parent)
        preview_image = Path(output_dir) / "subtitle_preview.jpg"
        
        # 清理旧的预览图片
        if preview_image.exists():
            try:
                preview_image.unlink()
            except:
                pass
        
        try:
            import subprocess
            import random
            
            # 获取视频时长
            probe_cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ]
            result = subprocess.run(probe_cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            duration = float(result.stdout.strip())
            
            # 随机选择一个时间点（避开开头和结尾各10%）
            random_time = random.uniform(duration * 0.1, duration * 0.9)
            
            # 构建字幕样式
            font_size = self.font_size.value()
            font_name = self.font_name.currentText()
            margin_v = self.margin_v.value()
            
            # 构建 drawtext 滤镜
            text_filter = f"drawtext=text='TEST TEST TEST TEST':fontfile='C\\:/Windows/Fonts/arial.ttf'"
            if font_name == "Microsoft YaHei":
                text_filter = f"drawtext=text='TEST TEST TEST TEST':fontfile='C\\:/Windows/Fonts/msyh.ttc'"
            elif font_name == "SimHei":
                text_filter = f"drawtext=text='TEST TEST TEST TEST':fontfile='C\\:/Windows/Fonts/simhei.ttf'"
            elif font_name == "SimSun":
                text_filter = f"drawtext=text='TEST TEST TEST TEST':fontfile='C\\:/Windows/Fonts/simsun.ttc'"
            else:
                text_filter = f"drawtext=text='TEST TEST TEST TEST':fontfile='C\\:/Windows/Fonts/arial.ttf'"
            
            text_filter += f":fontsize={font_size}:fontcolor=white:borderw=2:bordercolor=black"
            text_filter += f":x=(w-text_w)/2:y=h-{margin_v}-text_h"
            
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-ss', str(random_time),
                '-i', video_path,
                '-vf', text_filter,
                '-vframes', '1',
                str(preview_image)
            ]
            
            subprocess.run(ffmpeg_cmd, capture_output=True, encoding='utf-8', errors='replace', check=True)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"预览失败:\n{str(e)}")
    
    def get_model_path(self):
        """获取完整的模型路径"""
        model_text = self.model_path.currentText()
        # 如果是相对路径（只有文件名）
        if not Path(model_text).is_absolute() and self.detected_models:
            for full_path in self.detected_models:
                if Path(full_path).name == model_text:
                    return full_path
        return model_text
    
    def start_processing(self):
        """开始处理"""
        # 验证输入
        if not self.video_path.text():
            QMessageBox.warning(self, "警告", "请选择视频文件")
            return
        
        if not self.whisper_path.text():
            QMessageBox.warning(self, "警告", "请选择 whisper.cpp 主程序")
            return
        
        if not self.model_path.currentText():
            QMessageBox.warning(self, "警告", "请选择模型文件")
            return
        
        # 强制选择语言
        if self.language.currentIndex() == 0:
            QMessageBox.critical(self, "错误", "请选择视频的语言！\n\n这是必选项，否则识别会出错。")
            return
        
        # 检查翻译配置
        translate_enabled = self.translate_checkbox.isChecked()
        translate_config = None
        if translate_enabled:
            # 重新加载配置以获取最新值
            self.ai_config = self.load_ai_config()
            
            if not self.ai_config.get('api_key'):
                QMessageBox.warning(self, "警告", "启用翻译需要先配置 API Key\n\n请点击 'AI 配置' 按钮进行配置")
                return
            
            translate_config = {
                'api_url': self.ai_config['api_url'],
                'api_key': self.ai_config['api_key'],
                'model': self.ai_config['model'],
                'target_language': self.target_language.currentText(),
                'translation_on_top': self.translation_position.currentIndex() == 0,
                'translation_mode': self.get_translation_mode()
            }
        
        # 获取语言代码
        lang_text = self.language.currentText()
        lang_code = lang_text.split("(")[1].split(")")[0] if "(" in lang_text else None
        
        # 解析视频路径（支持多个视频，分号分隔）
        video_paths = [p.strip() for p in self.video_path.text().split(";") if p.strip()]
        
        # 禁用界面
        self.start_btn.setEnabled(False)
        self.start_btn.setText("处理中...")
        self.progress_bar.setRange(0, 0)  # 无限进度
        if len(video_paths) > 1:
            self.status_label.setText(f"正在批量处理 {len(video_paths)} 个视频...")
        else:
            self.status_label.setText("正在处理...")
        
        # 准备参数
        gpu_backend = self.gpu_backend.currentText().lower()
        if gpu_backend == "cpu":
            gpu_backend = None
        
        subtitle_style = None
        if self.embed_checkbox.isChecked():
            # 转换十六进制颜色为 ASS 格式 (&HBBGGRR)
            def hex_to_ass_color(hex_color):
                """将 #RRGGBB 转换为 ASS 格式 &HBBGGRR"""
                hex_color = hex_color.lstrip('#')
                r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
                return f"&H{b:02X}{g:02X}{r:02X}"
            
            # 如果禁用描边，设置宽度为0
            outline_width = self.outline_width.value() if self.outline_enabled_checkbox.isChecked() else 0
            
            subtitle_style = {
                'font_size': self.font_size.value(),
                'font_name': self.font_name.currentText(),
                'margin_v': self.margin_v.value(),
                'margin_h': 0,
                'primary_color': hex_to_ass_color(self.primary_color),
                'outline_color': hex_to_ass_color(self.outline_color),
                'outline_width': outline_width,
                'bold': self.bold_checkbox.isChecked(),
                'italic': self.italic_checkbox.isChecked()
            }
        
        try:
            generator = VideoSubtitleGeneratorCpp(
                whisper_cpp_path=self.whisper_path.text(),
                model_path=self.get_model_path(),
                gpu_backend=gpu_backend
            )
            
            # 创建处理线程（传入视频路径列表）
            self.thread = ProcessThread(
                generator=generator,
                video_paths=video_paths,
                language=lang_code,
                output_dir=self.output_dir.text() or None,
                embed_subtitles=self.embed_checkbox.isChecked(),
                threads=self.threads.value(),
                gpu_layers=1 if gpu_backend else 0,
                subtitle_style=subtitle_style,
                translate_enabled=translate_enabled,
                translate_config=translate_config,
                use_audio_preprocessing=self.audio_preprocess_checkbox.isChecked(),
                parallel_count=self.parallel_count.value()
            )
            
            self.thread.finished.connect(self.on_finished)
            self.thread.error.connect(self.on_error)
            self.thread.progress.connect(self.on_progress)
            self.thread.start()
            
        except Exception as e:
            self.on_error(str(e))
    
    def on_progress(self, message):
        """更新进度"""
        self.status_label.setText(message)
    
    def on_finished(self, result):
        """处理完成"""
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.status_label.setText("✓ 处理完成！")
        self.start_btn.setEnabled(True)
        self.start_btn.setText("开始生成字幕")
        
        # 判断是单个文件还是批量处理
        if "\n" in result:
            # 批量处理结果（包含换行符）
            QMessageBox.information(self, "批量处理完成", result)
        else:
            # 单个文件处理完成
            QMessageBox.information(self, "成功", f"字幕生成完成！\n\n文件位置:\n{result}")
    
    def on_error(self, error_msg):
        """处理错误"""
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        # 判断是否为批量处理的部分失败
        if "批量处理完成" in error_msg and "成功:" in error_msg:
            self.status_label.setText("⚠ 部分视频处理失败")
            QMessageBox.warning(self, "批量处理完成（部分失败）", error_msg)
        else:
            self.status_label.setText("✗ 处理失败")
            QMessageBox.critical(self, "错误", error_msg)
        
        self.start_btn.setEnabled(True)
        self.start_btn.setText("开始生成字幕")
        
        QMessageBox.critical(self, "错误", f"处理失败:\n\n{error_msg}")
    
    def init_advanced_tab(self, tab_widget):
        """初始化高级配置标签页"""
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title = QLabel("高级配置")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # whisper.cpp 配置组
        config_group = QGroupBox("Whisper.cpp 配置")
        config_layout = QVBoxLayout()
        
        # 检测状态
        if self.detected_whisper_cli:
            status = QLabel("✓ 已自动检测到 whisper.cpp 配置")
            status.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            status = QLabel("⚠ 未检测到 whisper.cpp，请在下方配置")
            status.setStyleSheet("color: #FF9800; font-weight: bold;")
        config_layout.addWidget(status)
        
        # 主程序路径
        prog_layout = QHBoxLayout()
        prog_label = QLabel("主程序:")
        prog_label.setFixedWidth(100)
        prog_layout.addWidget(prog_label)
        self.whisper_path = QLineEdit(self.detected_whisper_cli or "")
        self.whisper_path.setFixedWidth(500)
        prog_layout.addWidget(self.whisper_path)
        browse_prog = QPushButton("浏览")
        browse_prog.setFixedWidth(100)
        browse_prog.clicked.connect(self.browse_whisper_cpp)
        prog_layout.addWidget(browse_prog)
        prog_layout.addStretch()
        config_layout.addLayout(prog_layout)
        
        # 模型文件
        model_layout = QHBoxLayout()
        model_label = QLabel("模型文件:")
        model_label.setFixedWidth(100)
        model_layout.addWidget(model_label)
        self.model_path = QComboBox()
        if self.detected_models:
            self.model_path.addItems([Path(m).name for m in self.detected_models])
            self.model_path.setCurrentIndex(0)
        self.model_path.setEditable(True)
        if self.detected_models:
            self.model_path.setCurrentText(self.detected_models[0])
        self.model_path.setFixedWidth(500)
        model_layout.addWidget(self.model_path)
        browse_model = QPushButton("浏览")
        browse_model.setFixedWidth(100)
        browse_model.clicked.connect(self.browse_model)
        model_layout.addWidget(browse_model)
        model_layout.addStretch()
        config_layout.addLayout(model_layout)
        
        # CPU线程和GPU设置
        thread_gpu_layout = QHBoxLayout()
        thread_label = QLabel("CPU线程:")
        thread_label.setFixedWidth(100)
        thread_gpu_layout.addWidget(thread_label)
        self.threads = QSpinBox()
        self.threads.setRange(1, 16)
        self.threads.setValue(4)
        self.threads.setFixedWidth(100)
        thread_gpu_layout.addWidget(self.threads)
        
        thread_gpu_layout.addSpacing(30)
        gpu_label = QLabel("GPU后端:")
        gpu_label.setFixedWidth(80)
        thread_gpu_layout.addWidget(gpu_label)
        self.gpu_backend = QComboBox()
        self.gpu_backend.addItems(["Vulkan", "CUDA", "OpenCL", "Metal", "CPU"])
        self.gpu_backend.setCurrentText("Vulkan")
        self.gpu_backend.setFixedWidth(150)
        thread_gpu_layout.addWidget(self.gpu_backend)
        thread_gpu_layout.addStretch()
        config_layout.addLayout(thread_gpu_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # 音频处理组
        audio_group = QGroupBox("音频处理")
        audio_layout = QVBoxLayout()
        
        self.audio_preprocess_checkbox = QCheckBox("✓ 启用音频预处理（人声分离+智能切片）")
        self.audio_preprocess_checkbox.setChecked(True)
        self.audio_preprocess_checkbox.setToolTip("启用后会进行人声分离和静音检测切片，避免长音频产生幻觉")
        audio_layout.addWidget(self.audio_preprocess_checkbox)
        
        # 并行处理配置
        parallel_layout = QHBoxLayout()
        parallel_label = QLabel("并行处理数量:")
        parallel_label.setFixedWidth(120)
        parallel_label.setToolTip("同时处理的音频切片数量，建议根据显卡显存调整\n4GB显存: 1-2\n6GB显存: 2-3\n8GB+显存: 3-4")
        parallel_layout.addWidget(parallel_label)
        
        self.parallel_count = QSpinBox()
        self.parallel_count.setRange(1, 8)
        self.parallel_count.setValue(2)
        self.parallel_count.setFixedWidth(100)
        self.parallel_count.setSuffix(" 个")
        self.parallel_count.setToolTip("根据显卡性能调整：\n• 低端显卡(4GB): 1-2个\n• 中端显卡(6-8GB): 2-3个\n• 高端显卡(8GB+): 3-4个")
        parallel_layout.addWidget(self.parallel_count)
        
        parallel_layout.addStretch()
        audio_layout.addLayout(parallel_layout)
        
        # 帮助文本
        help_text = QLabel("💡 提示：增加并行数量可以加快处理速度，但需要更多显存")
        help_text.setStyleSheet("color: #666; font-size: 11px; padding-left: 20px;")
        audio_layout.addWidget(help_text)
        
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        
        # 其他设置
        other_group = QGroupBox("其他设置")
        other_layout = QVBoxLayout()
        
        # 界面语言选择
        lang_layout = QHBoxLayout()
        lang_label = QLabel("界面语言:")
        lang_label.setFixedWidth(100)
        lang_layout.addWidget(lang_label)
        
        self.ui_language = QComboBox()
        self.ui_language.addItems(["中文", "English", "日本語"])
        self.ui_language.setFixedWidth(150)
        self.ui_language.currentIndexChanged.connect(self.change_ui_language)
        lang_layout.addWidget(self.ui_language)
        
        lang_help = QLabel("(更改后需重启程序)")
        lang_help.setStyleSheet("color: #999; font-size: 10px;")
        lang_layout.addWidget(lang_help)
        lang_layout.addStretch()
        other_layout.addLayout(lang_layout)
        
        other_layout.addSpacing(20)
        
        reset_btn = QPushButton("重置所有设置")
        reset_btn.clicked.connect(self.reset_all_settings)
        other_layout.addWidget(reset_btn)
        
        other_group.setLayout(other_layout)
        layout.addWidget(other_group)
        
        layout.addStretch()
    
    def reset_all_settings(self):
        """重置所有设置"""
        reply = QMessageBox.question(
            self, '确认重置', 
            '确定要重置所有设置吗？这将清除所有保存的配置。',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 删除配置文件
            if self.config_manager.config_file.exists():
                self.config_manager.config_file.unlink()
            
            # 重新加载默认配置
            self.config_manager = ConfigManager()
            self.load_settings()
            
            QMessageBox.information(self, '成功', '所有设置已重置为默认值')
    
    def load_settings(self):
        """加载上次的设置"""
        # 字幕样式
        subtitle_config = self.config_manager.get_category('subtitle')
        self.font_size.setValue(subtitle_config.get('font_size', 10))
        
        # 设置字体
        font_name = subtitle_config.get('font_name', 'Arial')
        index = self.font_name.findText(font_name)
        if index >= 0:
            self.font_name.setCurrentIndex(index)
        
        # 加载颜色
        self.primary_color = subtitle_config.get('primary_color', '#FFFFFF')
        self.outline_color = subtitle_config.get('outline_color', '#000000')
        self.update_color_buttons()
        
        # 加载其他字幕设置
        self.margin_v.setValue(subtitle_config.get('margin_v', 25))
        self.outline_width.setValue(subtitle_config.get('outline_width', 2))
        self.bold_checkbox.setChecked(subtitle_config.get('bold', False))
        self.italic_checkbox.setChecked(subtitle_config.get('italic', False))
        self.shadow_checkbox.setChecked(subtitle_config.get('shadow', False))
        
        # 加载描边启用状态
        outline_enabled = subtitle_config.get('outline_enabled', True)
        self.outline_enabled_checkbox.setChecked(outline_enabled)
        self.toggle_outline_controls()  # 更新控件状态
        
        # 翻译设置
        trans_config = self.config_manager.get_category('translation')
        self.translate_checkbox.setChecked(trans_config.get('enabled', False))
        
        target_lang = trans_config.get('target_language', '中文')
        index = self.target_language.findText(target_lang)
        if index >= 0:
            self.target_language.setCurrentIndex(index)
        
        display_mode = trans_config.get('display_mode', '双行显示（原文+翻译）')
        index = self.translation_mode.findText(display_mode)
        if index >= 0:
            self.translation_mode.setCurrentIndex(index)
        
        # Whisper 设置
        whisper_config = self.config_manager.get_category('whisper')
        
        language = whisper_config.get('language', '请选择语言 ⚠')
        index = self.language.findText(language)
        if index >= 0:
            self.language.setCurrentIndex(index)
        
        gpu_backend = whisper_config.get('gpu_backend', 'Vulkan')
        index = self.gpu_backend.findText(gpu_backend)
        if index >= 0:
            self.gpu_backend.setCurrentIndex(index)
        
        self.threads.setValue(whisper_config.get('threads', 4))
        self.embed_checkbox.setChecked(whisper_config.get('embed_subtitles', True))
        self.audio_preprocess_checkbox.setChecked(whisper_config.get('audio_preprocessing', True))
        self.parallel_count.setValue(whisper_config.get('parallel_count', 2))
        
        # 应用设置
        app_config = self.config_manager.get_category('app')
        language_code = app_config.get('language', 'zh_CN')
        
        # 映射语言代码到界面显示
        lang_map = {'zh_CN': '中文', 'en_US': 'English', 'ja_JP': '日本語'}
        lang_display = lang_map.get(language_code, '中文')
        index = self.ui_language.findText(lang_display)
        if index >= 0:
            self.ui_language.setCurrentIndex(index)
    
    def save_current_settings(self):
        """保存当前设置"""
        # 字幕样式
        self.config_manager.set('subtitle', 'font_size', self.font_size.value())
        self.config_manager.set('subtitle', 'font_name', self.font_name.currentText())
        self.config_manager.set('subtitle', 'primary_color', self.primary_color)
        self.config_manager.set('subtitle', 'outline_color', self.outline_color)
        self.config_manager.set('subtitle', 'outline_enabled', self.outline_enabled_checkbox.isChecked())
        self.config_manager.set('subtitle', 'margin_v', self.margin_v.value())
        self.config_manager.set('subtitle', 'outline_width', self.outline_width.value())
        self.config_manager.set('subtitle', 'bold', self.bold_checkbox.isChecked())
        self.config_manager.set('subtitle', 'italic', self.italic_checkbox.isChecked())
        self.config_manager.set('subtitle', 'shadow', self.shadow_checkbox.isChecked())
        
        # 翻译设置
        self.config_manager.set('translation', 'enabled', self.translate_checkbox.isChecked())
        self.config_manager.set('translation', 'target_language', self.target_language.currentText())
        self.config_manager.set('translation', 'display_mode', self.translation_mode.currentText())
        self.config_manager.set('translation', 'translation_on_top', self.translation_position.currentIndex() == 0)
        
        # Whisper 设置
        self.config_manager.set('whisper', 'language', self.language.currentText())
        self.config_manager.set('whisper', 'gpu_backend', self.gpu_backend.currentText())
        self.config_manager.set('whisper', 'threads', self.threads.value())
        self.config_manager.set('whisper', 'embed_subtitles', self.embed_checkbox.isChecked())
        self.config_manager.set('whisper', 'audio_preprocessing', self.audio_preprocess_checkbox.isChecked())
        self.config_manager.set('whisper', 'parallel_count', self.parallel_count.value())
        
        # 保存到文件
        self.config_manager.save_config()
    
    def choose_primary_color(self):
        """选择主颜色"""
        color = QColorDialog.getColor(QColor(self.primary_color), self, "选择字幕颜色")
        if color.isValid():
            self.primary_color = color.name()
            self.update_color_buttons()
            self.save_current_settings()
    
    def choose_outline_color(self):
        """选择描边颜色"""
        color = QColorDialog.getColor(QColor(self.outline_color), self, "选择描边颜色")
        if color.isValid():
            self.outline_color = color.name()
            self.update_color_buttons()
            self.save_current_settings()
    
    def toggle_outline_controls(self):
        """切换描边控件的启用状态"""
        enabled = self.outline_enabled_checkbox.isChecked()
        self.outline_color_label.setEnabled(enabled)
        self.outline_color_btn.setEnabled(enabled)
        self.outline_width_label.setEnabled(enabled)
        self.outline_width.setEnabled(enabled)
        self.save_current_settings()
    
    def update_color_buttons(self):
        """更新颜色按钮显示"""
        self.primary_color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.primary_color};
                border: 2px solid #CCCCCC;
                border-radius: 4px;
            }}
        """)
        
        self.outline_color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.outline_color};
                border: 2px solid #CCCCCC;
                border-radius: 4px;
            }}
        """)
    
    def import_custom_font(self):
        """导入自定义字体"""
        font_file, _ = QFileDialog.getOpenFileName(
            self, 
            "选择字体文件", 
            "", 
            "字体文件 (*.ttf *.otf);;所有文件 (*)"
        )
        
        if font_file:
            import shutil
            
            # 创建 fonts 目录
            fonts_dir = Path("fonts")
            fonts_dir.mkdir(exist_ok=True)
            
            # 获取字体文件名
            font_filename = Path(font_file).name
            font_name = Path(font_file).stem
            
            # 目标路径
            target_font_path = fonts_dir / font_filename
            
            try:
                # 复制字体文件到 fonts 目录
                if not target_font_path.exists():
                    shutil.copy2(font_file, target_font_path)
                    print(f"字体已复制到: {target_font_path}")
                else:
                    print(f"字体文件已存在: {target_font_path}")
                
                # 保存字体路径（相对路径）
                self.config_manager.set('subtitle', 'font_path', str(target_font_path))
                self.config_manager.save_config()
                
                # 添加到下拉菜单
                custom_name = f"自定义: {font_name}"
                
                # 检查是否已存在
                if self.font_name.findText(custom_name) < 0:
                    self.font_name.addItem(custom_name)
                
                self.font_name.setCurrentText(custom_name)
                QMessageBox.information(
                    self, 
                    '成功', 
                    f'字体已导入并保存到 fonts 目录:\n{font_name}\n\n下次启动程序可以直接使用此字体。'
                )
                
            except Exception as e:
                QMessageBox.critical(self, '错误', f'字体导入失败:\n{str(e)}')
    
    def load_custom_fonts(self):
        """加载 fonts 目录中的自定义字体"""
        fonts_dir = Path("fonts")
        
        if not fonts_dir.exists():
            return
        
        # 查找所有字体文件
        font_files = list(fonts_dir.glob("*.ttf")) + list(fonts_dir.glob("*.otf"))
        
        if font_files:
            print(f"找到 {len(font_files)} 个自定义字体")
            for font_file in sorted(font_files):
                font_name = font_file.stem
                custom_name = f"自定义: {font_name}"
                
                # 检查是否已存在
                if self.font_name.findText(custom_name) < 0:
                    self.font_name.addItem(custom_name)
                    print(f"  加载字体: {font_name}")


def translate_srt(srt_path, api_url, api_key, model, target_language, translation_on_top=True, translation_mode="dual"):
    """
    翻译 SRT 字幕文件
    
    Args:
        srt_path: SRT 文件路径
        api_url: API 地址
        api_key: API Key
        model: 模型名称
        target_language: 目标语言
        translation_on_top: True=翻译在上，False=原文在上
        translation_mode: 显示模式 ("dual"=双行, "translation_only"=仅翻译, "original_only"=仅原文)
    """
    import re
    
    # 读取 SRT 文件
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析 SRT
    pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n((?:.*\n?)+?)(?=\n\d+\n|\Z)'
    matches = re.findall(pattern, content, re.MULTILINE)
    
    if not matches:
        raise ValueError("无法解析 SRT 文件")
    
    # 如果是只显示原文，直接返回
    if translation_mode == "original_only":
        return
    
    # 提取所有文本
    texts = [match[3].strip() for match in matches]
    
    # 批量翻译
    translated_texts = batch_translate(texts, api_url, api_key, model, target_language)
    
    # 重建 SRT
    new_srt_lines = []
    for i, match in enumerate(matches):
        index, start, end, original = match
        translated = translated_texts[i]
        
        # 根据显示模式组合文本
        if translation_mode == "translation_only":
            # 只显示翻译
            combined_text = translated
        elif translation_mode == "dual":
            # 双行显示
            if translation_on_top:
                combined_text = f"{translated}\n{original.strip()}"
            else:
                combined_text = f"{original.strip()}\n{translated}"
        else:
            # 默认双行
            combined_text = f"{original.strip()}\n{translated}"
        
        new_srt_lines.append(f"{index}")
        new_srt_lines.append(f"{start} --> {end}")
        new_srt_lines.append(combined_text)
        new_srt_lines.append("")
    
    # 写回文件
    with open(srt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_srt_lines))


def batch_translate(texts, api_url, api_key, model, target_language, batch_size=10):
    """
    批量翻译文本
    
    Args:
        texts: 文本列表
        api_url: API 地址
        api_key: API Key
        model: 模型名称
        target_language: 目标语言
        batch_size: 每批处理数量
    
    Returns:
        翻译后的文本列表
    """
    translated = []
    
    # 确定 API 类型（OpenAI 或 Anthropic）
    is_anthropic = 'anthropic' in api_url.lower() or model.startswith('claude')
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        
        # 构建提示（使用英语）
        prompt = f"Translate the following subtitle texts into {target_language}. Keep the original format and line breaks. Return only the translations without any explanations.\n\n"
        for j, text in enumerate(batch):
            prompt += f"[{j+1}] {text}\n"
        
        try:
            if is_anthropic:
                # Anthropic API 格式
                response = requests.post(
                    f"{api_url.rstrip('/')}/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": model,
                        "max_tokens": 4096,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ]
                    },
                    timeout=60
                )
            else:
                # OpenAI API 格式
                response = requests.post(
                    f"{api_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3
                    },
                    timeout=60
                )
            
            response.raise_for_status()
            result = response.json()
            
            # 解析响应
            if is_anthropic:
                translated_text = result['content'][0]['text']
            else:
                translated_text = result['choices'][0]['message']['content']
            
            # 解析翻译结果
            lines = translated_text.strip().split('\n')
            
            # 更健壮的解析方式
            import re
            batch_results = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 跳过明显的解释性文本
                if any(skip_word in line.lower() for skip_word in [
                    'here are', 'translation', 'as follows', '以下是', '翻译结果'
                ]):
                    continue
                
                # 尝试去掉编号前缀 [1], [2] 等
                cleaned = re.sub(r'^\[\d+\]\s*', '', line)
                if cleaned:
                    batch_results.append(cleaned)
            
            # 确保返回的数量与批次相同
            if len(batch_results) == len(batch):
                translated.extend(batch_results)
            elif len(batch_results) > 0:
                # 如果数量不匹配，尝试匹配
                print(f"⚠️ 翻译返回 {len(batch_results)} 条，期望 {len(batch)} 条")
                # 取前N条或补齐
                for j in range(len(batch)):
                    if j < len(batch_results):
                        translated.append(batch_results[j])
                    else:
                        translated.append(batch[j])  # 使用原文
            else:
                # 完全解析失败，使用原文
                print(f"⚠️ 翻译解析失败，使用原文")
                translated.extend(batch)
        
        except Exception as e:
            # 出错时使用原文
            print(f"翻译批次失败: {e}")
            translated.extend(batch)
    
    return translated


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = ModernWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
