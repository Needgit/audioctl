# audioctl

audioctl is a lightweight command-line utility for Linux that manages PipeWire audio output profiles.

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

## Configuration

The configuration file is stored at:

- `$XDG_CONFIG_HOME/audioctl/config.toml`
- or `~/.config/audioctl/config.toml` if `XDG_CONFIG_HOME` is not set.

Create the config by adding a profile (the command will create the config if missing):

```bash
audioctl profiles add headset --match alsa_output.usb-Headset --volume 60
```

A sample configuration for a headset and speaker profile:

```toml
[[profiles]]
name = "headset"
match = "alsa_output.usb-Logitech_G733_Gaming_Headset_0000000000000000-00.analog-stereo"
volume = 60

[[profiles]]
name = "speakers"
prefix = "alsa_output.usb-Generic_USB_Audio-00.HiFi__hw_"
suffix = "__sink"
volume = 30
```

## Usage

```bash
audioctl next
audioctl previous
audioctl use <profile>
audioctl status
audioctl profiles init
audioctl profiles list
```

## Testing

Install test dependencies in the virtual environment and run:

```bash
pip install -e .[test]
python -m pytest
```

## Disclaimer

- This project was created with assistance from GitHub Copilot. The generated code and documentation have been reviewed and edited by a human maintainer.

