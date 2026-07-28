from pathlib import Path

import pytest

from audioctl.config import ConfigurationError, load_config, save_config
from audioctl.models import Config, Profile


def test_load_config_valid(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
[[profiles]]
name = "headset"
match = "sink-1"
volume = 50
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert isinstance(config, Config)
    assert config.path == config_path
    assert config.profiles == (Profile(name="headset", match="sink-1", prefix=None, suffix=None, volume=50),)


def test_load_config_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError):
        load_config(tmp_path / "missing.toml")


def test_save_config(tmp_path: Path) -> None:
    config = Config(profiles=(Profile(name="speakers", prefix="sink-", suffix=None, volume=30),), path=tmp_path / "config.toml")
    save_config(config)

    assert config.path.exists()
    content = config.path.read_text(encoding="utf-8")
    assert "name = \"speakers\"" in content
    assert "prefix = \"sink-\"" in content
    assert "volume = 30" in content
