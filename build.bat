@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul || (echo Python Launcher not found & exit /b 1)
py -3.12 -c "import sys; assert sys.version_info[:2]==(3,12)" || (echo Python 3.12 x64 is required & exit /b 1)
if not exist .venv py -3.12 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
set PYTHONPATH=%CD%
pytest -q
if errorlevel 1 exit /b 1
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
pyinstaller --clean --noconfirm InventoryChecker.spec
if not exist dist\InventoryChecker\InventoryChecker.exe exit /b 1
echo EXE created: dist\InventoryChecker\InventoryChecker.exe
where ISCC.exe >nul 2>nul && ISCC.exe installer\installer.iss || echo Inno Setup not found in PATH. Open installer\installer.iss in Inno Setup Compiler.
endlocal
