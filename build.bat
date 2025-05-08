@echo off
echo Building Image Display Application...

REM 激活虚拟环境（如果存在）
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM 确保所有依赖都已安装
pip install -r requirements.txt

REM 使用PyInstaller打包应用程序
pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --icon=app_icon.ico ^
    --add-data "app_icon.ico;." ^
    --name "图片显示器" ^
    image_display.py

REM 检查是否成功创建了exe文件
if exist "dist\图片显示器.exe" (
    echo.
    echo Build successful! Executable created at: dist\图片显示器.exe
    echo.
) else (
    echo.
    echo Build failed! Please check the error messages above.
    echo.
)

REM 如果是从虚拟环境启动的，则退出虚拟环境
if defined VIRTUAL_ENV (
    deactivate
)

pause 