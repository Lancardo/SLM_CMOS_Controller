@echo off
echo Starting single-file packaging process...

:: Check if captured_images directory exists, if not create it
if not exist captured_images mkdir captured_images

:: Make sure PyInstaller is installed
pip install pyinstaller

:: Create a onefile version for easier distribution
pyinstaller --onefile --windowed --icon=app_icon.ico --add-data "gxipy;gxipy" --add-data "app_icon.ico;." --name "图片显示器_单文件版" image_display.py

echo Single-file packaging completed!
echo The packaged application is located in the dist directory as 图片显示器_单文件版.exe
pause