from pathlib import Path

import pytest

from audioctl import __version__
from audioctl.cli import cli_main
from audioctl.models import Config, Profile
from audioctl.pipewire import DeviceStatus, SinkInfo


def make_status(active_name: str | None, names: list[str]) -> DeviceStatus:
    sinks = []
    for name in names:
        sinks.append(SinkInfo(name=name, node=f"node-{name}", device=name, volume=50, active=name == active_name))
    active_sink = next((sink for sink in sinks if sink.active), None)
    return DeviceStatus(sink=active_sink, available_sinks=tuple(sinks))


def test_version_option(capsys):
    with pytest.raises(SystemExit) as exc_info:
        cli_main(["--version"])

    assert exc_info.value.code == 0
    assert capsys.readouterr().out == f"audioctl {__version__}\n"


def test_profiles_without_subcommand_prints_profiles_help(monkeypatch, capsys):
    exit_code = cli_main(["profiles"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "usage: audioctl profiles" in captured.out
    assert "list" in captured.out
    assert "sinks" in captured.out


def test_profiles_list_shows_available_profiles(monkeypatch, capsys):
    config = Config(
        profiles=(
            Profile(name="headset", match="sink-1"),
            Profile(name="speakers", prefix="usb-", suffix="-sink"),
        ),
        path=Path("/tmp/config.toml"),
    )
    status = make_status("sink-1", ["sink-1", "usb-main-sink"])

    monkeypatch.setattr("audioctl.cli.load_config", lambda _: config)
    monkeypatch.setattr("audioctl.cli.get_status", lambda: status)

    exit_code = cli_main(["profiles", "list"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "headset: active" in captured.out
    assert "speakers: available" in captured.out
