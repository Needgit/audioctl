"""Logging helpers for audioctl."""

from importlib import import_module

logging = import_module("logging")


def configure_logging(level: int = logging.INFO) -> None:
    """Configure basic logging for the application."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
