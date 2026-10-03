# audioctl

audioctl is a lightweight command-line utility for Linux that manages PipeWire audio output profiles.

It depends on PipeWire and the `wpctl` command-line tool to query and control sinks.

I made this tool because I wanted a quick way to switch between headset and speaker setups, and to keep volume stable when I switch. Since the volume encoder on my keyboard is not behaving consistently, I also wanted a reliable command-line fallback that I can bind to keyboard shortcuts.

> This project was created with assistance from GitHub Copilot. The generated code and documentation have been reviewed and edited by a human maintainer.

## Usage

Basic profile switching:

```bash
audioctl next
audioctl previous
audioctl use <profile>
audioctl status
```

Profile configuration and discovery:

```bash
audioctl profiles list
audioctl profiles sinks
audioctl profiles add <name> --match <sink-name> [--volume <percent>]
audioctl profiles remove <name>
```

Volume control:

```bash
audioctl volume set <percent>
audioctl volume up --step 5
audioctl volume down --step 5
audioctl volume reset
```

`audioctl profiles add` will create the config file if it does not already exist. `audioctl volume reset` restores the configured volume for the active profile when available.

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
python -m pip install -e .
```

## Testing

Install test dependencies in the virtual environment and run:

```bash
python -m pip install -e '.[test]'
python -m pytest
```

## Local Releases

Package versions come from Git tags via `setuptools-scm`; do not set the version in `pyproject.toml` or `audioctl/__init__.py`. Create a tag on the committed release changes, then refresh the editable install so `audioctl --version` reports that tag:

```bash
git tag -a v0.1.0 -m "audioctl 0.1.0"
python -m pip install -e .
python -m audioctl --version
```

Use a new version tag for each release; do not move or reuse a published version tag. To build locally, follow the wheel build steps below. Checkouts without usable Git metadata fall back to `0.0.dev0`.

## Local Deployment

You can build a wheel in the project's development venv, then install it with `pipx` so the `audioctl` command is available to your user. `pipx` creates a separate virtual environment for the installed application; it does not install the application into the project `.venv` or system Python.

### Build in the project `.venv`

Run these commands from the repository root while the project `.venv` is active. This builds the wheel from the project source:

```bash
python -m pip install --upgrade pip build
python -m build
```

The built artifacts will be in `dist/`.

### Install with `pipx` (outside the `.venv`)

After building the wheel, deactivate the project `.venv` before running these commands. Install `pipx` if you don't have it, then install the wheel from `dist/`:

```bash
deactivate

# Dependencies
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Deploy
pipx install dist/*.whl

# Return to the development environment
source .venv/bin/activate
```

To deploy an updated build, first rerun your tests against the development install in `.venv` (the editable install uses your current source files). Build while `.venv` is active, then deactivate it before updating the separate `pipx` installation. Reactivate `.venv` afterward to continue development:

```bash
# In the project .venv, from the repository root
python -m build
deactivate

# Outside .venv, from the repository root
pipx install --force dist/*.whl

# Return to the development environment
source .venv/bin/activate
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
