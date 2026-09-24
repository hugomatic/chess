render_fn = 48;
$fn = render_fn;
set = "scale_hull"; // [scale_hull, scale_floor, scale_transom, assembly, full_size_assembly]
revision_string = "dev";

boat_length = 4267.2;       // 168 in
overall_width = 1828.8;     // 72 in / 6 ft (3 ft floor plus two 18 in tubes)
tube_diameter = 457.2;      // 18 in
floor_thickness = 152.4;    // 6 in
bow_height = 609.6;         // 24 in overall height at the raised bow
bow_rise_length = 914.4;    // 36 in / 3 ft longitudinal upslope
model_scale = 0.0416666667; // 1:24
transom_width = 1371.6;     // 54 in; tube-center to tube-center
transom_height = 457.2;     // 18 in; flush with the tubes in z
transom_thickness = 38.1;   // 1.5 in
transom_inset = 609.6;      // 2 ft forward of stern tube-center
transom_motor_drop = 152.4; // 6 in motor well
transom_motor_angle = 30;   // degrees from vertical, each side
transom_motor_flat = 304.8; // 12 in flat where the motor sits
print_flat = 0.6;           // scaled-model bed-contact trim
engraving_depth = 6;
engraving_size = 75;
boolean_overlap = 0.1;
bow_flat = 304.8;           // 12 in front tube centerline
handle_length = 203.2;      // 8 in webbing loop, two per side
handle_stock = 12.7;        // 0.5 in
handle_standoff = 38.1;     // 1.5 in above the tube
d_ring_width = 50.8;        // 2 in metal D-ring under the front tube
d_ring_stock = 8;

tube_radius = tube_diameter / 2;
tube_center_x = overall_width / 2 - tube_radius;
channel_width = overall_width - 2 * tube_diameter;
bow_front_y = boat_length - tube_radius;
bow_angle_start_y = bow_front_y - tube_center_x;
bow_corner_x = bow_flat / 2;
bow_rise_end_y = bow_front_y;
bow_rise_start_y = bow_rise_end_y - bow_rise_length;
transom_y = tube_radius + transom_inset;
floor_rear_y = transom_y;
floor_front_y = bow_front_y - tube_radius;
handle_run = bow_angle_start_y - transom_y;
handle_aft_y = transom_y + handle_run / 6;
handle_fwd_y = transom_y + 5 * handle_run / 6;

assert(boat_length > overall_width && overall_width > 2 * tube_diameter);
assert(tube_center_x > tube_radius, "Merged bow must leave a positive inner radius");
assert(bow_flat > 0 && bow_flat < 2 * tube_center_x);
assert(floor_thickness > 0 && floor_thickness < tube_diameter);
assert(bow_height >= tube_diameter);
assert(bow_rise_length > 0 && bow_rise_start_y > transom_y);
assert(transom_inset >= 0 && floor_rear_y < bow_rise_start_y);
assert(abs(channel_width - 914.4) < 0.001,
       "Tube and width values must retain the 3 ft channel");
assert(transom_width > channel_width && transom_width <= overall_width);
assert(abs(transom_width - 2 * tube_center_x) < 0.001,
       "Transom spans the tube centers so its sides can wrap the tubes");
assert(abs(transom_height - tube_diameter) < 0.001,
       "Transom is flush with the tubes in z");
assert(transom_thickness > engraving_depth);
assert(model_scale > 0 && model_scale <= 1);
assert(print_flat >= 0 && print_flat < tube_radius * model_scale);
assert(handle_length > 0 && handle_standoff > 0 && handle_stock > 0);
assert(d_ring_width > 2 * d_ring_stock && d_ring_stock > 0);
assert(handle_aft_y > transom_y && handle_fwd_y < bow_angle_start_y);
assert(transom_motor_drop > 0 && transom_motor_drop < transom_height);
assert(transom_motor_angle > 0 && transom_motor_angle < 90);
assert(transom_motor_flat > 0
       && transom_motor_flat + 2 * transom_motor_drop * tan(transom_motor_angle)
          < channel_width);

function tube_center_z(y) =
    y <= bow_rise_start_y
    ? tube_radius
    : tube_radius + (y - bow_rise_start_y) / bow_rise_length
        * (bow_height - tube_diameter);

module tube_sphere(point) {
    translate(point) sphere(r = tube_radius);
}

module tube_segment(first, second) {
    hull() {
        tube_sphere(first);
        tube_sphere(second);
    }
}

