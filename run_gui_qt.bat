@echo off
chcp 65001 >nul
echo ========================================
echo 视频自动字幕生成器 (PyQt6)
echo ========================================
echo.

REM 检查 stable-ts 是否安装
python -c "import stable_whisper" 2>nul
if errorlevel 1 (
    echo ⚠️  检测到 stable-ts 未安装
    echo.
    echo 推荐安装 stable-ts 以获得更准确的时间戳
    echo.
    choice /C YN /M "是否现在安装 stable-ts？"
    if errorlevel 2 goto skip_install
    if errorlevel 1 (
        echo.
        echo 正在安装 stable-ts 和 faster-whisper...
        pip install -U stable-ts faster-whisper
        echo.
        echo ✓ 安装完成！
        echo.
    )
)

:skip_install
echo 正在启动 GUI...
echo.
python video_subtitle_gui_qt.py
pause

