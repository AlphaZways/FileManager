@echo off
chcp 65001
chcp 65001 >nul
title 文件管理系统 - 一键启动

:: ============================================
:: 文件管理系统 - 自动环境配置和启动脚本
:: ============================================

setlocal enabledelayedexpansion

:: 设置颜色
color 0A

echo.
echo ╔══════════════════════════════════════════════╗
echo ║       文件管理系统 - 环境检测和启动            ║
echo ╚══════════════════════════════════════════════╝
echo.

:: ============================================
:: 1. 检测 Python
:: ============================================
echo [1/5] 正在检测 Python 环境...
echo.

set PYTHON_FOUND=0
set PYTHON_VERSION=0
set PYTHON_PATH=

:: 尝试查找 Python 3.10+
for %%p in (python python3 py) do (
    where %%p >nul 2>nul
    if !errorlevel! equ 0 (
        for /f "tokens=2" %%v in ('%%p --version 2^>^&1') do (
            set PYTHON_VERSION=%%v
            set PYTHON_PATH=%%p
            
            :: 检查版本是否 >= 3.10
            for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
                set MAJOR=%%a
                set MINOR=%%b
                if !MAJOR! geq 3 (
                    if !MINOR! geq 10 (
                        set PYTHON_FOUND=1
                    )
                )
            )
        )
    )
    if !PYTHON_FOUND! equ 1 goto :python_found
)

:python_found
if %PYTHON_FOUND% equ 1 (
    echo ✓ 检测到 Python %PYTHON_VERSION%
    echo   路径: %PYTHON_PATH%
    goto :check_requirements
)

echo ✗ 未检测到 Python 3.10+
echo.
echo 正在准备安装 Python 3.10...
goto :install_python

:: ============================================
:: 2. 安装 Python
:: ============================================
:install_python
echo.
echo [2/5] 下载并安装 Python 3.10...
echo.

:: 检测系统架构
set ARCH=x64
if "%PROCESSOR_ARCHITECTURE%"=="x86" (
    if not defined PROCESSOR_ARCHITEW6432 (
        set ARCH=x86
    )
)

:: Python 3.10.11 下载地址
set PYTHON_URL=https://mirrors.huaweicloud.com/python/3.10.11/python-3.10.11-amd64.exe
if "%ARCH%"=="x86" (
    set PYTHON_URL=https://mirrors.huaweicloud.com/python/3.10.11/python-3.10.11.exe
)

set PYTHON_INSTALLER=%TEMP%\python-3.10.11-installer.exe

echo 正在下载 Python 3.10.11...
echo 下载地址: %PYTHON_URL%
echo.

:: 使用 PowerShell 下载（更好的进度条）
powershell -Command "& {
    $url = '%PYTHON_URL%'
    $output = '%PYTHON_INSTALLER%'
    Write-Host '下载中...' -ForegroundColor Green
    $ProgressPreference = 'Continue'
    Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
    Write-Host '下载完成!' -ForegroundColor Green
}"

