// Based on things/3d_template/scad/flat_plate.scad. Dimensions in mm.
render_fn = 96;
$fn = render_fn;
set = "chess_board"; // [chess_board, drawer, assembly, interference]
revision_string = "dev";

square_size = 20;
border_width = 5;
board_thickness = 4;
groove_width = 1;
groove_depth = 1;
engraving_depth = 0.4;
boolean_overlap = 0.1;

// Drawer height includes its floor. Clearances are per side, in mm.
drawer_height = 27.5;
wall_thickness = 3;
drawer_wall = 2.4;
drawer_floor = 2.4;
slide_clearance = 0.4;
top_clearance = 0.6;
guide_width = 3;
front_thickness = 6;
top_ramp_width = 3;
// 7 mm base diameter gives the rear snap a broad, positive engagement.
detent_base_radius = 3.5;
detent_depth = 1.2;
detent_dimple_depth = 1.4;
detent_back_offset = 8;
// Assembly-only opening distance; zero is flush/closed.
drawer_open = 0;

board_size = 8 * square_size + 2 * border_width;
playing_origin = -4 * square_size;

assert(square_size > 0 && border_width >= 5);
assert(board_thickness > groove_depth + engraving_depth);
assert(groove_width > 0 && groove_width < square_size);
assert(groove_depth > 0 && groove_depth < board_thickness);
assert(engraving_depth > 0);

housing_inner = board_size - 2 * wall_thickness;
drawer_width = housing_inner - 2 * slide_clearance;
drawer_length = board_size - wall_thickness - slide_clearance;
drawer_y_center = -board_size / 2 + drawer_length / 2;
drawer_bottom = -top_clearance - drawer_height;
rail_bottom = drawer_bottom - slide_clearance;
housing_height = -rail_bottom;
// The cone extends this far beyond the drawer's ordinary sliding plane.
detent_interference = detent_depth - slide_clearance;

assert(slide_clearance > 0 && top_clearance > 0);
assert(drawer_height > guide_width + drawer_floor);
assert(drawer_floor > 0 && drawer_wall > 0 && wall_thickness > 0);
assert(drawer_length > front_thickness + drawer_wall);
assert(top_ramp_width > 0 && top_ramp_width <= wall_thickness);
assert(detent_base_radius > detent_dimple_depth && detent_dimple_depth > detent_depth);
assert(detent_interference > 0,
       "detent must extend beyond the normal drawer side clearance");

detent_y = board_size / 2 - wall_thickness - detent_back_offset;
detent_z = drawer_bottom + drawer_height / 2;

module chess_board_positive() {
    // Model coordinates: centered XY, playing face at board_thickness.
    translate([-board_size / 2, -board_size / 2, 0])
        cube([board_size, board_size, board_thickness]);
}

// Rectangular cutter along Y. It extends above the face for a clean,
// exact-width opening and leaves a 1 mm-deep flat bottom.
module groove(length) {
    translate([-groove_width / 2, -length / 2, board_thickness - groove_depth])
        cube([groove_width, length, groove_depth + boolean_overlap]);
}

module chess_board_negative() {
    // Seven internal dividers plus the playing-area perimeter.
    // Square size is the pitch; flat interiors are pitch minus groove width.
    for (i = [0:8]) {
        translate([playing_origin + i * square_size, 0, 0])
            groove(8 * square_size + groove_width);
        rotate([0, 0, 90])
            translate([playing_origin + i * square_size, 0, 0])
                groove(8 * square_size + groove_width);
    }

    // Center the back engraving; it faces upward during printing, clear of the bed.
    translate([0, 0, engraving_depth])
        rotate([180, 0, 0])
            linear_extrude(height = engraving_depth + boolean_overlap)
                text(revision_string, size = 5.5, halign = "center",
                     valign = "center");
}

module chess_board() {
    difference() {
        chess_board_positive();
        chess_board_negative();
    }
}

// Extrude an XZ profile along Y; coordinates remain in the assembly frame.
module along_y(points, length, y_center = 0) {
    translate([0, y_center, 0])
        rotate([90, 0, 0])
            linear_extrude(height = length, center = true) polygon(points);
}

