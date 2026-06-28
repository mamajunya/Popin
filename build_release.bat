@echo off
chcp 65001 >nul
echo ========================================
echo Popin 发布包构建脚本
echo ========================================
echo.

REM 检查是否安装 PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [错误] 未安装 PyInstaller
    echo 正在安装 PyInstaller...
    pip install pyinstaller
)

echo [步骤 1/5] 清理旧的构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "release" rmdir /s /q "release"

echo [步骤 2/5] 使用 PyInstaller 打包程序...
pyinstaller popin.spec

if errorlevel 1 (
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo [步骤 3/5] 创建发布目录结构...
mkdir release
mkdir release\Popin
xcopy /E /I /Y dist\Popin release\Popin

echo [步骤 4/5] 复制 whisper.cpp 文件...
if exist "whisper.cpp" (
    xcopy /E /I /Y whisper.cpp release\Popin\whisper.cpp
    echo ✓ whisper.cpp 已复制
) else (
    echo [警告] whisper.cpp 目录不存在，跳过
)

echo [步骤 5/5] 创建必要的目录和文件...
mkdir release\Popin\fonts
copy fonts\README.md release\Popin\fonts\ >nul 2>&1
copy README.md release\Popin\ >nul 2>&1
copy README_zh.md release\Popin\ >nul 2>&1
copy requirements.txt release\Popin\ >nul 2>&1

REM 创建启动脚本
echo @echo off > release\Popin\启动Popin.bat
echo cd /d %%~dp0 >> release\Popin\启动Popin.bat
echo start Popin.exe >> release\Popin\启动Popin.bat

echo @echo off > release\Popin\Start_Popin.bat
echo cd /d %%~dp0 >> release\Popin\Start_Popin.bat
echo start Popin.exe >> release\Popin\Start_Popin.bat

echo.
echo ========================================
echo ✓ 构建完成！
echo ========================================
echo.
echo 发布包位置: release\Popin\
echo.
echo 包含内容:
echo   - Popin.exe (主程序)
echo   - whisper.cpp\ (Whisper.cpp 引擎)
echo   - locales\ (多语言文件)
echo   - fonts\ (自定义字体目录)
echo   - README.md (英文文档)
echo   - README_zh.md (中文文档)
echo   - 启动Popin.bat (启动脚本)
echo.
pause
