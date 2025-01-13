from pathlib import Path
from .core.communication.system import normalize_env_paths

normalize_env_paths(Path("file_tracker") / "var" / ".env")
