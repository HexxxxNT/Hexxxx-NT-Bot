# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    [".\\src\\composition_root.py"],
    pathex=["."],
    binaries=[],
    datas=[(os.path.join(dp, f), dp) for dp, dn, filenames in os.walk("./res") for f in filenames],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Hexxxxs_NT_Bot",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[".\\res\\icon.ico"],
    version=".\\version.rc",
)
