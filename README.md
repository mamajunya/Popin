# Popin - Subtitle Generator

> Fast, Accurate, and Intelligent Video Subtitle Generation Tool

Professional subtitle generation software based on Whisper.cpp and AI, supporting GPU acceleration, audio preprocessing, hallucination filtering, and AI translation.

---

## Key Features

### Cross-Platform High Performance
- **Whisper.cpp**: No need for CUDA; AMD and Intel GPUs can also accelerate, and older GPUs support OpenGL
- **Batch Processing**: Import multiple videos simultaneously for automatic sequential processing
- **Parallel Processing**: Configure the number of audio segments to process simultaneously (1-8), fully utilizing GPU performance
- **Smart Segmentation**: Vocal separation + silence detection for optimized processing efficiency

### High Accuracy
- **Large-v3 Model**: The latest and most accurate Whisper model
- **Audio Preprocessing**: Demucs vocal separation to reduce background interference
- **Hallucination Filtering**: Automatically filters AI-generated meaningless text
- **Silence Skipping**: Intelligently detects and skips silent segments

### Highly Customizable
- **Subtitle Styles**: Fully adjustable font, size, color, and outline
- **Custom Fonts**: Support for importing .ttf/.otf font files
- **Color Picker**: Any RGB color
- **Configuration Memory**: Automatically saves preferences

### Integrated AI Translation
- **Multi-language**: Supports OpenAI/Anthropic API
- **Display Modes**: Dual-line/translation-only/original-only
- **Batch Optimization**: Smart batching reduces API calls

---

## Quick Start

### System Requirements
- Windows 10/11
- Python 3.8+
- 4GB+ RAM
- (Recommended) GPU with Vulkan/CUDA support

### Installation Steps

#### 1. Clone or Download the Project
```bash
git clone <repository-url>
cd Popin
```

#### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Configure Whisper.cpp
(If you insist on downloading whisper.cpp yourself) (Release package already integrated)
1. Download Whisper.cpp precompiled version
2. Download GGML model file (e.g., ggml-large-v3.bin)
3. The program will auto-detect (or manually set in "Advanced Settings")

#### 4. Launch the Program
```bash
# Windows Users (Recommended)
Double-click run_gui_qt.bat

# Or via command line
python video_subtitle_gui_qt.py
```

### First-Time Use

1. **Select Video File**
2. **Select Language** (Required!)
3. **Adjust Subtitle Style** (Optional)
4. **Click "Start Generating Subtitles"**

✅ Done! Subtitles will be automatically generated and embedded into the video.

---

## User Guide

### Main Interface (Subtitle Generation)

#### Video Configuration
- **Video File**: Select the video to process
- **Output Directory**: Output location for subtitles and videos (optional, defaults to video directory)
- **Language**: ⚠️ **Required**, select the video's language (e.g., Chinese, Japanese, English)
- **Embed Subtitles**: Check to generate a new video with embedded subtitles

#### Subtitle Style
- **Font Size**: Default 10, range 8-72
- **Font Selection**: Arial, Microsoft YaHei, SimHei, SimSun
- **Import Font**: Import custom .ttf/.otf fonts
- **Subtitle Color**: Click button to select text color
- **Outline Color**: Click button to select outline color
- **Outline Width**: 1-5 pixels
- **Bottom Margin**: Distance of subtitles from bottom of screen
- **Bold/Italic/Shadow**: Text style options

#### Subtitle Translation (Optional)
- **Enable Translation**: Check to enable AI translation
- **Target Language**: Select translation target language
- **Display Mode**: 
  - Dual-line (original + translation)
  - Translation only
  - Original only
- **Display Order**: Translation on top / Original on top

### AI Settings

Configure OpenAI or Anthropic-compatible API for subtitle translation:

#### API Format Selection
- **OpenAI**: OpenAI official API format
  - API URL: `https://api.openai.com/v1`
  - Common models: gpt-4o-mini, gpt-4o
- **Anthropic**: Anthropic official API format
  - API URL: `https://api.anthropic.com/v1`
  - Common models: claude-3-5-sonnet, claude-3-5-haiku
- **Custom**: Third-party APIs compatible with OpenAI or Anthropic format
  - E.g., DeepSeek, locally deployed models
  - Enter API URL and model name manually

#### Configuration Steps
1. Select API format (program auto-fills corresponding API URL)
2. Enter API Key
3. Enter or modify model name
   - 💡 Tip: You can enter any model name, e.g., `deepseek-v4-flash`
4. Click "Test Connection" to verify configuration
5. Save configuration

### Advanced Settings

#### Whisper.cpp Configuration
- **Main Program**: whisper-cli.exe path (usually auto-detected)
- **Model File**: GGML model path (e.g., ggml-large-v3.bin)
- **CPU Threads**: 4-8 recommended
- **GPU Backend**: Vulkan (AMD/Universal), CUDA (NVIDIA), OpenCL, Metal (macOS)

