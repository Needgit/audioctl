"""Configuration management for audioctl."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import tomli
import tomli_w

from audioctl.models import Config, Profile
from audioctl.utils import get_config_home


class ConfigurationError(Exception):
    """Raised when configuration cannot be loaded or validated."""


def get_default_config_path() -> Path:
    """Return the default config file path."""
    return get_config_home() / "audioctl" / "config.toml"


def load_config(path: Path | None = None) -> Config:
    """Load and validate configuration from a TOML file."""
    config_path = path or get_default_config_path()
    try:
        raw = tomli.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigurationError(f"Configuration file not found: {config_path}") from exc
    except tomli.TOMLDecodeError as exc:
        raise ConfigurationError(f"Invalid TOML configuration: {exc}") from exc

    profiles_data = raw.get("profiles")
    if not isinstance(profiles_data, list):
        raise ConfigurationError("Configuration must include a profiles table array.")

    profiles: list[Profile] = []
    for profile_data in profiles_data:
        if not isinstance(profile_data, dict):
            raise ConfigurationError("Each profile must be a table in config.")
        name = profile_data.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ConfigurationError("Each profile must have a non-empty name.")

        match = profile_data.get("match")
        prefix = profile_data.get("prefix")
        suffix = profile_data.get("suffix")
        volume = profile_data.get("volume")

        if volume is not None:
            if not isinstance(volume, int) or not 0 <= volume <= 100:
                raise ConfigurationError("Profile volume must be an integer between 0 and 100.")

        if match is not None and not isinstance(match, str):
            raise ConfigurationError("Profile match value must be a string.")
        if prefix is not None and not isinstance(prefix, str):
            raise ConfigurationError("Profile prefix value must be a string.")
        if suffix is not None and not isinstance(suffix, str):
            raise ConfigurationError("Profile suffix value must be a string.")

        if not any([match, prefix, suffix]):
            raise ConfigurationError(
                f"Profile '{name}' must define match, prefix, or suffix."
            )

        profiles.append(Profile(name=name, match=match, prefix=prefix, suffix=suffix, volume=volume))

    return Config(profiles=tuple(profiles), path=config_path)


def save_config(config: Config) -> None:
    """Save configuration to the config file path."""
    data: dict[str, Any] = {
        "profiles": [
            {
                "name": profile.name,
                **({"match": profile.match} if profile.match is not None else {}),
                **({"prefix": profile.prefix} if profile.prefix is not None else {}),
                **({"suffix": profile.suffix} if profile.suffix is not None else {}),
                **({"volume": profile.volume} if profile.volume is not None else {}),
            }
            for profile in config.profiles
        ]
    }
    config.path.parent.mkdir(parents=True, exist_ok=True)
    config.path.write_text(tomli_w.dumps(data), encoding="utf-8")