module inflatable_hull() {
    union() {
        for (side = [-1, 1]) {
            tube_segment(
                [side * tube_center_x, tube_radius, tube_radius],
                [side * tube_center_x, bow_rise_start_y, tube_radius]
            );
            tube_segment(
                [side * tube_center_x, bow_rise_start_y, tube_radius],
                [side * tube_center_x, bow_angle_start_y, tube_center_z(bow_angle_start_y)]
            );
            tube_segment(
                [side * tube_center_x, bow_angle_start_y, tube_center_z(bow_angle_start_y)],
                [side * bow_corner_x, bow_front_y, tube_center_z(bow_front_y)]
            );
        }
        tube_segment(
            [-bow_corner_x, bow_front_y, tube_center_z(bow_front_y)],
            [bow_corner_x, bow_front_y, tube_center_z(bow_front_y)]
        );
    }
}

module drop_stitch_floor() {
    linear_extrude(height = floor_thickness)
        polygon([
            [-channel_width / 2, floor_rear_y],
            [-channel_width / 2, bow_angle_start_y],
            [-bow_corner_x, floor_front_y],
            [bow_corner_x, floor_front_y],
            [channel_width / 2, bow_angle_start_y],
            [channel_width / 2, floor_rear_y]
        ]);
}

module transom_part() {
    well_flat = transom_motor_flat / 2;
    well_flare = transom_motor_drop * tan(transom_motor_angle);
    well_z = transom_height - transom_motor_drop;
    difference() {
        translate([-transom_width / 2, 0, 0])
            cube([transom_width, transom_thickness, transom_height]);
        for (side = [-1, 1])
            translate([side * tube_center_x, -boolean_overlap, tube_radius])
                rotate([-90, 0, 0])
                    cylinder(
                        h = transom_thickness + 2 * boolean_overlap,
                        r = tube_radius
                    );
        translate([0, transom_thickness + boolean_overlap, 0])
            rotate([90, 0, 0])
                linear_extrude(height = transom_thickness + 2 * boolean_overlap)
                    polygon([
                        [-well_flat, well_z],
                        [well_flat, well_z],
                        [well_flat + well_flare, transom_height + boolean_overlap],
                        [-well_flat - well_flare, transom_height + boolean_overlap]
                    ]);
        translate([0, transom_thickness + boolean_overlap, well_z * 0.5])
            rotate([90, 0, 0])
                linear_extrude(height = engraving_depth + boolean_overlap)
                    text(revision_string, size = engraving_size,
                         halign = "center", valign = "center");
    }
}

module side_handle() {
    half = handle_length / 2;
    for (s = [-1, 1])
        translate([0, s * half, 0])
            cylinder(h = handle_standoff, r = handle_stock / 2);
    translate([0, 0, handle_standoff])
        rotate([90, 0, 0])
            cylinder(h = handle_length, r = handle_stock / 2, center = true);
}

module metal_d_ring() {
    major = d_ring_width / 2;
    minor = d_ring_stock / 2;
    difference() {
        rotate_extrude()
            translate([major, 0]) circle(r = minor);
        translate([-major * 2, -major * 4, -minor * 2])
            cube([major * 4, major * 4, minor * 4]);
    }
    rotate([0, 90, 0])
        cylinder(h = d_ring_width, r = minor, center = true);
}

module deck_hardware() {
    for (side = [-1, 1])
        for (y = [handle_aft_y, handle_fwd_y])
            translate([side * (tube_center_x + tube_radius), y, tube_center_z(y)])
                rotate([0, side * 90, 0])
                    side_handle();
    translate([0, bow_rise_end_y, bow_height - tube_diameter - d_ring_stock / 2])
        rotate([-90, 0, 0])
            metal_d_ring();
}

module full_size_assembly() {
    color("firebrick") inflatable_hull();
    color("lightgray") drop_stitch_floor();
    translate([0, transom_y - transom_thickness / 2, 0])
        color("saddlebrown") transom_part();
    color("silver") deck_hardware();
}

module printable_hull() {
    intersection() {
        translate([0, 0, -print_flat])
            scale([model_scale, model_scale, model_scale]) inflatable_hull();
        translate([-overall_width, -boat_length, 0])
            cube([2 * overall_width, 2 * boat_length, bow_height]);
    }
}

module printable_floor() {
    translate([0, -floor_rear_y * model_scale, 0])
        scale([model_scale, model_scale, model_scale]) drop_stitch_floor();
}

module printable_transom() {
    translate([0, transom_height * model_scale, 0])
        rotate([90, 0, 0])
            scale([model_scale, model_scale, model_scale]) transom_part();
}

if (set == "scale_hull") {
    printable_hull();
} else if (set == "scale_floor") {
    printable_floor();
} else if (set == "scale_transom") {
    printable_transom();
} else if (set == "assembly") {
    scale([model_scale, model_scale, model_scale]) full_size_assembly();
} else if (set == "full_size_assembly") {
    full_size_assembly();
} else {
    assert(false, str("Unknown set: ", set));
}
