@echo off
echo Image Display Application Installation
echo ===================================
echo.

echo Checking for gxipy SDK...
if not exist libs\gxipy (
    echo WARNING: gxipy SDK not found in the libs directory.
    echo Please copy your gxipy SDK files to the libs folder before running the application.
    echo See libs\README.txt for more information.
    echo.
    pause
)

echo Creating Desktop shortcut...
set SCRIPT="%TEMP%\create_shortcut.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\Image Display.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%~dp0image_display.exe" >> %SCRIPT%
echo oLink.WorkingDirectory = "%~dp0" >> %SCRIPT%
echo oLink.Description = "Image Display Application" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%
cscript /nologo %SCRIPT%
del %SCRIPT%

echo.
echo Installation complete!
echo You can now run the application from the desktop shortcut or by using run_app.bat
echo.
pause 