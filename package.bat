@echo off
echo Starting packaging process...

:: Check if captured_images directory exists, if not create it
if not exist captured_images mkdir captured_images

:: Make sure PyInstaller is installed
pip install pyinstaller

:: Run PyInstaller with the updated spec file
pyinstaller --clean 图片显示器_updated.spec

echo Packaging completed!
echo The packaged application is located in the dist/图片显示器 directory
pause