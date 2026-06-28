# Popin v2.0 Release Notes

## 🎉 新特性

### 多语言支持
- ✅ 中文 (简体)
- ✅ English
- ✅ 日本語
- 自动检测系统语言
- 支持运行时切换

### 核心功能
- **Whisper.cpp 集成**: GPU 加速字幕识别
- **批量处理**: 同时处理多个视频文件
- **并行处理**: 可配置并行音频切片数量（1-8）
- **音频预处理**: Demucs 人声分离 + 静音检测
- **幻觉过滤**: 自动过滤 AI 生成的无意义文本
- **AI 翻译**: 支持 OpenAI/Anthropic API
- **字幕样式**: 完全自定义字体、颜色、描边
- **自定义字体**: 支持导入 .ttf/.otf 字体文件

### GPU 支持
- ✅ NVIDIA GPU (CUDA)
- ✅ AMD GPU (Vulkan)
- ✅ Intel GPU (Vulkan/OpenCL)
- ✅ 旧显卡 (OpenCL)

## 📦 发布包内容

```
Popin/
├── Popin.exe              # 主程序
├── 启动Popin.bat          # 启动脚本 (中文)
├── Start_Popin.bat        # 启动脚本 (English)
├── whisper.cpp/           # Whisper.cpp 引擎
│   ├── whisper-cli.exe    # 主程序
│   ├── *.dll              # 依赖库
│   └── models/            # 模型目录 (需自行下载)
├── locales/               # 多语言文件
│   ├── zh_CN.json         # 中文
│   ├── en_US.json         # English
│   └── ja_JP.json         # 日本語
├── fonts/                 # 自定义字体目录
│   └── README.md
├── README.md              # 英文文档
└── README_zh.md           # 中文文档
```

## 🚀 使用方法

### 首次使用

1. **下载模型**
   - 访问: https://huggingface.co/ggerganov/whisper.cpp/tree/main
   - 下载 `ggml-large-v3.bin` (推荐) 或其他模型
   - 放置到 `whisper.cpp/models/` 目录

2. **启动程序**
   - 双击 `启动Popin.bat` 或 `Popin.exe`

3. **开始使用**
   - 选择视频文件
   - 选择语言（必须！）
   - 点击"开始生成字幕"

### 进阶功能

#### 批量处理
1. 按住 Ctrl 键选择多个视频文件
2. 程序会自动依次处理所有视频

#### 并行处理
1. 进入"高级配置"标签
2. 调整"并行处理数量"（根据显卡性能）
   - 4GB 显存: 1-2
   - 6-8GB 显存: 2-3
   - 8GB+ 显存: 3-4

#### AI 翻译
1. 进入"AI 设置"标签
2. 选择 API 格式 (OpenAI/Anthropic/自定义)
3. 输入 API Key 和模型名称
4. 在主界面勾选"启用字幕翻译"

#### 自定义字体
1. 点击"导入字体"按钮
2. 选择 .ttf 或 .otf 字体文件
3. 字体会自动保存到 fonts/ 目录
4. 下次启动自动加载

## 📊 性能指标

### 测试环境
- GPU: AMD Radeon RX 6800 XT
- Backend: Vulkan
- Model: ggml-large-v3.bin
- Video: 4分47秒 日语歌曲 MV

### 测试结果
- 处理时间: 2分24秒
- 速度比: 1.99x (约2倍实时速度)
- 准确度: 极高
- 幻觉过滤: 1条成功过滤

## 🔧 系统要求

### 最低要求
- Windows 10/11 (64-bit)
- 4GB RAM
- 2GB 可用磁盘空间

### 推荐配置
- Windows 10/11 (64-bit)
- 8GB+ RAM
- GPU with 4GB+ VRAM
- 10GB 可用磁盘空间

## 📝 更新日志

### v2.0 (2026-06-28)
- ✨ 添加多语言支持（中日英）
- ✨ 支持批量视频处理
- ✨ 支持并行音频切片处理
- ✨ 添加自定义字体导入功能
- ✨ 添加描边启用/禁用选项
- 🐛 修复自定义字体名称问题
- 🐛 修复字幕嵌入失败问题
- 🐛 优化错误处理和日志输出
- 📝 完善中英文档

## 🐛 已知问题

1. **Windows Defender 误报**
   - PyInstaller 打包的程序可能被误报为病毒
   - 解决方法: 添加到白名单

2. **GPU 加速不可用**
   - 确保显卡驱动最新
   - 尝试不同的 GPU 后端
   - 可退回 CPU 模式（较慢）

## 💡 常见问题

### Q: 模型文件放在哪里？
A: 放在 `whisper.cpp/models/` 目录下

### Q: 如何选择合适的模型？
A: 
- `ggml-large-v3.bin`: 最准确（推荐）
- `ggml-base.bin`: 最快但准确度较低
- `ggml-medium.bin`: 平衡选择

### Q: 如何加快处理速度？
A:
1. 启用 GPU 加速
2. 增加并行处理数量
3. 使用较小的模型
4. 禁用音频预处理（会降低准确度）

### Q: 翻译功能如何收费？
A: 使用第三方 API，需自己的 API Key，按调用量计费

## 📞 支持

- GitHub: https://github.com/mamajunya/Popin
- Issues: https://github.com/mamajunya/Popin/issues
- Documentation: README.md, README_zh.md

## 📄 许可证

MIT License

## 🙏 致谢

- OpenAI - Whisper 模型
- ggml-org - Whisper.cpp 实现
- Facebook - Demucs 人声分离
- Qt - PyQt6 GUI 框架
- FFmpeg - 音视频处理

---

Popin v2.0  
2026-06-28  
mamajunya
