# audioctl Agent Guide

## Project

- `audioctl` is a Linux CLI for managing PipeWire audio output profiles. It supports Python 3.10 and newer; see [pyproject.toml](pyproject.toml) for Python package and test dependencies.
- Runtime audio control requires PipeWire and the external `wpctl` executable. See [README.md](README.md) for setup and runtime details.

## Code Boundaries

- `audioctl/cli.py` owns argument parsing, command dispatch, and CLI output; keep its callable as `cli_main(argv)`.
- `audioctl/__main__.py` owns `main()` and delegates to `audioctl.cli:cli_main`. The console script targets `audioctl.__main__:main` (configured in `pyproject.toml`); preserve this separation.
- `audioctl/controller.py` owns profile matching, selection/cycling, profile application, and volume behavior. `audioctl/pipewire.py` owns `wpctl` subprocess calls, output parsing, and `PipeWireError`.
- `audioctl/config.py` owns TOML validation and persistence. Resolve the config location through `get_default_config_path()` / `audioctl/utils.py`, not a hard-coded user path.

## Tests and Development

- Use the project `.venv`; follow [README.md](README.md) for environment setup, build, and deployment steps. Run tests from the repository root with the environment active: `python -m pytest`.
- Tests in `tests/` use monkeypatching and temporary configuration paths to isolate behavior. PipeWire/`wpctl` calls are mocked, so unit tests need no live audio service.
- Keep wheel builds in `.venv`; `pipx` installs or updates belong outside it and use a separate environment. See the README before deployment.
- `pyproject.toml` defines no lint or type-check command; do not assume one is a project validation gate.