REM Used to automatically copy the custom_resize_brush on Windows
REM extension to the roaming appdata pykrita folder
echo off

Rem set /p "install_type=Choose install method (s: symlink | c: copy):"
set install_type="c"

set "EXTENSION_NAME=custom_brush_resize"
set "KRITA_APPDATA_DIR=%APPDATA%\krita"
set "KRITA_PYKRITA_DIR=%KRITA_APPDATA_DIR%\pykrita"
set "CURRENT_DIR=%~dp0"
set "FINAL_EXTENSION_DIR=%KRITA_PYKRITA_DIR%\%EXTENSION_NAME%"
set "EXTENSION_DESKTOP_FILE=%CURRENT_DIR%\%EXTENSION_NAME%.desktop"
set "EXISTING_DESKTOP_FILE=%KRITA_PYKRITA_DIR%\%EXTENSION_NAME%.desktop"


if %install_type% == "s" (
    goto :make_symlink
)

if %install_type% == "c" (
    goto :copy_extension
)

echo Invalid install method
EXIT /b 1


:make_symlink
echo Creating symlink
echo Not implemented yet :)
goto :finished


:copy_extension
echo Copying extension
if EXIST %FINAL_EXTENSION_DIR% (
    echo Replacing outdated version
    del %FINAL_EXTENSION_DIR% /F /Q
)

mkdir %FINAL_EXTENSION_DIR%

if EXIST %EXISTING_DESKTOP_FILE% (
    del %EXISTING_DESKTOP_FILE% /F /Q
)

copy "%EXTENSION_DESKTOP_FILE%" "%EXISTING_DESKTOP_FILE%" /Y 


REM for %%a in (%CURRENT_DIR%*.py) do copy %%a %FINAL_EXTENSION_DIR%  /Y
xcopy %CURRENT_DIR% %FINAL_EXTENSION_DIR% /Y /Q /E 
goto :finished

:finished
echo Finished installing %EXTENSION_NAME%