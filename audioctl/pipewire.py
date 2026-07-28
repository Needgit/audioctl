"""PipeWire backend for audioctl."""

from __future__ import annotations

from importlib import import_module
import re
import subprocess

logging = import_module("logging")
from dataclasses import dataclass
from typing import NamedTuple


class PipeWireError(Exception):
    """Raised when PipeWire interaction fails."""


@dataclass(frozen=True)
class SinkInfo:
    name: str
    node: str
    device: str
    volume: int
    active: bool


class DeviceStatus(NamedTuple):
    sink: SinkInfo | None
    available_sinks: tuple[SinkInfo, ...]


def _run_wpctl(args: list[str]) -> str:
    cmd = ["wpctl", *args]
    logging.debug("Running wpctl command: %s", cmd)
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return completed.stdout.strip()
    except subprocess.CalledProcessError as exc:
        raise PipeWireError(f"wpctl failed: {exc.stderr.strip() or exc}") from exc
    except FileNotFoundError as exc:
        raise PipeWireError("wpctl command not found") from exc


def get_status() -> DeviceStatus:
    """Return current sink status and available sinks."""
    output = _run_wpctl(["status", "-n"])
    sinks: list[SinkInfo] = []
    active_sink: SinkInfo | None = None
    in_sinks_section = False
    sink_line = re.compile(
        r"^.*?(?P<active>\*)?\s*(?P<id>\d+)\.\s+(?P<name>\S+)\s+\[vol:\s*(?P<volume>[0-9.]+)(?:\s*MUTED)?"
    )

    for line in output.splitlines():
        stripped = line.strip()
        if stripped.endswith("Sinks:"):
            in_sinks_section = True
            continue
        if in_sinks_section and stripped.endswith("Sources:"):
            break
        if not in_sinks_section:
            continue
        match = sink_line.match(line)
        if not match:
            continue

        name = match.group("name")
        active = bool(match.group("active"))
        try:
            volume = int(round(float(match.group("volume")) * 100))
        except ValueError:
            volume = 0

        info = SinkInfo(name=name, node=match.group("id"), device=name, volume=volume, active=active)
        sinks.append(info)
        if active:
            active_sink = info

    return DeviceStatus(sink=active_sink, available_sinks=tuple(sinks))


def set_default(sink_name: str) -> None:
    """Set the default audio sink."""
    _run_wpctl(["set-default", sink_name])


def set_volume(sink_name: str, volume: int) -> None:
    """Set volume for a sink."""
    _run_wpctl(["set-volume", sink_name, f"{volume}%"])
