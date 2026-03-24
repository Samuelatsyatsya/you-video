# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules

ffmpeg_path = os.path.join("tools", "ffmpeg", "bin", "ffmpeg.exe")
extra_binaries = []
if os.path.exists(ffmpeg_path):
    # Bundle ffmpeg so users don't need to install it separately.
    extra_binaries.append((ffmpeg_path, os.path.join("ffmpeg")))

hidden = collect_submodules("yt_dlp")

a = Analysis(
    ['YouVideo.py'],
    pathex=[],
    binaries=extra_binaries,
    datas=[('./PeerLearn.png', '.')],
    hiddenimports=hidden,
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
    name='YouVideo',
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
    icon=['PeerLearn.png'],
)
