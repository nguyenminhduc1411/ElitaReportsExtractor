import sys
from pathlib import Path


def resource_path(filename: str) -> Path:
    """
    Return the absolute path of a bundled resource.
    Works for:
    - VS Code / Python
    - PyInstaller one-dir
    - PyInstaller one-file
    """

    if getattr(sys, "frozen", False):

        exe_dir = Path(sys.executable).parent

        internal = exe_dir / "_internal"

        if internal.exists():
            return internal / filename

        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS) / filename

        return exe_dir / filename

    return Path(__file__).resolve().parent / filename