#### Audio Processing
- **Audio Preprocessing**: Enable vocal separation and smart segmentation
  - Improves recognition accuracy
  - Avoids long audio hallucinations
  - Auto-skips silent segments
- **Parallel Processing Count**: Number of audio segments to process simultaneously (1-8)
  - Increasing parallelism speeds up processing but requires more VRAM
    - Low-end GPU (4GB): 1-2
    - Mid-range GPU (6-8GB): 2-3
    - High-end GPU (8GB+): 3-4
  - Settings are automatically saved

#### Other Settings
- **Reset All Settings**: Restore default configuration

---

## 📊 Performance Metrics

### Real Test Data
```
Test Video: Japanese Song MV
Video Duration: 286.7 seconds (4m47s)
Processing Time: 144.3 seconds (2m24s)
Speed Ratio: 1.99x (approximately 2x real-time speed)
GPU: AMD Radeon RX 6800 XT
Backend: Whisper.cpp + Vulkan
Model: ggml-large-v3.bin
```

### Processing Flow
```
1. Audio Extraction:     5s
2. Vocal Separation:    25s
3. Silence Detection:    2s
4. Segment Recognition: 90s (11 segments)
5. Hallucination Filter: 1s (filtered 1)
6. Subtitle Merge:       2s
7. Subtitle Embed:      15s
---
Total:                 144s
```

### Accuracy
- ✅ Complete Japanese lyrics recognition
- ✅ Precise timeline synchronization
- ✅ No hallucination text (successfully filtered)
- ✅ Accurate silence skipping (8.4%)
- ✅ Complete vocal retention (91.6%)

---

## 🔧 Core Features Explained

### 1. Subtitle Recognition
- **Engine**: Whisper.cpp (large-v3 model)
- **Acceleration**: GPU support (Vulkan/CUDA/OpenCL)
- **Speed**: Approximately 2x real-time speed
- **Languages**: Supports 100+ languages
- **Accuracy**: Very high (large-v3 model)

### 2. Audio Preprocessing
- **Vocal Separation**: Demucs htdemucs model
- **Silence Detection**: Precisely identifies vocal segments
- **Smart Segmentation**: Automatically splits long audio
- **Skip Silence**: Avoids meaningless processing
- **Effect**: Dramatically reduces AI hallucinations

### 3. Hallucination Filtering
- **Auto-Filter**: Common hallucination text
- **Rule Engine**: Regular expression support
- **Configurable**: `hallucination_filters.json`
- **Tested**: 26/26 passed
- **Effect**: Significantly improves subtitle quality

**Default Filter Rules**:
- Japanese: "ご視聴ありがとうございました", "チャンネル登録"
- English: "Thank you for watching", "Subscribe"
- Background Music: "BGM", "音楽"
- Production Info: "字幕by", "翻訳:"

### 4. AI Translation
- **API Support**: OpenAI, Anthropic
- **Models**: All supported
- **Batch Processing**: Improved efficiency
- **Display Modes**: Dual-line/translation-only/original-only
- **Robust**: Comprehensive error handling

### 5. Subtitle Styling
- **Subtitle Color**: Any RGB color
- **Outline Color**: Any RGB color
- **Outline Width**: Adjustable 1-5 pixels
- **Fonts**: System fonts + custom imports
- **Styles**: Bold, italic, shadow
- **Position**: Adjustable bottom margin

### 6. Configuration System
- **Auto-Save**: Saves on program close
- **Auto-Load**: Loads on program start
- **Path Not Saved**: File paths not remembered
- **Complete**: All settings can be saved
- **Reset**: One-click restore defaults

---

## 🔧 Configuration Files

### popin_config.json
User preference settings (auto-generated)
```json
{
  "subtitle": {
    "font_size": 10,
    "font_name": "Arial",
    "primary_color": "#FFFFFF",
    "outline_color": "#000000",
    "outline_width": 2,
    "outline_enabled": true,
    "margin_v": 25,
    "bold": false,
    "italic": false,
    "shadow": false
  },
  "translation": {
    "enabled": false,
    "target_language": "English",
    "display_mode": "Dual-line (original + translation)",
    "translation_on_top": true
  },
  "whisper": {
    "language": "Japanese (ja)",
    "gpu_backend": "Vulkan",
    "threads": 4,
    "embed_subtitles": true,
    "audio_preprocessing": true,
    "parallel_count": 2
  }
}
```

### hallucination_filters.json
Hallucination filter rules (customizable)
```json
{
  "enabled": true,
  "filters": {
    "japanese_common": {
      "enabled": true,
      "description": "Common Japanese hallucinations",
      "patterns": [
        "ご視聴ありがとうございました",
        "チャンネル登録",
        "高評価"
      ]
    },
    "english_common": {
      "enabled": true,
      "description": "Common English hallucinations",
      "patterns": [
        "thank you for watching",
        "subscribe"
      ]
    },
    "custom": {
      "enabled": true,
      "description": "Custom rules",
      "patterns": [
        "Text you want to filter"
      ]
    }
  }
}
```

