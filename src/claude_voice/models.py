"""Where the Kokoro model lives, and how to fetch it."""

from __future__ import annotations

import os
import sys
import urllib.request
from pathlib import Path

RELEASE_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
MODEL_FILE = "kokoro-v1.0.onnx"
VOICES_FILE = "voices-v1.0.bin"


def data_dir() -> Path:
    base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    return base / "claude-voice"


def model_path() -> Path:
    return data_dir() / MODEL_FILE


def voices_path() -> Path:
    return data_dir() / VOICES_FILE


def is_installed() -> bool:
    return model_path().is_file() and voices_path().is_file()


def download() -> None:
    """Fetch the missing model files (about 350 MB), skipping those already present."""
    data_dir().mkdir(parents=True, exist_ok=True)
    for target in (model_path(), voices_path()):
        if target.is_file():
            continue
        print(f"Downloading {target.name}...", file=sys.stderr)
        partial = target.with_suffix(".part")
        urllib.request.urlretrieve(f"{RELEASE_URL}/{target.name}", partial)
        partial.rename(target)
