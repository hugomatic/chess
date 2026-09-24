"""Resolve the small amount of filesystem context needed by the CAD CLI."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectContext:
    root: Path
    data_dir: Path


def resolve_context(env: Mapping[str, str] | None = None) -> ProjectContext:
    values = os.environ if env is None else env
    package_root = Path(__file__).resolve().parents[1]
    root = Path(values.get("CHESS_ROOT", package_root)).expanduser().resolve()
    data_dir = Path(values.get("CHESS_DATA_DIR", root / "data")).expanduser().resolve()
    return ProjectContext(root=root, data_dir=data_dir)
