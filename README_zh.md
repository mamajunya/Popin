# Popin - 字幕生成器

> 快速、准确、智能的视频字幕自动生成工具

基于 Whisper.cpp 和 AI 的专业字幕生成软件，支持 GPU 加速、音频预处理、幻觉过滤和 AI 翻译。

---

## 特色内容

### 全平台高性能
- **Whisper.cpp**: 无需强制使用CUDA AMD，英特尔显卡也可以进行加速,老式显卡也支持使用OpenGL
- **批量处理**: 支持同时导入多个视频，自动依次处理
- **并行处理**: 可配置同时处理的音频切片数量（1-8个），充分利用显卡性能
- **智能切片**: 人声分离+静音检测，优化处理效率

### 高准确度
- **Large-v3 模型**: 最新最准确的 Whisper 模型
- **音频预处理**: Demucs 人声分离，减少背景干扰
- **幻觉过滤**: 自动过滤 AI 生成的无意义文本
- **静音跳过**: 智能检测并跳过静音段

### 高度自定义
- **字幕样式**: 字体、大小、颜色、描边完全可调
- **自定义字体**: 支持导入 .ttf/.otf 字体文件
- **颜色选择器**: 任意 RGB 颜色
- **配置记忆**: 自动保存偏好

###  集成 AI 翻译
- **多语言**: 支持 OpenAI/Anthropic API
- **显示模式**: 双行/仅翻译/仅原文
- **批量优化**: 智能分批减少 API 调用

---

## 快速开始

### 系统要求
- Windows 10/11
- Python 3.8+
- 4GB+ 内存
- （推荐）支持 Vulkan/CUDA 的 GPU

### 安装步骤

#### 1. 克隆或下载项目
```bash
git clone <repository-url>
cd Popin
```

#### 2. 安装 Python 依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置 Whisper.cpp
(如果你坚持自己下载whisper.cpp)(发布包已自动集成)
1. 下载 Whisper.cpp 预编译版本
2. 下载 GGML 模型文件（如 ggml-large-v3.bin）
3. 程序会自动检测（或在"高级配置"中手动设置）

#### 4. 启动程序
```bash
# Windows 用户（推荐）
双击 run_gui_qt.bat

# 或命令行
python video_subtitle_gui_qt.py
```

### 首次使用

1. **选择视频文件**
2. **选择语言**（必须！）
3. **调整字幕样式**（可选）
4. **点击"开始生成字幕"**

✅ 完成！字幕会自动生成并嵌入视频。

---

## 使用指南

### 主界面（字幕生成）

#### 视频配置
- **视频文件**: 选择要处理的视频
- **输出目录**: 字幕和视频的输出位置（可选，默认为视频所在目录）
- **语言**: ⚠️ **必选**，选择视频的语言（如：中文、日语、英语）
- **嵌入字幕**: 勾选后会生成带字幕的新视频

#### 字幕样式
- **字体大小**: 默认 10，范围 8-72
- **字体选择**: Arial、微软雅黑、黑体、宋体
- **导入字体**: 可导入自定义 .ttf/.otf 字体
- **字幕颜色**: 点击按钮选择文字颜色
- **描边颜色**: 点击按钮选择描边颜色
- **描边宽度**: 1-5 像素
- **底部边距**: 字幕距离屏幕底部的距离
- **粗体/斜体/阴影**: 文字样式选项

#### 字幕翻译（可选）
- **启用翻译**: 勾选启用 AI 翻译
- **目标语言**: 选择翻译目标语言
- **显示模式**: 
  - 双行显示（原文+翻译）
  - 只显示翻译
  - 只显示原文
- **显示顺序**: 翻译在上/原文在上

### AI 设置

配置 OpenAI 或 Anthropic 兼容的 API 用于字幕翻译：

#### API 格式选择
- **OpenAI**: OpenAI 官方 API 格式
  - API 地址: `https://api.openai.com/v1`
  - 常用模型: gpt-5-4-mini, gpt-5-4
- **Anthropic**: Anthropic 官方 API 格式
  - API 地址: `https://api.anthropic.com/v1`
  - 常用模型: claude-4-5-sonnet, claude-4-5haiku
- **自定义**: 兼容 OpenAI 或 Anthropic 格式的第三方 API
  - 例如: DeepSeek, 本地部署的模型等
  - 自行输入 API 地址和模型名称

#### 配置步骤
1. 选择 API 格式（程序会自动填充对应的 API 地址）
2. 输入 API Key
3. 输入或修改模型名称
   - 💡 提示: 可以输入任意模型名称，如 `deepseek-v4-flash`
4. 点击"测试连接"验证配置
5. 保存配置

### 高级配置

#### Whisper.cpp 配置
- **主程序**: whisper-cli.exe 路径（通常自动检测）
- **模型文件**: GGML 模型路径（如 ggml-large-v3.bin）
- **CPU 线程**: 4-8 推荐
- **GPU 后端**: Vulkan（AMD/通用）、CUDA（NVIDIA）、OpenCL、Metal（macOS）

