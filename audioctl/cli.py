"""Command-line interface for audioctl."""

from __future__ import annotations

import argparse
from importlib import import_module
import sys
from pathlib import Path

logging = import_module("logging")

from audioctl.config import ConfigurationError, get_default_config_path, load_config, save_config
from audioctl.controller import (
    ControllerError,
    apply_profile,
    cycle_profile,
    get_active_profile,
    match_profile,
    select_profile,
)
from audioctl.logconfig import configure_logging
from audioctl.pipewire import DeviceStatus, PipeWireError, get_status
from audioctl.models import Config, Profile


EXIT_CONFIG = 2
EXIT_PIPEWIRE = 3
EXIT_PROFILE_NOT_FOUND = 4


def _print_profile(profile: Profile, active: bool, available: bool) -> None:
    status = "active" if active else "available" if available else "unavailable"
    print(f"{profile.name}: {status}")


def _print_status(config: Config, status: DeviceStatus) -> None:
    active_profile = get_active_profile(config, status)
    if active_profile is None:
        print("Active profile: none")
    else:
        print(f"Active profile: {active_profile.name}")
    if status.sink is None:
        print("PipeWire node: none")
        print("Configured volume: none")
        return
    print(f"PipeWire node: {status.sink.node}")
    print(f"Configured volume: {status.sink.volume}%")


def _list_profiles(config: Config, status: DeviceStatus) -> None:
    for profile in config.profiles:
        available = any(match_profile(profile, sink) for sink in status.available_sinks)
        active = status.sink is not None and match_profile(profile, status.sink)
        _print_profile(profile, active=active, available=available)


def _initialize_config(path: Path | None = None) -> None:
    config_path = path or get_default_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    default = Config(profiles=(), path=config_path)
    save_config(default)
    print(f"Initialized configuration at {config_path}")


def _load_status() -> DeviceStatus:
    try:
        return get_status()
    except PipeWireError as exc:
        raise SystemExit(EXIT_PIPEWIRE) from exc


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    parser = argparse.ArgumentParser(prog="audioctl")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("next", help="switch to the next available profile")
    subparsers.add_parser("previous", help="switch to the previous available profile")
    use_parser = subparsers.add_parser("use", help="switch to a named profile")
    use_parser.add_argument("name", help="profile name to activate")
    subparsers.add_parser("status", help="show current active profile and sink status")
    profiles_parser = subparsers.add_parser("profiles", help="profile configuration management")
    profiles_subparsers = profiles_parser.add_subparsers(dest="profiles_command")
    profiles_subparsers.add_parser("init", help="initialize configuration file")
    profiles_subparsers.add_parser("list", help="list configured profiles")
    # volume controls
    volume_parser = subparsers.add_parser("volume", help="control sink volume")
    volume_subparsers = volume_parser.add_subparsers(dest="volume_command")
    vol_set = volume_subparsers.add_parser("set", help="set volume to a value")
    vol_set.add_argument("value", type=int, help="volume percent (0-100)")
    volume_subparsers.add_parser("reset", help="reset volume to the active profile value")
    vol_up = volume_subparsers.add_parser("up", help="increase volume by step")
    vol_up.add_argument("--step", "-s", type=int, default=5, help="step in percent")
    vol_down = volume_subparsers.add_parser("down", help="decrease volume by step")
    vol_down.add_argument("--step", "-s", type=int, default=5, help="step in percent")

    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 1

    try:
        if args.command == "profiles":
            if args.profiles_command == "list":
                config = load_config(None)
                status = _load_status()
                _list_profiles(config, status)
                return 0
            if args.profiles_command == "init":
                _initialize_config()
                return 0
            profiles_parser.print_help()
            return 1

        if args.command == "volume" and getattr(args, "volume_command", None) is None:
            volume_parser.print_help()
            return 1

        config = load_config(None)
        status = _load_status()

        if args.command == "volume":
            try:
                if args.volume_command == "set":
                    from audioctl.controller import set_volume_now

                    set_volume_now(status, args.value)
                    print(f"Set volume to {args.value}%")
                    return 0
                if args.volume_command == "up":
                    from audioctl.controller import adjust_volume

                    new = adjust_volume(status, int(args.step))
                    print(f"Volume increased to {new}%")
                    return 0
                if args.volume_command == "down":
                    from audioctl.controller import adjust_volume

                    new = adjust_volume(status, -int(args.step))
                    print(f"Volume decreased to {new}%")
                    return 0
                if args.volume_command == "reset":
                    from audioctl.controller import reset_volume_to_profile

                    vol = reset_volume_to_profile(config, status)
                    print(f"Volume reset to {vol}%")
                    return 0
            except ControllerError as exc:
                logging.warning(str(exc))
                print(str(exc))
                return 1

        if args.command == "next":
            profile = cycle_profile(config, status, step=1)
            apply_profile(profile, status)
            print(f"Switched to {profile.name}")
            return 0
        if args.command == "previous":
            profile = cycle_profile(config, status, step=-1)
            apply_profile(profile, status)
            print(f"Switched to {profile.name}")
            return 0
        if args.command == "use":
            profile = select_profile(config, status, args.name)
            apply_profile(profile, status)
            print(f"Switched to {profile.name}")
            return 0
        # Note: no top-level `list` command. Use `audioctl profiles list`.
        if args.command == "status":
            _print_status(config, status)
            return 0
    except ConfigurationError as exc:
        logging.warning(str(exc))
        print(f"Configuration error: {exc}")
        return EXIT_CONFIG
    except ControllerError as exc:
        logging.warning(str(exc))
        if "not found" in str(exc).lower():
            print(str(exc))
            return EXIT_PROFILE_NOT_FOUND
        print(str(exc))
        return 1
    except SystemExit as exc:
        raise
    except Exception as exc:
        logging.exception("Unexpected error")
        print(f"Error: {exc}")
        return 1

    return 1
