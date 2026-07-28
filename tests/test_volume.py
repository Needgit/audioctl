from pathlib import Path

from audioctl.controller import adjust_volume, set_volume_now, reset_volume_to_profile, ControllerError
from audioctl.models import Config, Profile
from audioctl.pipewire import DeviceStatus, SinkInfo


class DummyCalled:
    def __init__(self):
        self.called = False
        self.args = None


def make_status(active_name: str | None, names: list[str], volumes: dict[str, int] | None = None) -> DeviceStatus:
    sinks = []
    for name in names:
        vol = 0
        if volumes and name in volumes:
            vol = volumes[name]
        sinks.append(SinkInfo(name=name, node=f"node-{name}", device=name, volume=vol, active=name == active_name))
    active_sink = next((sink for sink in sinks if sink.active), None)
    return DeviceStatus(sink=active_sink, available_sinks=tuple(sinks))


def test_adjust_volume_calls_pipewire(monkeypatch):
    status = make_status("sink-1", ["sink-1"], volumes={"sink-1": 50})

    called = DummyCalled()

    def fake_set_volume(node, vol):
        called.called = True
        called.args = (node, vol)

    monkeypatch.setattr("audioctl.pipewire.set_volume", fake_set_volume, raising=False)

    new = adjust_volume(status, 5)
    assert called.called
    assert called.args[1] == 55
    assert new == 55


def test_set_volume_now_no_sink_raises():
    status = make_status(None, ["sink-1"], volumes={"sink-1": 50})
    try:
        set_volume_now(status, 30)
        raised = False
    except ControllerError:
        raised = True
    assert raised


def test_reset_volume_no_profile_raises():
    config = Config(profiles=(), path=Path("/tmp/config.toml"))
    status = make_status("sink-1", ["sink-1"], volumes={"sink-1": 40})
    try:
        reset_volume_to_profile(config, status)
        raised = False
    except ControllerError:
        raised = True
    assert raised


def test_reset_volume_applies_profile(monkeypatch):
    profile = Profile(name="headset", match="sink-1", volume=60)
    config = Config(profiles=(profile,), path=Path("/tmp/config.toml"))
    status = make_status("sink-1", ["sink-1"], volumes={"sink-1": 40})

    called = DummyCalled()

    def fake_set_volume(node, vol):
        called.called = True
        called.args = (node, vol)

    monkeypatch.setattr("audioctl.pipewire.set_volume", fake_set_volume, raising=False)

    vol = reset_volume_to_profile(config, status)
    assert called.called
    assert vol == 60
 