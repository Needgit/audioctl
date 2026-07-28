"""Business logic for audioctl."""

from __future__ import annotations

from importlib import import_module
from typing import Iterable

logging = import_module("logging")

from audioctl.models import Config, Profile
from audioctl.pipewire import DeviceStatus, PipeWireError, SinkInfo


class ControllerError(Exception):
    """Raised for controller-specific errors."""


def match_profile(profile: Profile, sink: SinkInfo) -> bool:
    """Return True if sink matches profile rules."""
    if profile.match is not None:
        return sink.name == profile.match
    if profile.prefix is not None and profile.suffix is not None:
        return sink.name.startswith(profile.prefix) and sink.name.endswith(profile.suffix)
    if profile.prefix is not None:
        return sink.name.startswith(profile.prefix)
    if profile.suffix is not None:
        return sink.name.endswith(profile.suffix)
    return False


def find_matching_profiles(config: Config, status: DeviceStatus) -> tuple[Profile, ...]:
    """Return profiles that match available sinks."""
    return tuple(
        profile for profile in config.profiles if any(match_profile(profile, sink) for sink in status.available_sinks)
    )


def get_active_profile(config: Config, status: DeviceStatus) -> Profile | None:
    """Return the active configured profile or None if none match."""
    if status.sink is None:
        return None
    for profile in config.profiles:
        if match_profile(profile, status.sink):
            return profile
    return None


def _cycle_index(current_index: int, count: int, step: int) -> int:
    return (current_index + step) % count


def _resolve_profile_index(config: Config, status: DeviceStatus) -> int:
    active = get_active_profile(config, status)
    if active is None:
        raise ControllerError("No active profile found.")
    for index, profile in enumerate(config.profiles):
        if profile == active:
            return index
    raise ControllerError("Active profile not in configuration.")


def cycle_profile(config: Config, status: DeviceStatus, step: int) -> Profile:
    """Return the next or previous profile that is available."""
    available_profiles = [profile for profile in config.profiles if any(match_profile(profile, sink) for sink in status.available_sinks)]
    if not available_profiles:
        raise ControllerError("No available profiles to cycle.")
    if status.sink is None:
        return available_profiles[0]
    try:
        current_index = next(i for i, profile in enumerate(available_profiles) if match_profile(profile, status.sink))
    except StopIteration:
        return available_profiles[0]
    next_index = _cycle_index(current_index, len(available_profiles), step)
    return available_profiles[next_index]


def select_profile(config: Config, status: DeviceStatus, name: str) -> Profile:
    """Return a requested profile by name."""
    normalized = name.casefold()
    for profile in config.profiles:
        if profile.name.casefold() == normalized:
            if any(match_profile(profile, sink) for sink in status.available_sinks):
                return profile
            raise ControllerError(f"Profile '{name}' is not available.")
    raise ControllerError(f"Profile '{name}' not found.")


def _choose_sink_for_profile(profile: Profile, sinks: Iterable[SinkInfo]) -> SinkInfo:
    matching = [sink for sink in sinks if match_profile(profile, sink)]
    if not matching:
        raise ControllerError(f"Profile '{profile.name}' has no available sink.")
    return min(matching, key=lambda sink: (len(sink.name), sink.name))


def apply_profile(profile: Profile, status: DeviceStatus) -> None:
    """Apply profile to the matching sink."""
    sink = _choose_sink_for_profile(profile, status.available_sinks)
    if status.sink is not None and status.sink.name == sink.name:
        logging.info("Profile '%s' is already active.", profile.name)
    else:
        try:
            from audioctl.pipewire import set_default

            set_default(sink.node)
        except PipeWireError as exc:
            raise ControllerError(str(exc)) from exc
    if profile.volume is not None:
        try:
            from audioctl.pipewire import set_volume

            set_volume(sink.node, profile.volume)
        except PipeWireError as exc:
            raise ControllerError(str(exc)) from exc
