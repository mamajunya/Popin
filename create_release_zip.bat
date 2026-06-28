@echo off
chcp 65001 >nul
echo ========================================
echo 创建 Popin 发布压缩包
echo ========================================
echo.

cd release

if not exist "Popin" (
    echo [错误] Popin 目录不存在！
    echo 请先运行 build_release.bat 构建发布包
    pause
    exit /b 1
)

echo [正在创建压缩包...]
echo 目标: Popin_v2.0_Windows_x64.zip

REM 使用 PowerShell 创建 ZIP
powershell -Command "Compress-Archive -Path 'Popin\*' -DestinationPath 'Popin_v2.0_Windows_x64.zip' -Force"

if errorlevel 1 (
    echo [错误] 压缩失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ 压缩包创建完成！
echo ========================================
echo.
echo 位置: release\Popin_v2.0_Windows_x64.zip
echo.

REM 显示文件大小
for %%A in ("Popin_v2.0_Windows_x64.zip") do (
    echo 文件大小: %%~zA 字节
    set /a size_mb=%%~zA/1024/1024
)
echo 约 %size_mb% MB
echo.

pause