// Extrude a YZ profile along X; coordinates remain in the assembly frame.
module along_x(points, length, x_center = 0, y_center = 0) {
    translate([x_center, y_center, 0])
        // Map the 2D profile's X/Y axes to assembly Y/Z, then extrude on X.
        multmatrix([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
            linear_extrude(height = length, center = true) polygon(points);
}

// A horizontal 45-degree conical frustum. The base fuses to the wall and the
// smaller end faces the drawer, so every overhang grows no faster than 45°.
module detent_cone(side, depth) {
    rotate([0, -side * 90, 0])
        cylinder(h = depth, r1 = detent_base_radius,
                 r2 = detent_base_radius - depth);
}

// The drawer recess is slightly deeper than the housing cone for a firm,
// rear-only snap fit while avoiding unsupported spherical overhangs.
module housing_detent(side) {
    translate([side * housing_inner / 2, detent_y, detent_z])
        detent_cone(side, detent_depth);
}

module drawer_detent_dimple(side) {
    // Start outside the side face and extend through it, preventing
    // coplanar cutter faces from causing preview Z-fighting.
    translate([side * (drawer_width / 2 + boolean_overlap),
               detent_y, drawer_height / 2])
        rotate([0, -side * 90, 0])
            cylinder(h = detent_dimple_depth + boolean_overlap,
                     r1 = detent_base_radius + boolean_overlap,
                     r2 = detent_base_radius - detent_dimple_depth);
}

module housing() {
    union() {
        chess_board();
        // Two sides and a back stop, open below and at the front (-Y).
        for (side = [-1, 1])
            translate([side * (board_size - wall_thickness) / 2,
                       0, -housing_height / 2])
                cube([wall_thickness, board_size, housing_height], center = true);
        translate([0, (board_size - wall_thickness) / 2, -housing_height / 2])
            cube([board_size, wall_thickness, housing_height], center = true);
        // Rails grow inward at 45 degrees when the housing is printed upside down.
        // Matching bevels on the drawer ride on these slopes.
        for (side = [-1, 1])
            scale([side, 1, 1])
                along_y([
                    [housing_inner / 2 + boolean_overlap, rail_bottom],
                    [housing_inner / 2 - guide_width - slide_clearance, rail_bottom],
                    [housing_inner / 2 + boolean_overlap,
                     rail_bottom + guide_width + slide_clearance + boolean_overlap]
                ], board_size);
        // Top ramps guide the drawer's matching upper bevels and retain it
        // around the two sides and back without closing the front opening.
        for (side = [-1, 1])
            scale([side, 1, 1])
                along_y([
                    [housing_inner / 2, 0],
                    [housing_inner / 2 - top_ramp_width, 0],
                    [housing_inner / 2, -top_ramp_width]
                ], board_size);
        along_x([
            [housing_inner / 2, 0],
            [housing_inner / 2 - top_ramp_width, 0],
            [housing_inner / 2, -top_ramp_width]
        ], housing_inner, 0);
        for (side = [-1, 1]) housing_detent(side);
    }
}

// Drawer coordinates: bottom Z=0, front Y=-board_size/2.
module drawer() {
    difference() {
        translate([-drawer_width / 2, -board_size / 2, 0])
            cube([drawer_width, drawer_length, drawer_height]);
        translate([-drawer_width / 2 + drawer_wall,
                   -board_size / 2 + front_thickness, drawer_floor])
            cube([drawer_width - 2 * drawer_wall,
                  drawer_length - front_thickness - drawer_wall,
                  drawer_height + boolean_overlap]);
        // Chamfer both bottom edges: outward growth is 45 degrees on the bed.
        for (side = [-1, 1])
            scale([side, 1, 1])
                along_y([
                    [drawer_width / 2 - guide_width, -boolean_overlap],
                    [drawer_width / 2 + boolean_overlap, -boolean_overlap],
                    [drawer_width / 2 + boolean_overlap, guide_width + boolean_overlap],
                    [drawer_width / 2, guide_width],
                    [drawer_width / 2 - guide_width, 0]
                ], board_size + 2 * boolean_overlap);
        // Matching top bevels clear the housing ramps at 45 degrees.
        for (side = [-1, 1])
            scale([side, 1, 1])
                along_y([
                    [drawer_width / 2 - top_ramp_width - boolean_overlap,
                     drawer_height + boolean_overlap],
                    [drawer_width / 2 + boolean_overlap,
                     drawer_height - top_ramp_width],
                    [drawer_width / 2 + boolean_overlap,
                     drawer_height + boolean_overlap]
                ], drawer_length + 2 * boolean_overlap, drawer_y_center);
        along_x([
            [drawer_length / 2 - top_ramp_width - boolean_overlap,
             drawer_height + boolean_overlap],
            [drawer_length / 2 + boolean_overlap,
             drawer_height - top_ramp_width],
            [drawer_length / 2 + boolean_overlap,
             drawer_height + boolean_overlap]
        ], drawer_width + 2 * boolean_overlap, 0, drawer_y_center);
        for (side = [-1, 1]) drawer_detent_dimple(side);
        // Engrave the revision in the drawer bottom, clear of its sliding faces.
        translate([0, 0, -boolean_overlap])
            linear_extrude(height = engraving_depth + boolean_overlap)
                text(revision_string, size = 5.5, halign = "center", valign = "center");
    }
}

module chess_board_assembly() {
    color("burlywood") housing();
    translate([0, -drawer_open, drawer_bottom]) color("sienna") drawer();
}

// Non-printable fit diagnostic: a correct closed fit has no rendered solid.
module interference() {
    intersection() {
        housing();
        translate([0, 0, drawer_bottom]) drawer();
    }
}

if (set == "chess_board") {
    // Playing face on the bed; walls and rails grow upward.
    translate([0, 0, board_thickness]) rotate([180, 0, 0]) housing();
} else if (set == "drawer") {
    drawer();
} else if (set == "assembly") {
    chess_board_assembly();
} else if (set == "interference") {
    interference();
} else {
    assert(false, str("Unknown set: ", set));
}
