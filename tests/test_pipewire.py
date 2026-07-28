from audioctl.pipewire import get_status


def test_get_status_parses_wpctl_output(monkeypatch):
    sample_output = \
    '''
    PipeWire 'pipewire-0' [1.0.5, user@host, cookie:1834161144]
    └─ Clients:
            32. pipewire                            [1.0.5, user@host, pid:1695]

    Audio
    ├─ Devices:
    │      46. alsa_card.pci-0000_01_00.1          [alsa]
    │      47. alsa_card.usb-Generic_USB_Audio-00  [alsa]
    ├─ Sinks:
    │      33. alsa_output.usb-Logitech_G733_Gaming_Headset_0000000000000000-00.analog-stereo [vol: 0.60]
    │      55. alsa_output.pci-0000_01_00.1.hdmi-stereo [vol: 0.00 MUTED]
    │      56. alsa_output.usb-Generic_USB_Audio-00.HiFi__hw_Audio_2__sink [vol: 5.00 MUTED]
    │      57. alsa_output.usb-Generic_USB_Audio-00.HiFi__hw_Audio_1__sink [vol: 1.00]
    │  *   58. alsa_output.usb-Generic_USB_Audio-00.HiFi__hw_Audio__sink [vol: 0.30]
    │  
    ├─ Sink endpoints:
    '''  # noqa: E501

    monkeypatch.setattr("audioctl.pipewire._run_wpctl", lambda args: sample_output)
    status = get_status()

    assert status.sink is not None
    assert status.sink.name == "alsa_output.usb-Generic_USB_Audio-00.HiFi__hw_Audio__sink"
    assert status.sink.node == "58"
    assert status.sink.active
    assert status.sink.volume == 30
    assert any(sink.name == "alsa_output.usb-Logitech_G733_Gaming_Headset_0000000000000000-00.analog-stereo" for sink in status.available_sinks)
