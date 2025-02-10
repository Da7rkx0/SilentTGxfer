import os
import sys
import subprocess
from pathlib import Path

def build_exe():
    """Build the executable"""
    subprocess.run([
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--hidden-import=telegram.ext.filters",
        "--hidden-import=win32timezone",
        "--name=FileIndexerService",
        "SilentTGxfer.py"
    ], check=True)

if __name__ == "__main__":
    # Build the executable
    build_exe()
