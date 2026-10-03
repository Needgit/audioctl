"""audioctl package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("audioctl")
except PackageNotFoundError:
    __version__ = "0+unknown"

__all__ = ["cli", "controller", "pipewire", "config", "models", "utils"]