#### 音频处理
- **音频预处理**: 启用人声分离和智能切片
  -  提高识别准确度
  -  避免长音频幻觉
  -  自动跳过静音段
- **并行处理数量**: 同时处理的音频切片数量（1-8）
  -  增加并行数可加快处理速度，但需要更多显存
  -  设置会自动保存

#### 其他设置
- **重置所有设置**: 恢复默认配置

---

## 📊 性能表现

### 实测数据
```
测试视频: 日语歌曲 MV
视频时长: 286.7 秒 (4分47秒)
处理时间: 144.3 秒 (2分24秒)
速度比:   1.99x (约2倍实时速度)
GPU:      AMD Radeon RX 6800 XT
后端:     Whisper.cpp + Vulkan
模型:     ggml-large-v3.bin
```

### 处理流程
```
1. 音频提取:      5秒
2. 人声分离:     25秒
3. 静音检测:      2秒
4. 切片识别:     90秒 (11个片段)
5. 幻觉过滤:      1秒 (过滤1条)
6. 字幕合并:      2秒
7. 字幕嵌入:     15秒
---
总计:           144秒
```

### 准确度
- ✅ 日语歌词完整识别
- ✅ 时间轴精确同步
- ✅ 无幻觉文本（成功过滤）
- ✅ 静音段准确跳过 (8.4%)
- ✅ 有声段完整保留 (91.6%)

---

## 🔧 核心功能详解

### 1. 字幕识别 
- **引擎**: Whisper.cpp (large-v3 模型)
- **加速**: GPU 支持（Vulkan/CUDA/OpenCL）
- **速度**: 约 2x 实时速度
- **语言**: 支持 100+ 语言
- **准确度**: 极高（large-v3 模型）

### 2. 音频预处理 
- **人声分离**: Demucs htdemucs 模型
- **静音检测**: 精确识别有声片段
- **智能切片**: 自动切分长音频
- **跳过静音**: 避免无意义的处理
- **效果**: 大幅减少 AI 幻觉

### 3. 幻觉过滤 
- **自动过滤**: 常见幻觉文本
- **规则引擎**: 正则表达式支持
- **可配置**: `hallucination_filters.json`
- **测试**: 26/26 通过
- **效果**: 显著提高字幕质量

**默认过滤规则**:
- 日语: "ご視聴ありがとうございました"、"チャンネル登録"
- 英语: "Thank you for watching"、"Subscribe"
- 背景音乐: "BGM"、"音楽"
- 制作信息: "字幕by"、"翻訳:"

### 4. AI 翻译 
- **API 支持**: OpenAI, Anthropic
- **模型**: 全部支持
- **批量处理**: 提高效率
- **显示模式**: 双行/仅翻译/仅原文
- **健壮**: 完善的错误处理

### 5. 字幕样式 
- **字幕颜色**: 任意 RGB 颜色
- **描边颜色**: 任意 RGB 颜色
- **描边宽度**: 1-5 像素可调
- **字体**: 系统字体 + 自定义导入
- **样式**: 粗体、斜体、阴影
- **位置**: 底部边距可调

### 6. 配置系统 
- **自动保存**: 程序关闭时保存
- **自动加载**: 程序启动时加载
- **不保存路径**: 文件路径不记忆
- **完整**: 所有设置都可保存
- **重置**: 一键恢复默认值

---

## 🔧 配置文件

### popin_config.json
用户偏好设置（自动生成）
```json
{
  "subtitle": {
    "font_size": 10,
    "font_name": "Arial",
    "primary_color": "#FFFFFF",
    "outline_color": "#000000",
    "outline_width": 2,
    "margin_v": 25,
    "bold": false,
    "italic": false,
    "shadow": false
  },
  "translation": {
    "enabled": false,
    "target_language": "中文",
    "display_mode": "双行显示（原文+翻译）",
    "translation_on_top": true
  },
  "whisper": {
    "language": "日语 (ja)",
    "gpu_backend": "Vulkan",
    "threads": 4,
    "embed_subtitles": true,
    "audio_preprocessing": true
  }
}
```

### hallucination_filters.json
幻觉过滤规则（可自定义）
```json
{
  "enabled": true,
  "filters": {
    "japanese_common": {
      "enabled": true,
      "description": "日语常见幻觉",
      "patterns": [
        "ご視聴ありがとうございました",
        "チャンネル登録",
        "高評価"
      ]
    },
    "english_common": {
      "enabled": true,
      "description": "英语常见幻觉",
      "patterns": [
        "thank you for watching",
        "subscribe"
      ]
    },
    "custom": {
      "enabled": true,
      "description": "自定义规则",
      "patterns": [
        "你想过滤的文本"
      ]
    }
  }
}
```

### ai_config.json
AI 翻译配置
```json
{
  "api_url": "https://XXXXX/v1",
  "api_key": "sk-...",
  "model": "XXXXX"
}
```

