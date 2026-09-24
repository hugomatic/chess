#!/usr/bin/env python3
"""LibreCAD-ready top, side, and back views of infaltable_boat, with measurements.

Dimensions match things/infaltable_boat/infaltable_boat.scad (full size, mm).
Stern is at X=0, bow to the right. Side view sits above the aligned top view.
Back view sits to the left of the side view, keel aligned.

Run from the repo root:

    uv run --with ezdxf python boat_plan/infaltable_boat_plan.py

Output: boat_plan/infaltable_boat_plan.dxf
"""

from __future__ import annotations

from math import atan2, degrees, hypot, radians, tan
from pathlib import Path

import ezdxf
from ezdxf import units
from ezdxf.enums import TextEntityAlignment

OUT = Path(__file__).with_name("infaltable_boat_plan.dxf")

BOAT_LENGTH = 4267.2
OVERALL_WIDTH = 1828.8
TUBE_DIAMETER = 457.2
FLOOR_THICKNESS = 152.4
BOW_HEIGHT = 609.6
BOW_RISE_LENGTH = 914.4
TRANSOM_INSET = 609.6
TRANSOM_WIDTH = 1371.6
TRANSOM_HEIGHT = 457.2
TRANSOM_THICKNESS = 38.1

TUBE_RADIUS = TUBE_DIAMETER / 2.0
TUBE_CENTER_X = OVERALL_WIDTH / 2.0 - TUBE_RADIUS
CHANNEL_WIDTH = OVERALL_WIDTH - 2.0 * TUBE_DIAMETER
BOW_FLAT = 304.8
BOW_FRONT_Y = BOAT_LENGTH - TUBE_RADIUS
BOW_ANGLE_START_Y = BOW_FRONT_Y - TUBE_CENTER_X
BOW_CORNER_X = BOW_FLAT / 2.0
BOW_CENTER_Z = BOW_HEIGHT - TUBE_RADIUS
BOW_RISE_START_Y = BOW_FRONT_Y - BOW_RISE_LENGTH
KNUCKLE_CENTER_Z = (
    TUBE_RADIUS
    + (BOW_ANGLE_START_Y - BOW_RISE_START_Y) / BOW_RISE_LENGTH * (BOW_HEIGHT - TUBE_DIAMETER)
)
KNUCKLE_TOP_Z = KNUCKLE_CENTER_Z + TUBE_RADIUS
TRANSOM_Y = TUBE_RADIUS + TRANSOM_INSET
FLOOR_REAR_Y = TRANSOM_Y
FLOOR_FRONT_Y = BOW_FRONT_Y - TUBE_RADIUS
HALF_WIDTH = OVERALL_WIDTH / 2.0
HALF_CHANNEL = CHANNEL_WIDTH / 2.0
TRANSOM_TOP = TRANSOM_HEIGHT
TRANSOM_Y0 = TRANSOM_Y - TRANSOM_THICKNESS / 2.0
TRANSOM_Y1 = TRANSOM_Y + TRANSOM_THICKNESS / 2.0
MOTOR_DROP = 152.4
MOTOR_ANGLE = 30.0
MOTOR_FLAT = 304.8
MOTOR_FLARE = MOTOR_DROP * tan(radians(MOTOR_ANGLE))
MOTOR_WELL_Z = TRANSOM_TOP - MOTOR_DROP
MOTOR_WELL_TOP = MOTOR_FLAT / 2.0 + MOTOR_FLARE
HANDLE_LENGTH = 203.2
HANDLE_WIDTH = 50.8
HANDLE_STOCK = 12.7
HANDLE_STANDOFF = 38.1
DRING_WIDTH = 50.8
DRING_STOCK = 8.0
HANDLE_SPAN = BOW_ANGLE_START_Y - TRANSOM_Y
HANDLE_AFT_Y = TRANSOM_Y + HANDLE_SPAN / 6.0
HANDLE_FWD_Y = TRANSOM_Y + 5.0 * HANDLE_SPAN / 6.0
HANDLE_YS = (HANDLE_AFT_Y, HANDLE_FWD_Y)

# Side view uses boat (length, height). Top view is directly below, same length axis.
# Back view sits to the left of the side view, keel aligned with the side view.
DIM = 260.0
DIM2 = 160.0
TOP_CY = -HALF_WIDTH - 900.0
BACK_CX = -(HALF_WIDTH + DIM + 700.0)
TEXT_H = 42.0
MM_PER_INCH = 25.4


