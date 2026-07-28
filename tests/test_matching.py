from audioctl.controller import match_profile
from audioctl.models import Profile
from audioctl.pipewire import SinkInfo


def test_match_profile_exact() -> None:
    profile = Profile(name="headset", match="sink-1")
    sink = SinkInfo(name="sink-1", node="node-1", device="sink-1", volume=50, active=True)

    assert match_profile(profile, sink)


def test_match_profile_prefix() -> None:
    profile = Profile(name="speakers", prefix="usb-")
    sink = SinkInfo(name="usb-sink-a", node="node-a", device="usb-sink-a", volume=30, active=False)

    assert match_profile(profile, sink)


def test_match_profile_suffix() -> None:
    profile = Profile(name="desk", suffix="-sink")
    sink = SinkInfo(name="main-sink", node="node-b", device="main-sink", volume=20, active=False)

    assert match_profile(profile, sink)


def test_match_profile_prefix_and_suffix() -> None:
    profile = Profile(name="combo", prefix="usb-", suffix="-sink")
    sink = SinkInfo(name="usb-main-sink", node="node-c", device="usb-main-sink", volume=40, active=False)

    assert match_profile(profile, sink)


def test_match_profile_no_match() -> None:
    profile = Profile(name="other", prefix="alsa", suffix="-sink")
    sink = SinkInfo(name="usb-main-sink", node="node-d", device="usb-main-sink", volume=40, active=False)

    assert not match_profile(profile, sink)
