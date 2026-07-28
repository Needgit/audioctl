from audioctl.controller import _choose_sink_for_profile
from audioctl.models import Profile
from audioctl.pipewire import SinkInfo


def test_choose_shortest_matching_sink_for_prefix_suffix() -> None:
    profile = Profile(name="speakers", prefix="alsa_output.usb-Generic_USB_Audio-00.HiFi__hw_", suffix="__sink")
    sinks = [
        SinkInfo(name="alsa_output.usb-Generic_USB_Audio-00.HiFi__hw_Audio_2__sink", node="56", device="...", volume=5, active=False),
        SinkInfo(name="alsa_output.usb-Generic_USB_Audio-00.HiFi__hw_Audio__sink", node="58", device="...", volume=30, active=True),
    ]

    chosen = _choose_sink_for_profile(profile, sinks)

    assert chosen.node == "58"
    assert chosen.name == "alsa_output.usb-Generic_USB_Audio-00.HiFi__hw_Audio__sink"