### ai_config.json
AI translation configuration
```json
{
  "api_url": "https://XXXXX/v1",
  "api_key": "sk-...",
  "model": "XXXXX",
  "api_format": "openai"
}
```

---

## FAQ

### Q: Why is language selection mandatory?
**A**: The Whisper model needs to know the audio language for accurate recognition. Not selecting will cause recognition errors.

### Q: What if GPU acceleration doesn't work?
**A**: 
1. Check if drivers are up to date
2. Try different GPU backends (Vulkan/CUDA/OpenCL)
3. If none work, select CPU (will be slower)

### Q: How is translation billed?
**A**: Using OpenAI/Anthropic API requires your own API Key, billed by usage. Approximately:
- 5-minute video ≈ $0.05-0.10
- Translation is optional; no API needed if not translating

### Q: Subtitle colors not working?
**A**: Ensure:
1. "Embed subtitles in video" is checked
2. Color selection confirmed after choosing
3. View generated video (not SRT file)

### Q: How to speed up processing?
**A**: 
1. Enable GPU acceleration (Vulkan/CUDA)
2. Use smaller models (e.g., base instead of large)
3. Disable audio preprocessing (accuracy will decrease)
4. Upgrade hardware

### Q: Recognition inaccurate?
**A**: 
1. Confirm language selection is correct
2. Enable audio preprocessing
3. Use larger model (large-v3)
4. Check audio quality (background noise)

### Q: How to customize filter rules?
**A**: 
1. Edit `hallucination_filters.json`
2. Add your rules in `custom.patterns`
3. Supports regular expressions
4. Regenerate subtitles

---

## Technical Architecture

### Tech Stack
```
Frontend: PyQt6 (GUI)
Backend: Whisper.cpp (C++)
Audio: Demucs (PyTorch)
Translation: OpenAI/Anthropic API
Format: SRT/ASS
Video: FFmpeg
```

### Module Design
```
video_subtitle_gui_qt.py        Main GUI program
├── video_subtitle_generator_cpp.py   Whisper.cpp backend
│   └── whisper-cli.exe              C++ engine
├── audio_processor.py               Audio processing module
│   ├── Demucs                       Vocal separation
│   ├── FFmpeg                       Audio operations
│   └── hallucination_filters.json  Filter rules
├── config_manager.py                Configuration management
│   └── popin_config.json           User config
└── OpenAI/Anthropic API             Translation service
    └── ai_config.json               API config
```

### Data Flow
```
Video File
  ↓ FFmpeg Extract
Audio File
  ↓ Demucs Separate (optional)
Vocal Track
  ↓ Silence Detection
Audio Segments
  ↓ Whisper.cpp Recognition
Subtitle Segments
  ↓ Hallucination Filter
Clean Subtitles
  ↓ Timeline Adjustment
Complete SRT
  ↓ AI Translation (optional)
Translated SRT
  ↓ FFmpeg Embed
Video with Subtitles
```

---

## Project Structure

```
Popin/
├── Core Programs (5)
│   ├── video_subtitle_gui_qt.py          # Main program
│   ├── video_subtitle_generator_cpp.py   # Whisper.cpp backend
│   ├── video_subtitle_generator.py       # Python backend (backup)
│   ├── audio_processor.py                # Audio processing
│   └── config_manager.py                 # Config management
│
├── Configuration Files (4)
│   ├── popin_config.json                 # User config
│   ├── ai_config.json                    # AI config
│   ├── hallucination_filters.json        # Filter rules
│   └── requirements.txt                  # Dependencies
│
├── Launch Scripts (1)
│   └── run_gui_qt.bat                    # Windows launcher
│
├── Documentation (2)
│   ├── README.md                         # English docs (this file)
│   └── README_zh.md                      # Chinese docs
│
└── Data Directories (6)
    ├── whisper.cpp/                      # Whisper.cpp installation
    ├── fonts/                            # Custom fonts
    ├── vedio/                            # Input videos
    ├── vedio_t/                          # Output results
    ├── test_output/                      # Test output
    └── __pycache__/                      # Python cache
```

---

## Getting Started

### Installation
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure Whisper.cpp (see README_WHISPER_CPP.md)

# 3. Launch program
python video_subtitle_gui_qt.py
```

### Quick Generate
```
1. Double-click run_gui_qt.bat
2. Select video
3. Select language
4. Start generating
```

It's that simple!

---

## Contributing

Contributions, bug reports, and suggestions are welcome!

---

## License

MIT License

---

## Credits

- **OpenAI** - Whisper model
- **ggml-org** - Whisper.cpp implementation
- **facebook** - Demucs vocal separation
- **Qt** - PyQt6 GUI framework
- **FFmpeg** - Audio/video processing
- **whisper.cpp source** - https://github.com/ggml-org/whisper.cpp

---

## Support

- Documentation: This document
- Issues: See FAQ section
- Report: Submit an Issue

---

Popin v2.0  
2026-6-28  
mamajunya