def _feet_inches(mm: float) -> str:
    inches = round(mm / MM_PER_INCH * 2.0) / 2.0
    feet = int(inches // 12)
    remainder = inches - feet * 12
    if remainder == int(remainder):
        return f"{feet}'-{int(remainder)}\""
    return f"{feet}'-{remainder:g}\""


def _dim_label(p1, p2) -> str:
    mm = hypot(p2[0] - p1[0], p2[1] - p1[1])
    return f"{_feet_inches(mm)}  ({mm:.1f} mm)"


def _dimstyle(doc: ezdxf.Drawing) -> str:
    if "BOAT" not in doc.dimstyles:
        style = doc.dimstyles.duplicate_entry("EZDXF", "BOAT")
        style.dxf.dimtxt = TEXT_H
        style.dxf.dimasz = 28.0
        style.dxf.dimexe = 16.0
        style.dxf.dimexo = 20.0
        style.dxf.dimgap = 10.0
        style.dxf.dimdec = 1
        style.dxf.dimzin = 8
        style.dxf.dimtix = 1
        style.dxf.dimtxsty = "Standard"
    return "BOAT"


def _linear(msp, dimstyle: str, p1, p2, base, angle: float = 0.0) -> None:
    dim = msp.add_linear_dim(
        base=base,
        p1=p1,
        p2=p2,
        angle=angle,
        dimstyle=dimstyle,
        dxfattribs={"layer": "DIMS"},
    )
    dim.set_text(_dim_label(p1, p2))
    dim.render()


def _bake_dimension_text(msp) -> None:
    """Explode DIMENSION entities and turn MTEXT into plain TEXT.

    LibreCAD and most DXF previews draw the dimension lines but skip the
    anonymous-block MTEXT ezdxf uses for the numbers.
    """
    for dim in list(msp.query("DIMENSION")):
        dim.explode()
    for mtext in list(msp.query("MTEXT")):
        rotation = float(mtext.dxf.rotation) if mtext.dxf.hasattr("rotation") else 0.0
        entity = msp.add_text(
            mtext.plain_text(),
            height=mtext.dxf.char_height,
            dxfattribs={
                "layer": mtext.dxf.layer,
                "style": "Standard",
                "rotation": rotation,
            },
        )
        entity.set_placement(
            (mtext.dxf.insert.x, mtext.dxf.insert.y),
            align=TextEntityAlignment.MIDDLE_CENTER,
        )
        msp.delete_entity(mtext)


def _note(msp, text: str, insert, height: float = TEXT_H, align=TextEntityAlignment.LEFT) -> None:
    entity = msp.add_text(text, height=height, dxfattribs={"layer": "NOTES"})
    entity.set_placement(insert, align=align)


def _offset_segment(
    p1: tuple[float, float], p2: tuple[float, float], dist: float, *, left: bool
) -> tuple[tuple[float, float], tuple[float, float]]:
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = hypot(dx, dy)
    ux, uy = dx / length, dy / length
    nx, ny = (-uy, ux) if left else (uy, -ux)
    return (p1[0] + nx * dist, p1[1] + ny * dist), (p2[0] + nx * dist, p2[1] + ny * dist)


def _intersect_lines(
    a1: tuple[float, float],
    a2: tuple[float, float],
    b1: tuple[float, float],
    b2: tuple[float, float],
) -> tuple[float, float]:
    x1, y1 = a1
    x2, y2 = a2
    x3, y3 = b1
    x4, y4 = b2
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-9:
        raise ValueError("hull offsets are parallel")
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def _add_short_arc(msp, mapper, center, radius, p_start, p_end, attribs: dict) -> None:
    c = mapper(*center)
    a0 = degrees(atan2(mapper(*p_start)[1] - c[1], mapper(*p_start)[0] - c[0])) % 360.0
    a1 = degrees(atan2(mapper(*p_end)[1] - c[1], mapper(*p_end)[0] - c[0])) % 360.0
    if (a1 - a0) % 360.0 > 180.0:
        a0, a1 = a1, a0
    msp.add_arc(c, radius, a0, a1, dxfattribs=attribs)


def _add_top_arc(msp, center, p_start, p_end, attribs: dict) -> None:
    _add_short_arc(msp, top_xy, center, TUBE_RADIUS, p_start, p_end, attribs)


def _stadium_along_x(msp, center, length: float, width: float, attribs: dict) -> None:
    cx, cy = center
    radius = width / 2.0
    half = length / 2.0 - radius
    if half <= 0:
        msp.add_circle(center, radius, dxfattribs=attribs)
        return
    msp.add_lwpolyline(
        [
            (cx - half, cy - radius, 0),
            (cx + half, cy - radius, 1),
            (cx + half, cy + radius, 0),
            (cx - half, cy + radius, 1),
        ],
        format="xyb",
        close=True,
        dxfattribs=attribs,
    )


def _d_ring(msp, center, pointing: str, attribs: dict) -> None:
    cx, cy = center
    outer = DRING_WIDTH / 2.0
    inner = outer - DRING_STOCK
    if pointing == "bow":
        msp.add_line((cx, cy - outer), (cx, cy + outer), dxfattribs=attribs)
        msp.add_arc(center, outer, -90.0, 90.0, dxfattribs=attribs)
        msp.add_arc(center, inner, -90.0, 90.0, dxfattribs=attribs)
    elif pointing == "up":
        msp.add_line((cx - outer, cy), (cx + outer, cy), dxfattribs=attribs)
        msp.add_arc(center, outer, 0.0, 180.0, dxfattribs=attribs)
        msp.add_arc(center, inner, 0.0, 180.0, dxfattribs=attribs)
    else:
        msp.add_line((cx - outer, cy), (cx + outer, cy), dxfattribs=attribs)
        msp.add_arc(center, outer, 180.0, 360.0, dxfattribs=attribs)
        msp.add_arc(center, inner, 180.0, 360.0, dxfattribs=attribs)


def top_xy(boat_x: float, boat_y: float) -> tuple[float, float]:
    """Top view: length along +X (bow right), beam along +Y (starboard up)."""
    return (boat_y, boat_x + TOP_CY)


def side_xy(boat_y: float, boat_z: float) -> tuple[float, float]:
    """Side view: length along +X (bow right), height along +Y."""
    return (boat_y, boat_z)


def back_xy(boat_x: float, boat_z: float) -> tuple[float, float]:
    """Back view: looking forward. Starboard to the right, height up, keel aligned."""
    return (BACK_CX + boat_x, boat_z)


def _external_tangents(
    first: tuple[float, float], second: tuple[float, float], radius: float
) -> tuple[tuple[tuple[float, float], tuple[float, float]], tuple[tuple[float, float], tuple[float, float]]]:
    dx = second[0] - first[0]
    dz = second[1] - first[1]
    length = hypot(dx, dz)
    ux, uz = dx / length, dz / length
    px, pz = -uz, ux
    if pz < 0:
        px, pz = -px, -pz
    upper = (
        (first[0] + px * radius, first[1] + pz * radius),
        (second[0] + px * radius, second[1] + pz * radius),
    )
    lower = (
        (first[0] - px * radius, first[1] - pz * radius),
        (second[0] - px * radius, second[1] - pz * radius),
    )
    return upper, lower


def _draw_side(msp, dimstyle: str) -> None:
    hull = {"layer": "HULL"}
    floor = {"layer": "FLOOR"}
    transom = {"layer": "TRANSOM"}
    center = {"layer": "CENTER", "linetype": "DASHED"}
    rise_start = (BOW_RISE_START_Y, TUBE_RADIUS)
    rise_end = (BOW_FRONT_Y, BOW_CENTER_Z)
    upper, lower = _external_tangents(rise_start, rise_end, TUBE_RADIUS)

    msp.add_arc(side_xy(TUBE_RADIUS, TUBE_RADIUS), TUBE_RADIUS, 90.0, 270.0, dxfattribs=hull)
    msp.add_line(side_xy(TUBE_RADIUS, 0.0), side_xy(BOW_RISE_START_Y, 0.0), dxfattribs=hull)
    msp.add_line(side_xy(TUBE_RADIUS, TUBE_DIAMETER), side_xy(BOW_RISE_START_Y, TUBE_DIAMETER), dxfattribs=hull)
    msp.add_line(side_xy(*upper[0]), side_xy(*upper[1]), dxfattribs=hull)
    msp.add_line(side_xy(*lower[0]), side_xy(*lower[1]), dxfattribs=hull)
    msp.add_arc(side_xy(BOW_FRONT_Y, BOW_CENTER_Z), TUBE_RADIUS, 270.0, 90.0, dxfattribs=hull)
    msp.add_line(side_xy(TUBE_RADIUS, TUBE_RADIUS), side_xy(BOW_RISE_START_Y, TUBE_RADIUS), dxfattribs=center)
    msp.add_line(side_xy(*rise_start), side_xy(*rise_end), dxfattribs=center)

    hardware = {"layer": "HARDWARE"}
    for handle_y in HANDLE_YS:
        _stadium_along_x(
            msp, side_xy(handle_y, TUBE_RADIUS), HANDLE_LENGTH, HANDLE_STOCK * 2.0, hardware
        )
    _d_ring(msp, side_xy(BOW_FRONT_Y, BOW_HEIGHT - TUBE_DIAMETER), "down", hardware)

    msp.add_lwpolyline(
        [
            side_xy(FLOOR_REAR_Y, 0.0),
            side_xy(FLOOR_FRONT_Y, 0.0),
            side_xy(FLOOR_FRONT_Y, FLOOR_THICKNESS),
            side_xy(FLOOR_REAR_Y, FLOOR_THICKNESS),
        ],
        close=True,
        dxfattribs=floor,
    )
    msp.add_lwpolyline(
        [
            side_xy(TRANSOM_Y0, 0.0),
            side_xy(TRANSOM_Y1, 0.0),
            side_xy(TRANSOM_Y1, TRANSOM_TOP),
            side_xy(TRANSOM_Y0, TRANSOM_TOP),
        ],
        close=True,
        dxfattribs=transom,
    )
    msp.add_line(
        side_xy(TRANSOM_Y0, MOTOR_WELL_Z),
        side_xy(TRANSOM_Y1, MOTOR_WELL_Z),
        dxfattribs=transom,
    )

    _linear(msp, dimstyle, side_xy(0.0, 0.0), side_xy(BOAT_LENGTH, 0.0), (BOAT_LENGTH / 2.0, -DIM))
    _linear(
        msp, dimstyle,
        side_xy(FLOOR_REAR_Y, FLOOR_THICKNESS), side_xy(FLOOR_FRONT_Y, FLOOR_THICKNESS),
        ((FLOOR_REAR_Y + FLOOR_FRONT_Y) / 2.0, -DIM2),
    )
    _linear(
        msp, dimstyle,
        side_xy(0.0, FLOOR_THICKNESS), side_xy(TRANSOM_Y, FLOOR_THICKNESS),
        (TRANSOM_Y / 2.0, FLOOR_THICKNESS + DIM2),
    )
    _linear(
        msp, dimstyle,
        side_xy(BOW_RISE_START_Y, BOW_HEIGHT), side_xy(BOW_FRONT_Y, BOW_HEIGHT),
        ((BOW_RISE_START_Y + BOW_FRONT_Y) / 2.0, BOW_HEIGHT + DIM2),
    )
    _linear(
        msp, dimstyle,
        side_xy(TUBE_RADIUS, 0.0), side_xy(TUBE_RADIUS, TUBE_DIAMETER),
        (-DIM2, TUBE_RADIUS),
        angle=90,
    )
    _linear(
        msp, dimstyle,
        side_xy(BOAT_LENGTH, 0.0), side_xy(BOAT_LENGTH, BOW_HEIGHT),
        (BOAT_LENGTH + DIM, BOW_HEIGHT / 2.0),
    )
    _linear(
        msp, dimstyle,
        side_xy(BOAT_LENGTH, BOW_CENTER_Z - TUBE_RADIUS),
        side_xy(BOAT_LENGTH, BOW_CENTER_Z + TUBE_RADIUS),
        (BOAT_LENGTH + DIM2, BOW_CENTER_Z),
    )
    _linear(
        msp, dimstyle,
        side_xy(TRANSOM_Y1, 0.0), side_xy(TRANSOM_Y1, TRANSOM_TOP),
        (TRANSOM_Y1 + DIM2, TRANSOM_HEIGHT / 2.0),
    )
    _linear(
        msp, dimstyle,
        side_xy(TRANSOM_Y1, MOTOR_WELL_Z), side_xy(TRANSOM_Y1, TRANSOM_TOP),
        (TRANSOM_Y1 + DIM2 + 80.0, MOTOR_WELL_Z + MOTOR_DROP / 2.0),
    )
    _linear(
        msp, dimstyle,
        side_xy(TRANSOM_Y0, TRANSOM_TOP), side_xy(TRANSOM_Y1, TRANSOM_TOP),
        ((TRANSOM_Y0 + TRANSOM_Y1) / 2.0, TRANSOM_TOP + DIM2),
    )

    _note(
        msp, "SIDE VIEW",
        (BOAT_LENGTH / 2.0, BOW_HEIGHT + DIM + 40.0),
        height=64.0,
        align=TextEntityAlignment.MIDDLE_CENTER,
    )
    _note(
        msp, "Bow right  |  whole bow rises over 3 ft to 2'-0\"  |  feet and mm",
        (BOAT_LENGTH / 2.0, BOW_HEIGHT + DIM - 30.0),
        height=28.0,
        align=TextEntityAlignment.MIDDLE_CENTER,
    )


def _draw_top(msp, dimstyle: str) -> None:
    hull = {"layer": "HULL"}
    floor = {"layer": "FLOOR"}
    transom = {"layer": "TRANSOM"}
    center = {"layer": "CENTER", "linetype": "DASHED"}

    def ty(boat_x: float, boat_y: float) -> tuple[float, float]:
        return top_xy(boat_x, boat_y)

    starboard_angle = ((TUBE_CENTER_X, BOW_ANGLE_START_Y), (BOW_CORNER_X, BOW_FRONT_Y))
    port_angle = ((-TUBE_CENTER_X, BOW_ANGLE_START_Y), (-BOW_CORNER_X, BOW_FRONT_Y))
    stbd_outer = _offset_segment(*starboard_angle, TUBE_RADIUS, left=False)
    stbd_inner = _offset_segment(*starboard_angle, TUBE_RADIUS, left=True)
    port_outer = _offset_segment(*port_angle, TUBE_RADIUS, left=True)
    port_inner = _offset_segment(*port_angle, TUBE_RADIUS, left=False)
    knuckle_stbd = (TUBE_CENTER_X, BOW_ANGLE_START_Y)
    knuckle_port = (-TUBE_CENTER_X, BOW_ANGLE_START_Y)
    corner_stbd = (BOW_CORNER_X, BOW_FRONT_Y)
    corner_port = (-BOW_CORNER_X, BOW_FRONT_Y)
    outer_front_stbd = (BOW_CORNER_X, BOAT_LENGTH)
    outer_front_port = (-BOW_CORNER_X, BOAT_LENGTH)
    inner_front = ((-HALF_WIDTH, FLOOR_FRONT_Y), (HALF_WIDTH, FLOOR_FRONT_Y))
    stbd_inner_knuckle = _intersect_lines(
        (HALF_CHANNEL, TUBE_RADIUS), (HALF_CHANNEL, BOW_FRONT_Y), *stbd_inner
    )
    port_inner_knuckle = _intersect_lines(
        (-HALF_CHANNEL, TUBE_RADIUS), (-HALF_CHANNEL, BOW_FRONT_Y), *port_inner
    )
    stbd_inner_bow = _intersect_lines(*stbd_inner, *inner_front)
    port_inner_bow = _intersect_lines(*port_inner, *inner_front)

    msp.add_line(ty(-HALF_WIDTH, TUBE_RADIUS), ty(-HALF_WIDTH, BOW_ANGLE_START_Y), dxfattribs=hull)
    msp.add_line(ty(HALF_WIDTH, TUBE_RADIUS), ty(HALF_WIDTH, BOW_ANGLE_START_Y), dxfattribs=hull)
    _add_top_arc(msp, knuckle_port, (-HALF_WIDTH, BOW_ANGLE_START_Y), port_outer[0], hull)
    _add_top_arc(msp, knuckle_stbd, (HALF_WIDTH, BOW_ANGLE_START_Y), stbd_outer[0], hull)
    msp.add_line(ty(*port_outer[0]), ty(*port_outer[1]), dxfattribs=hull)
    msp.add_line(ty(*stbd_outer[0]), ty(*stbd_outer[1]), dxfattribs=hull)
    _add_top_arc(msp, corner_port, port_outer[1], outer_front_port, hull)
    _add_top_arc(msp, corner_stbd, stbd_outer[1], outer_front_stbd, hull)
    msp.add_line(ty(*outer_front_port), ty(*outer_front_stbd), dxfattribs=hull)
    msp.add_line(ty(-HALF_CHANNEL, TUBE_RADIUS), ty(*port_inner_knuckle), dxfattribs=hull)
    msp.add_line(ty(HALF_CHANNEL, TUBE_RADIUS), ty(*stbd_inner_knuckle), dxfattribs=hull)
    msp.add_line(ty(*port_inner_knuckle), ty(*port_inner_bow), dxfattribs=hull)
    msp.add_line(ty(*stbd_inner_knuckle), ty(*stbd_inner_bow), dxfattribs=hull)
    msp.add_line(ty(*port_inner_bow), ty(*stbd_inner_bow), dxfattribs=hull)
    msp.add_arc(ty(-TUBE_CENTER_X, TUBE_RADIUS), TUBE_RADIUS, 90.0, 270.0, dxfattribs=hull)
    msp.add_arc(ty(TUBE_CENTER_X, TUBE_RADIUS), TUBE_RADIUS, 90.0, 270.0, dxfattribs=hull)

    msp.add_lwpolyline(
        [
            ty(-HALF_CHANNEL, FLOOR_REAR_Y),
            ty(HALF_CHANNEL, FLOOR_REAR_Y),
            ty(HALF_CHANNEL, BOW_ANGLE_START_Y),
            ty(BOW_CORNER_X, FLOOR_FRONT_Y),
            ty(-BOW_CORNER_X, FLOOR_FRONT_Y),
            ty(-HALF_CHANNEL, BOW_ANGLE_START_Y),
        ],
        close=True,
        dxfattribs=floor,
    )

    msp.add_lwpolyline(
        [
            ty(-TRANSOM_WIDTH / 2.0, TRANSOM_Y0),
            ty(TRANSOM_WIDTH / 2.0, TRANSOM_Y0),
            ty(TRANSOM_WIDTH / 2.0, TRANSOM_Y1),
            ty(-TRANSOM_WIDTH / 2.0, TRANSOM_Y1),
        ],
        close=True,
        dxfattribs=transom,
    )
    msp.add_lwpolyline(
        [
            ty(-MOTOR_WELL_TOP, TRANSOM_Y0),
            ty(MOTOR_WELL_TOP, TRANSOM_Y0),
            ty(MOTOR_WELL_TOP, TRANSOM_Y1),
            ty(-MOTOR_WELL_TOP, TRANSOM_Y1),
        ],
        close=True,
        dxfattribs=transom,
    )

    msp.add_line(ty(0.0, 0.0), ty(0.0, BOAT_LENGTH), dxfattribs=center)
    msp.add_line(ty(-TUBE_CENTER_X, TUBE_RADIUS), ty(-TUBE_CENTER_X, BOW_ANGLE_START_Y), dxfattribs=center)
    msp.add_line(ty(TUBE_CENTER_X, TUBE_RADIUS), ty(TUBE_CENTER_X, BOW_ANGLE_START_Y), dxfattribs=center)
    msp.add_line(ty(-TUBE_CENTER_X, BOW_ANGLE_START_Y), ty(-BOW_CORNER_X, BOW_FRONT_Y), dxfattribs=center)
    msp.add_line(ty(TUBE_CENTER_X, BOW_ANGLE_START_Y), ty(BOW_CORNER_X, BOW_FRONT_Y), dxfattribs=center)
    msp.add_line(ty(-BOW_CORNER_X, BOW_FRONT_Y), ty(BOW_CORNER_X, BOW_FRONT_Y), dxfattribs=center)

    hardware = {"layer": "HARDWARE"}
    for handle_y in HANDLE_YS:
        for side in (-1.0, 1.0):
            _stadium_along_x(
                msp,
                ty(side * (HALF_WIDTH + HANDLE_STANDOFF / 2.0), handle_y),
                HANDLE_LENGTH,
                HANDLE_STANDOFF,
                hardware,
            )
    _d_ring(msp, ty(0.0, BOW_FRONT_Y), "bow", hardware)
    _note(
        msp, "D-RING UNDER",
        (BOW_FRONT_Y + DRING_WIDTH + 80.0, TOP_CY),
        height=28.0,
        align=TextEntityAlignment.MIDDLE_CENTER,
    )

    mid_y = TOP_CY
    _linear(msp, dimstyle, ty(0.0, 0.0), ty(0.0, BOAT_LENGTH), (BOAT_LENGTH / 2.0, mid_y - HALF_WIDTH - DIM))
    _linear(
        msp, dimstyle,
        ty(-HALF_WIDTH, TUBE_RADIUS), ty(HALF_WIDTH, TUBE_RADIUS),
        (-DIM, mid_y),
        angle=90,
    )
    _linear(
        msp, dimstyle,
        ty(-TUBE_CENTER_X, TUBE_RADIUS), ty(TUBE_CENTER_X, TUBE_RADIUS),
        (-DIM2, mid_y),
        angle=90,
    )
    _linear(
        msp, dimstyle,
        ty(-HALF_CHANNEL, FLOOR_REAR_Y), ty(HALF_CHANNEL, FLOOR_REAR_Y),
        (FLOOR_REAR_Y + DIM2, mid_y),
        angle=90,
    )
    _linear(
        msp, dimstyle,
        ty(TUBE_CENTER_X - TUBE_RADIUS, BOAT_LENGTH * 0.45),
        ty(TUBE_CENTER_X + TUBE_RADIUS, BOAT_LENGTH * 0.45),
        (BOAT_LENGTH * 0.45, TOP_CY + TUBE_CENTER_X + DIM2),
        angle=90,
    )
    _linear(
        msp, dimstyle,
        ty(-TRANSOM_WIDTH / 2.0, TRANSOM_Y0), ty(TRANSOM_WIDTH / 2.0, TRANSOM_Y0),
        (TRANSOM_Y0 - 70.0, mid_y),
        angle=90,
    )
    _linear(
        msp, dimstyle,
        ty(0.0, TRANSOM_Y0), ty(0.0, TRANSOM_Y1),
        ((TRANSOM_Y0 + TRANSOM_Y1) / 2.0, mid_y - HALF_CHANNEL - 80.0),
    )
    _linear(
        msp, dimstyle,
        ty(-TUBE_CENTER_X, 0.0), ty(-TUBE_CENTER_X, TRANSOM_Y),
        (TRANSOM_Y / 2.0, mid_y - HALF_WIDTH - DIM2),
    )
    _linear(
        msp, dimstyle,
        ty(-BOW_CORNER_X, BOAT_LENGTH), ty(BOW_CORNER_X, BOAT_LENGTH),
        (BOAT_LENGTH + DIM2, mid_y),
        angle=90,
    )

    _note(
        msp, "TOP VIEW",
        (BOAT_LENGTH / 2.0, mid_y - HALF_WIDTH - DIM - 110.0),
        height=64.0,
        align=TextEntityAlignment.MIDDLE_CENTER,
    )
    _note(
        msp, "Bow right  |  starboard up  |  feet and mm",
        (BOAT_LENGTH / 2.0, mid_y - HALF_WIDTH - DIM - 175.0),
        height=28.0,
        align=TextEntityAlignment.MIDDLE_CENTER,
    )


def _draw_back(msp, dimstyle: str) -> None:
    hull = {"layer": "HULL"}
    floor = {"layer": "FLOOR"}
    transom = {"layer": "TRANSOM"}
    center = {"layer": "CENTER", "linetype": "DASHED"}

    msp.add_circle(back_xy(-TUBE_CENTER_X, TUBE_RADIUS), TUBE_RADIUS, dxfattribs=hull)
    msp.add_circle(back_xy(TUBE_CENTER_X, TUBE_RADIUS), TUBE_RADIUS, dxfattribs=hull)
    msp.add_lwpolyline(
        [
            back_xy(-HALF_CHANNEL, 0.0),
            back_xy(HALF_CHANNEL, 0.0),
            back_xy(HALF_CHANNEL, FLOOR_THICKNESS),
            back_xy(-HALF_CHANNEL, FLOOR_THICKNESS),
        ],
        close=True,
        dxfattribs=floor,
    )
    msp.add_line(
        back_xy(-TUBE_CENTER_X, TRANSOM_TOP),
        back_xy(-MOTOR_WELL_TOP, TRANSOM_TOP),
        dxfattribs=transom,
    )
    msp.add_line(
        back_xy(-MOTOR_WELL_TOP, TRANSOM_TOP),
        back_xy(-MOTOR_FLAT / 2.0, MOTOR_WELL_Z),
        dxfattribs=transom,
    )
    msp.add_line(
        back_xy(-MOTOR_FLAT / 2.0, MOTOR_WELL_Z),
        back_xy(MOTOR_FLAT / 2.0, MOTOR_WELL_Z),
        dxfattribs=transom,
    )
    msp.add_line(
        back_xy(MOTOR_FLAT / 2.0, MOTOR_WELL_Z),
        back_xy(MOTOR_WELL_TOP, TRANSOM_TOP),
        dxfattribs=transom,
    )
    msp.add_line(
        back_xy(MOTOR_WELL_TOP, TRANSOM_TOP),
        back_xy(TUBE_CENTER_X, TRANSOM_TOP),
        dxfattribs=transom,
    )
    msp.add_arc(
        back_xy(TUBE_CENTER_X, TUBE_RADIUS), TUBE_RADIUS, 90.0, 270.0, dxfattribs=transom
    )
    msp.add_line(
        back_xy(TUBE_CENTER_X, 0.0),
        back_xy(-TUBE_CENTER_X, 0.0),
        dxfattribs=transom,
    )
    msp.add_arc(
        back_xy(-TUBE_CENTER_X, TUBE_RADIUS), TUBE_RADIUS, 270.0, 90.0, dxfattribs=transom
    )
    _stadium_along_x(
        msp, back_xy(0.0, BOW_CENTER_Z), BOW_FLAT + TUBE_DIAMETER, TUBE_DIAMETER, center
    )
    msp.add_line(back_xy(0.0, 0.0), back_xy(0.0, BOW_HEIGHT), dxfattribs=center)
    for side in (-1.0, 1.0):
        msp.add_line(
            back_xy(side * TUBE_CENTER_X, TUBE_DIAMETER),
            back_xy(side * TUBE_CENTER_X, KNUCKLE_TOP_Z),
            dxfattribs=center,
        )
        msp.add_line(
            back_xy(side * TUBE_CENTER_X, KNUCKLE_TOP_Z),
            back_xy(side * BOW_CORNER_X, BOW_HEIGHT),
            dxfattribs=center,
        )
    msp.add_line(
        back_xy(-BOW_CORNER_X, BOW_HEIGHT),
        back_xy(BOW_CORNER_X, BOW_HEIGHT),
        dxfattribs=center,
    )
    _d_ring(msp, back_xy(0.0, BOW_HEIGHT - TUBE_DIAMETER), "down", {"layer": "HARDWARE"})

    _linear(
        msp, dimstyle,
        back_xy(-HALF_WIDTH, 0.0), back_xy(HALF_WIDTH, 0.0),
        (BACK_CX, -DIM),
    )
    _linear(
        msp, dimstyle,
        back_xy(-TUBE_CENTER_X, TRANSOM_TOP), back_xy(TUBE_CENTER_X, TRANSOM_TOP),
        (BACK_CX, TRANSOM_TOP + DIM2),
    )
    _linear(
        msp, dimstyle,
        back_xy(-HALF_CHANNEL, FLOOR_THICKNESS), back_xy(HALF_CHANNEL, FLOOR_THICKNESS),
        (BACK_CX, FLOOR_THICKNESS + 80.0),
    )
    _linear(
        msp, dimstyle,
        back_xy(-HALF_WIDTH, 0.0), back_xy(-HALF_WIDTH, TUBE_DIAMETER),
        (BACK_CX - HALF_WIDTH - DIM2, TUBE_RADIUS),
        angle=90,
    )
    _linear(
        msp, dimstyle,
        back_xy(HALF_WIDTH, 0.0), back_xy(HALF_WIDTH, BOW_HEIGHT),
        (BACK_CX + HALF_WIDTH + DIM, BOW_HEIGHT / 2.0),
        angle=90,
    )
    _linear(
        msp, dimstyle,
        back_xy(0.0, 0.0), back_xy(0.0, MOTOR_WELL_Z),
        (BACK_CX + 80.0, MOTOR_WELL_Z / 2.0),
        angle=90,
    )
    _linear(
        msp, dimstyle,
        back_xy(-MOTOR_FLAT / 2.0, MOTOR_WELL_Z),
        back_xy(MOTOR_FLAT / 2.0, MOTOR_WELL_Z),
        (BACK_CX, MOTOR_WELL_Z - 70.0),
    )
    _linear(
        msp, dimstyle,
        back_xy(MOTOR_FLAT / 2.0, MOTOR_WELL_Z),
        back_xy(MOTOR_FLAT / 2.0, TRANSOM_TOP),
        (BACK_CX + MOTOR_WELL_TOP + 50.0, MOTOR_WELL_Z + MOTOR_DROP / 2.0),
        angle=90,
    )
    _note(
        msp, "30°",
        back_xy(-(MOTOR_FLAT / 2.0 + MOTOR_WELL_TOP) / 2.0, MOTOR_WELL_Z + MOTOR_DROP * 0.55),
        height=28.0,
        align=TextEntityAlignment.MIDDLE_CENTER,
    )
    _note(
        msp, "30°",
        back_xy((MOTOR_FLAT / 2.0 + MOTOR_WELL_TOP) / 2.0, MOTOR_WELL_Z + MOTOR_DROP * 0.55),
        height=28.0,
        align=TextEntityAlignment.MIDDLE_CENTER,
    )
    _linear(
        msp, dimstyle,
        back_xy(-HALF_CHANNEL, 0.0), back_xy(-HALF_CHANNEL, FLOOR_THICKNESS),
        (BACK_CX - HALF_CHANNEL - 80.0, FLOOR_THICKNESS / 2.0),
        angle=90,
    )

    _note(
        msp, "BACK VIEW",
        (BACK_CX, BOW_HEIGHT + DIM + 40.0),
        height=64.0,
        align=TextEntityAlignment.MIDDLE_CENTER,
    )
    _note(
        msp, "Looking forward  |  starboard right  |  dashed = bow",
        (BACK_CX, BOW_HEIGHT + DIM - 30.0),
        height=28.0,
        align=TextEntityAlignment.MIDDLE_CENTER,
    )


def _title_block(msp) -> None:
    x = 0.0
    y = BOW_HEIGHT + DIM + 160.0
    _note(msp, "BEN'S BEST BOAT", (x, y + 80.0), height=72.0)
    _note(msp, "Top, side, and back views  |  full size  |  feet and millimetres", (x, y + 20.0), height=32.0)
    _note(
        msp,
        "14'-0\" L  x  6'-0\" W  x  1'-6\" tubes  |  2'-0\" bow over 3'-0\"  |  transom 2'-0\" in",
        (x, y - 30.0),
        height=28.0,
    )
    _note(
        msp,
        "Form reference only. Not a construction, pressure, buoyancy, or motor-rating drawing.",
        (x, y - 75.0),
        height=24.0,
    )


def build() -> None:
    doc = ezdxf.new("R2000", setup=True)
    doc.units = units.MM
    doc.header["$INSUNITS"] = units.MM
    doc.header["$MEASUREMENT"] = 1
    doc.header["$LTSCALE"] = 40.0

    doc.layers.add("HULL", color=7)
    doc.layers.add("FLOOR", color=4)
    doc.layers.add("TRANSOM", color=6)
    doc.layers.add("HARDWARE", color=1)
    doc.layers.add("CENTER", color=8)
    doc.layers.add("DIMS", color=3)
    doc.layers.add("NOTES", color=2)

    msp = doc.modelspace()
    dimstyle = _dimstyle(doc)
    _draw_side(msp, dimstyle)
    _draw_top(msp, dimstyle)
    _draw_back(msp, dimstyle)
    _title_block(msp)
    _bake_dimension_text(msp)
    doc.saveas(OUT)


if __name__ == "__main__":
    build()
    print(OUT.resolve())
