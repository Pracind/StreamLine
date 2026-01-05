# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files
import os

project_root = Path(os.getcwd()).resolve()

# -------------------------------
# Hidden imports (minimal + safe)
# -------------------------------
hiddenimports = [
    "whisper",
    "whisper.audio",
    "whisper.decoding",
    "whisper.model",
    "whisper.tokenizer",

    "torch",
    "torch.nn",
    "torch.nn.functional",
    "torch.backends",
]

hiddenimports += [
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
]

# -------------------------------
# Whisper Data files
# -------------------------------
whisper_datas = collect_data_files(
    "whisper",
    includes=["assets/*"]
)


# -------------------------------
# Data files
# -------------------------------
datas = [
    (str(project_root / "assets"), "assets"),
    (str(project_root / "data"), "data"),
] + whisper_datas

# -------------------------------
# FFmpeg binary
# -------------------------------
binaries = [
    (str(project_root / "ffmpeg" / "bin" / "ffmpeg.exe"), "ffmpeg"),
]

# -------------------------------
# Analysis
# -------------------------------
a = Analysis(
    [str(project_root / "src" / "ui" / "main.py")],
    pathex=[str(project_root / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=[
        "tensorboard",  # safe to exclude
    ],
    hookspath=[],
    runtime_hooks=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
)

# -------------------------------
# PYZ
# -------------------------------
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)

# -------------------------------
# EXE (no binaries here!)
# -------------------------------
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VOD-Engine",
    debug=False,
    strip=False,
    upx=False,
    console=False,   # GUI app
)

# -------------------------------
# COLLECT (this is ONEDIR)
# -------------------------------
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="VOD-Engine",
)
