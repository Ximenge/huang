@echo off

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到 Python 安装。请先安装 Python 3.6 或更高版本。
    pause
    exit /b 1
)

REM 检查 Pillow 库是否安装
python -c "import PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装 Pillow 库...
    pip install pillow
    if %errorlevel% neq 0 (
        echo 错误: 安装 Pillow 库失败。
        pause
        exit /b 1
    )
)

REM 执行转换脚本
echo 开始转换图片到 WebP 格式...
python convert_to_webp.py

REM 等待用户按任意键退出
echo.
echo 转换和复制完成！按任意键退出...
pause >nul
