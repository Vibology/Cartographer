import sys
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
from pathlib import Path

def get_version() -> str:
    """Reads the project version from pyproject.toml."""
    current_file = Path(__file__).resolve()
    # Go up: utils -> cartographer -> src -> root
    root_dir = current_file.parent.parent.parent.parent
    pyproject_path = root_dir / "pyproject.toml"

    if pyproject_path.exists():
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version", "0.0.0")

    return "0.0.0"
