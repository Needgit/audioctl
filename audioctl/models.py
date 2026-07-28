"""Data models for audioctl."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Profile:
    name: str
    match: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    volume: Optional[int] = None


@dataclass(frozen=True)
class Config:
    profiles: tuple[Profile, ...]
    path: Path
