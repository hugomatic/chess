#!/usr/bin/env python3
"""Create a LibreCAD-ready DXF: rectangle with a round hole and dimensions.

Run from the repo root:

    uv run --with ezdxf python boat_plan/create_rectangle.py

Output: boat_plan/rectangle_with_hole.dxf
"""

from pathlib import Path

import ezdxf
from ezdxf import units

OUT = Path(__file__).with_name("rectangle_with_hole.dxf")

WIDTH = 100.0
HEIGHT = 60.0
HOLE_DIA = 20.0
HOLE_R = HOLE_DIA / 2.0
CENTER = (WIDTH / 2.0, HEIGHT / 2.0)
DIM_OFFSET = 18.0


def _dimstyle(doc: ezdxf.EzDxfDocument) -> str:
    if "BOAT" not in doc.dimstyles:
        style = doc.dimstyles.duplicate_entry("EZDXF", "BOAT")
        style.dxf.dimtxt = 3.0
        style.dxf.dimasz = 2.5
        style.dxf.dimexe = 1.5
        style.dxf.dimexo = 2.0
        style.dxf.dimgap = 1.0
        style.dxf.dimdec = 1
        style.dxf.dimzin = 8  # suppress trailing zeros
    return "BOAT"


def build() -> None:
    # R2000 is the most reliable LibreCAD interchange version.
    doc = ezdxf.new("R2000", setup=True)
    doc.units = units.MM
    doc.header["$INSUNITS"] = units.MM
    doc.header["$MEASUREMENT"] = 1

    doc.layers.add("GEOMETRY", color=7)
    doc.layers.add("HOLE", color=1)
    doc.layers.add("DIMS", color=3)

    msp = doc.modelspace()
    dimstyle = _dimstyle(doc)

    msp.add_lwpolyline(
        [(0, 0), (WIDTH, 0), (WIDTH, HEIGHT), (0, HEIGHT)],
        close=True,
        dxfattribs={"layer": "GEOMETRY"},
    )
    msp.add_circle(CENTER, HOLE_R, dxfattribs={"layer": "HOLE"})

    width_dim = msp.add_linear_dim(
        base=(WIDTH / 2.0, -DIM_OFFSET),
        p1=(0, 0),
        p2=(WIDTH, 0),
        dimstyle=dimstyle,
        dxfattribs={"layer": "DIMS"},
    )
    width_dim.render()

    height_dim = msp.add_linear_dim(
        base=(-DIM_OFFSET, HEIGHT / 2.0),
        p1=(0, 0),
        p2=(0, HEIGHT),
        angle=90,
        dimstyle=dimstyle,
        dxfattribs={"layer": "DIMS"},
    )
    height_dim.render()

    hole_dim = msp.add_diameter_dim(
        center=CENTER,
        radius=HOLE_R,
        angle=45,
        dimstyle=dimstyle,
        dxfattribs={"layer": "DIMS"},
    )
    hole_dim.render()

    doc.saveas(OUT)


if __name__ == "__main__":
    build()
    print(OUT.resolve())
