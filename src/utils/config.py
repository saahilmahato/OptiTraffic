import yaml
from pathlib import Path
from typing import Any


def load_config(path: str) -> dict[str, Any]:
    """
    Load a YAML configuration file from the given path.

    Args:
        path (str): The file path to the YAML config.

    Returns:
        dict[str, Any]: Parsed configuration as a dictionary.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        yaml.YAMLError: If the file is not a valid YAML document.
    """
    config_path = Path(path)
    if not config_path.is_file():
        raise FileNotFoundError(f"Config file not found: {path}")

    with config_path.open("r") as file:
        return yaml.safe_load(file)
