import pytest
from pathlib import Path

from audioctl.controller import ControllerError, cycle_profile, get_active_profile, select_profile
from audioctl.models import Config, Profile
from audioctl.pipewire import DeviceStatus, SinkInfo


def make_status(active_name: str | None, names: list[str]) -> DeviceStatus:
    sinks = []
    for name in names:
        sinks.append(SinkInfo(name=name, node=f"node-{name}", device=name, volume=50, active=name == active_name))
    active_sink = next((sink for sink in sinks if sink.active), None)
    return DeviceStatus(sink=active_sink, available_sinks=tuple(sinks))


def test_cycle_profile_next() -> None:
    config = Config(
        profiles=(
            Profile(name="headset", match="sink-1"),
            Profile(name="speakers", match="sink-2"),
        ),
        path=Path("/tmp/config.toml"),
    )
    status = make_status("sink-1", ["sink-1", "sink-2"])

    next_profile = cycle_profile(config, status, step=1)

    assert next_profile.name == "speakers"


def test_cycle_profile_previous() -> None:
    config = Config(
        profiles=(
            Profile(name="headset", match="sink-1"),
            Profile(name="speakers", match="sink-2"),
        ),
        path=Path("/tmp/config.toml"),
    )
    status = make_status("sink-1", ["sink-1", "sink-2"])

    previous_profile = cycle_profile(config, status, step=-1)

    assert previous_profile.name == "speakers"


def test_select_profile_found() -> None:
    config = Config(
        profiles=(
            Profile(name="headset", match="sink-1"),
            Profile(name="speakers", match="sink-2"),
        ),
        path=Path("/tmp/config.toml"),
    )
    status = make_status(None, ["sink-2"])

    profile = select_profile(config, status, "Speakers")

    assert profile.name == "speakers"


def test_select_profile_unavailable() -> None:
    config = Config(
        profiles=(Profile(name="headset", match="sink-1"),),
        path=Path("/tmp/config.toml"),
    )
    status = make_status(None, ["sink-2"])

    with pytest.raises(ControllerError):
        select_profile(config, status, "headset")


def test_select_profile_not_found() -> None:
    config = Config(
        profiles=(Profile(name="headset", match="sink-1"),),
        path=Path("/tmp/config.toml"),
    )
    status = make_status(None, ["sink-1"])

    with pytest.raises(ControllerError):
        select_profile(config, status, "unknown")
