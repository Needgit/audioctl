import os
from pathlib import Path

import tomli

from audioctl.cli import cli_main
from audioctl.config import load_config


def test_profiles_add_and_remove(tmp_path, monkeypatch, capsys):
    # isolate config
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    # add a profile
    rc = cli_main(["profiles", "add", "headset", "--match", "alsa_output.foo", "--volume", "60"])
    assert rc == 0
    cfg = load_config(None)
    assert any(p.name == "headset" for p in cfg.profiles)

    # add another profile
    rc = cli_main(["profiles", "add", "Speakers", "--prefix", "alsa_output.bar", "--volume", "30"])
    assert rc == 0
    cfg = load_config(None)
    assert any(p.name == "Speakers" for p in cfg.profiles)

    # remove case-insensitively
    rc = cli_main(["profiles", "remove", "HEADSET"])
    captured = capsys.readouterr()
    assert rc == 0
    cfg = load_config(None)
    assert not any(p.name.lower() == "headset" for p in cfg.profiles)
    # ensure speakers still present
    assert any(p.name == "Speakers" for p in cfg.profiles)
 