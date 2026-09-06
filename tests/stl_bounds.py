from __future__ import annotations

from pathlib import Path
import re
import struct


_VERTEX = re.compile(
    rb"^\s*vertex\s+"
    rb"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)\s+"
    rb"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)\s+"
    rb"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)\s*$",
    re.MULTILINE,
)


def read_stl_bounds(
    path: Path,
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    data = path.read_bytes()
    points: list[tuple[float, float, float]] = []
    if len(data) >= 84:
        count = struct.unpack_from("<I", data, 80)[0]
        if len(data) == 84 + count * 50:
            for index in range(count):
                values = struct.unpack_from("<9f", data, 84 + index * 50 + 12)
                points.extend((values[0:3], values[3:6], values[6:9]))
    if not points:
        points = [
            tuple(float(value) for value in match.groups())
            for match in _VERTEX.finditer(data)
        ]
    if not points:
        raise ValueError(f"STL contains no vertices: {path}")
    return (
        tuple(min(point[axis] for point in points) for axis in range(3)),
        tuple(max(point[axis] for point in points) for axis in range(3)),
    )
