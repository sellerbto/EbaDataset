from pathlib import Path
from .core.communication.system import normalize_env_paths

normalize_env_paths(Path("eba_file_tracker") / "var" / ".env")
