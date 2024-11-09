
SET THIS_DIR=%~dp0
SET ROOT_DIR=%THIS_DIR%\..
SET VENV=%ROOT_DIR%\.venv
SET SRC=%ROOT_DIR%\src
SET DIST=%ROOT_DIR%\dist

SET ZIP_PATH=%DIST%\NT_Bot.zip

rem Build using pyinstaller & spec file:
%VENV%\Scripts\pyinstaller.exe %ROOT_DIR%/build.spec --noconfirm

rem Delete old and create new zip archive:
del %ZIP_PATH%
7z a -tzip %ZIP_PATH% %DIST%\Hexxxxs_NT_Bot.exe