---

## 常见问题

### Q: 为什么必须选择语言？
**A**: Whisper 模型需要知道音频语言才能准确识别。不选择会导致识别错误。

### Q: GPU 加速不工作怎么办？
**A**: 
1. 检查驱动是否最新
2. 尝试不同的 GPU 后端（Vulkan/CUDA/OpenCL）
3. 如果都不行，选择 CPU（会慢一些）

### Q: 翻译功能如何收费？
**A**: 使用 OpenAI/Anthropic API 需要自己的 API Key，按调用量计费。大约：
- 5 分钟视频 ≈ $0.05-0.10
- 翻译是可选的，不翻译无需 API

### Q: 字幕颜色不生效？
**A**: 确保：
1. 勾选了"将字幕嵌入视频"
2. 颜色选择后点击了确认
3. 查看生成的视频（不是 SRT 文件）

### Q: 处理速度慢怎么办？
**A**: 
1. 启用 GPU 加速（Vulkan/CUDA）
2. 使用较小的模型（如 base 代替 large）
3. 禁用音频预处理（准确度会降低）
4. 升级硬件

### Q: 识别不准确？
**A**: 
1. 确认语言选择正确
2. 启用音频预处理
3. 使用更大的模型（large-v3）
4. 检查音频质量（背景噪音）

### Q: 如何自定义过滤规则？
**A**: 
1. 编辑 `hallucination_filters.json`
2. 在 `custom.patterns` 中添加你的规则
3. 支持正则表达式
4. 重新生成字幕

---

## 技术架构

### 技术栈
```
前端: PyQt6 (GUI)
后端: Whisper.cpp (C++)
音频: Demucs (PyTorch)
翻译: OpenAI/Anthropic API
格式: SRT/ASS
视频: FFmpeg
```

### 模块设计
```
video_subtitle_gui_qt.py        主 GUI 程序
├── video_subtitle_generator_cpp.py   Whisper.cpp 后端
│   └── whisper-cli.exe              C++ 引擎
├── audio_processor.py               音频处理模块
│   ├── Demucs                       人声分离
│   ├── FFmpeg                       音频操作
│   └── hallucination_filters.json  过滤规则
├── config_manager.py                配置管理
│   └── popin_config.json           用户配置
└── OpenAI/Anthropic API             翻译服务
    └── ai_config.json               API 配置
```

### 数据流
```
视频文件
  ↓ FFmpeg 提取
音频文件
  ↓ Demucs 分离（可选）
人声轨道
  ↓ 静音检测
音频片段
  ↓ Whisper.cpp 识别
字幕片段
  ↓ 幻觉过滤
干净字幕
  ↓ 时间轴调整
完整 SRT
  ↓ AI 翻译（可选）
翻译 SRT
  ↓ FFmpeg 嵌入
带字幕视频
```

---

## 项目结构

```
Popin/
├── 核心程序 (5个)
│   ├── video_subtitle_gui_qt.py          # 主程序
│   ├── video_subtitle_generator_cpp.py   # Whisper.cpp 后端
│   ├── video_subtitle_generator.py       # Python 后端（备用）
│   ├── audio_processor.py                # 音频处理
│   └── config_manager.py                 # 配置管理
│
├── 配置文件 (4个)
│   ├── popin_config.json                 # 用户配置
│   ├── ai_config.json                    # AI 配置
│   ├── hallucination_filters.json        # 过滤规则
│   └── requirements.txt                  # 依赖列表
│
├── 启动脚本 (1个)
│   └── run_gui_qt.bat                    # Windows 启动
│
├── 文档 (2个)
│   ├── README.md                         # 英文文档
│   └── README_zh.md                      # 中文文档（本文件）
│
└── 数据目录 (5个)
    ├── whisper.cpp/                      # Whisper.cpp 安装
    ├── vedio/                            # 输入视频
    ├── vedio_t/                          # 输出结果
    ├── test_output/                      # 测试输出
    └── __pycache__/                      # Python 缓存
```

---

## 开始使用

### 安装
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 Whisper.cpp（见 README_WHISPER_CPP.md）

# 3. 启动程序
python video_subtitle_gui_qt.py
```

### 快速生成
```
1. 双击 run_gui_qt.bat
2. 选择视频
3. 选择语言
4. 开始生成
```

就是这么简单！

---

## 贡献

欢迎贡献代码、报告问题或提出建议！

---

## 许可证

MIT License 

---

## 致谢

- **OpenAI** - Whisper 模型
- **ggml-org** - Whisper.cpp 实现
- **facebook** - Demucs 人声分离
- **Qt** - PyQt6 GUI 框架
- **FFmpeg** - 音视频处理
- **whisper.cpp来源** - https://github.com/ggml-org/whisper.cpp
---

## 支持

- 文档: 本文档
- 问题: 查看常见问题章节
- 报告: 提交 Issue

---

Popin v2.0  
2026-6-28 
mamajunya