if not exist "%PYTHON_INSTALLER%" (
    echo.
    echo ✗ 下载失败，请手动安装 Python 3.10+
    echo   下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo.
echo 正在安装 Python 3.10.11（请等待）...
echo 注意：安装过程中请勿关闭窗口
echo.

:: 静默安装 Python
start /wait "" "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

:: 删除安装包
del /q "%PYTHON_INSTALLER%" 2>nul

:: 刷新环境变量
call :refresh_environment

:: 重新检测 Python
set PYTHON_FOUND=0
for %%p in (python python3 py) do (
    where %%p >nul 2>nul
    if !errorlevel! equ 0 (
        set PYTHON_PATH=%%p
        set PYTHON_FOUND=1
    )
)

if %PYTHON_FOUND% equ 1 (
    echo.
    echo ✓ Python 安装成功！
    echo.
) else (
    echo.
    echo ✗ Python 安装可能失败，请尝试手动安装
    echo   下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: ============================================
:: 3. 检查依赖包
:: ============================================
:check_requirements
echo.
echo [3/5] 正在检查依赖包...
echo.

:: 检查 pip
%PYTHON_PATH% -m pip --version >nul 2>nul
if %errorlevel% neq 0 (
    echo 正在安装 pip...
    %PYTHON_PATH% -m ensurepip --upgrade
)

:: 升级 pip
echo 正在升级 pip...
%PYTHON_PATH% -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ --quiet

:: 检查必要依赖
echo.
echo 正在检查必要依赖包...

set MISSING_PACKAGES=

:: 检查 pygame
%PYTHON_PATH% -c "import pygame" >nul 2>nul
if %errorlevel% neq 0 (
    set MISSING_PACKAGES=!MISSING_PACKAGES! pygame
)

:: 检查 qrcode
%PYTHON_PATH% -c "import qrcode" >nul 2>nul
if %errorlevel% neq 0 (
    set MISSING_PACKAGES=!MISSING_PACKAGES! qrcode
)

:: 检查 pillow
%PYTHON_PATH% -c "import PIL" >nul 2>nul
if %errorlevel% neq 0 (
    set MISSING_PACKAGES=!MISSING_PACKAGES! pillow
)

:: 检查 cryptography
%PYTHON_PATH% -c "import cryptography" >nul 2>nul
if %errorlevel% neq 0 (
    set MISSING_PACKAGES=!MISSING_PACKAGES! cryptography
)

if defined MISSING_PACKAGES (
    echo ✗ 缺少依赖包:!MISSING_PACKAGES!
    goto :install_requirements
) else (
    echo ✓ 所有依赖包已安装
    goto :check_project_files
)

:: ============================================
:: 4. 安装依赖
:: ============================================
:install_requirements
echo.
echo [4/5] 正在安装依赖包...
echo.

:: 使用阿里云镜像加速
set PIP_MIRROR=https://mirrors.aliyun.com/pypi/simple/

echo 安装 pygame...
%PYTHON_PATH% -m pip install pygame -i %PIP_MIRROR% --quiet

echo 安装 qrcode...
%PYTHON_PATH% -m pip install qrcode[pil] -i %PIP_MIRROR% --quiet

echo 安装 pillow...
%PYTHON_PATH% -m pip install pillow -i %PIP_MIRROR% --quiet

echo 安装 cryptography...
%PYTHON_PATH% -m pip install cryptography -i %PIP_MIRROR% --quiet

echo 安装 pyzbar...
%PYTHON_PATH% -m pip install pyzbar -i %PIP_MIRROR% --quiet

echo 安装 opencv-python...
%PYTHON_PATH% -m pip install opencv-python -i %PIP_MIRROR% --quiet

echo.
echo ✓ 依赖包安装完成！

:: ============================================
:: 5. 检查项目文件
:: ============================================
:check_project_files
echo.
echo [5/5]
echo 正在检查项目文件...

:: 查找主程序文件
set MAIN_FILE=
if exist "main.py" (
    set MAIN_FILE=main.py
) else if exist "file_manager.py" (
    set MAIN_FILE=file_manager.py
) else (
    :: 查找所有 .py 文件
    for %%f in (*.py) do (
        findstr /m "if __name__" "%%f" >nul 2>nul
        if !errorlevel! equ 0 (
            set MAIN_FILE=%%f
            goto :found_main
        )
    )
)

:found_main
if defined MAIN_FILE (
    echo ✓ 找到主程序: %MAIN_FILE%
    goto :run_app
) else (
    echo ✗ 未找到 Python 主程序文件
    echo 请确保 main.py 或 file_manager.py 存在
    echo.
    pause
    exit /b 1
)

:: ============================================
:: 启动应用
:: ============================================
:run_app
echo.
echo ╔══════════════════════════════════════════════╗
echo ║           环境准备完成，正在启动...            ║
echo ╚══════════════════════════════════════════════╝
echo.
echo 提示：按 Ctrl+C 可以停止程序
echo.

:: 启动程序
%PYTHON_PATH% %MAIN_FILE%

:: 程序退出后的处理
if %errorlevel% neq 0 (
    echo.
    echo ╔══════════════════════════════════════════════╗
    echo ║           程序异常退出                         ║
    echo ╚══════════════════════════════════════════════╝
    echo.
    echo 错误代码: %errorlevel%
    echo.
    echo 常见问题解决：
    echo 1. 检查 Python 版本是否为 3.10+
    echo 2. 尝试重新安装依赖：
    echo    %PYTHON_PATH% -m pip install --upgrade pygame qrcode pillow cryptography pyzbar opencv-python
    echo 3. 以管理员身份运行此脚本
    echo.
    pause
) else (
    echo.
    echo 程序已正常退出
    timeout /t 2 >nul
)

exit /b 0

:: ============================================
:: 辅助函数：刷新环境变量
:: ============================================
:refresh_environment
:: 刷新注册表中的环境变量到当前进程
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do (
    set "SYSTEM_PATH=%%b"
)
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do (
    set "USER_PATH=%%b"
)

:: 合并路径
set "PATH=%SYSTEM_PATH%;%USER_PATH%;%PATH%"
goto :eof