"""Utility helpers for audioctl."""

from pathlib import Path
import os


def get_config_home() -> Path:
    """Return the configuration home directory following XDG Base Directory spec."""
    xdg_home = os.getenv("XDG_CONFIG_HOME")
    if xdg_home:
        return Path(xdg_home)
    return Path.home() / ".config"
