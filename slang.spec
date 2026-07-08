# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\h2311\\Downloads\\SynthLang\\scripts\\slang_cli.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['synthlang', 'synthlang.lexer', 'synthlang.parser', 'synthlang.compiler', 'synthlang.vm', 'synthlang.ir', 'synthlang.gc', 'synthlang.scheduler', 'synthlang.ffi'],
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
    name='slang',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/installer-icon.ico',
)
