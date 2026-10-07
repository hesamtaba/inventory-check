# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files,collect_submodules
hiddenimports=collect_submodules('PySide6')
datas=[('assets','assets')]+collect_data_files('PySide6')
a=Analysis(['app/main.py'],pathex=['.'],binaries=[],datas=datas,hiddenimports=hiddenimports,hookspath=[],runtime_hooks=[],excludes=[],noarchive=False)
pyz=PYZ(a.pure); exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name='InventoryChecker',debug=False,bootloader_ignore_signals=False,strip=False,upx=True,console=False,icon='assets/app.ico')
coll=COLLECT(exe,a.binaries,a.datas,strip=False,upx=True,name='InventoryChecker')
