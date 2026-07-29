# audioctl

audioctl is a lightweight command-line utility for Linux that manages PipeWire audio output profiles.

It depends on PipeWire and the `wpctl` command-line tool to query and control sinks.

I made this tool because I wanted a quick way to switch between headset and speaker setups, and to keep volume stable when I switch. Since the volume encoder on my keyboard is not behaving consistently, I also wanted a reliable command-line fallback that I can bind to keyboard shortcuts.

>This project was created with assistance from GitHub Copilot. The generated code and documentation have been reviewed and edited by a human maintainer.

## Usage

```bash
audioctl next
audioctl previous
audioctl use <profile>
audioctl status
audioctl profiles list
```

### Configuration

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

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

## Testing

Install test dependencies in the virtual environment and run:

```bash
pip install -e .[test]
python -m pytest
```

## Local Deployment

You can build the distribution inside the project's development virtualenv (recommended), then install the built wheel outside the venv using `pipx` so the `audioctl` command is available system-wide for your user.

### Build in the project `.venv`

Run these commands from the repository root. This builds the wheel using the environment you use for development:

```bash
python -m pip install --upgrade pip build
python -m build
deactivate
```

The built artifacts will be in `dist/`.

### Install with `pipx` (outside the `.venv`)

Install `pipx` if you don't have it, then install the wheel from `dist/` (run these commands outside the activated `.venv`):

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install dist/*.whl
```

To upgrade later, rebuild in the `.venv` and then run:

```bash
python -m build
pipx install --force dist/*.whl
```

### Simple wrapper script (alternative)

If you prefer not to build/install, you can install a small wrapper script to `~/.local/bin` that invokes the project directly. An installer script is provided at `./scripts/install-wrapper.sh` which writes a venv-aware wrapper into `~/.local/bin/audioctl`.

```bash
bash ./scripts/install-wrapper.sh
```

Or create the wrapper manually (replace `/path/to/repo` with the project root):

```bash
mkdir -p ~/.local/bin
cat > ~/.local/bin/audioctl <<'EOF'
#!/usr/bin/env bash
# Replace /path/to/repo with the path to this project's root directory
REPO="/path/to/repo"
if [ -x "$REPO/.venv/bin/python" ]; then
	exec "$REPO/.venv/bin/python" "$REPO/audioctl/__main__.py" "$@"
else
	exec python3 "$REPO/audioctl/__main__.py" "$@"
fi
EOF
chmod +x ~/.local/bin/audioctl
```

Ensure `~/.local/bin` is on your `PATH` so the `audioctl` command is found.
