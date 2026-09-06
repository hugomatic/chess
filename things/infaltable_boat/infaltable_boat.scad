render_fn = 48;
$fn = render_fn;
set = "scale_hull"; // [scale_hull, scale_floor, scale_transom, assembly, full_size_assembly]
revision_string = "dev";

boat_length = 4267.2;       // 168 in
overall_width = 1600.2;     // 63 in
tube_diameter = 457.2;      // 18 in
floor_thickness = 152.4;    // 6 in
model_scale = 0.0416666667; // 1:24
transom_width = 685.8;      // 27 in
transom_height = 381;       // 15 in; form parameter, not a motor rating
transom_thickness = 38.1;   // 1.5 in
transom_y = 228.6;          // stern tube-center station
print_flat = 0.6;           // scaled-model bed-contact trim
engraving_depth = 6;
engraving_size = 75;
bow_segments = 32;
boolean_overlap = 0.1;

tube_radius = tube_diameter / 2;
tube_center_x = overall_width / 2 - tube_radius;
bow_path_radius = tube_center_x;
bow_center_y = boat_length - tube_radius - bow_path_radius;
inner_bow_radius = bow_path_radius - tube_radius;
channel_width = overall_width - 2 * tube_diameter;
floor_rear_y = tube_radius;
floor_front_y = bow_center_y + inner_bow_radius;

assert(boat_length > overall_width && overall_width > 2 * tube_diameter);
assert(tube_center_x > tube_radius, "Merged bow must leave a positive inner radius");
assert(floor_thickness > 0 && floor_thickness < tube_diameter);
assert(abs(channel_width - 685.8) < 0.001,
       "Tube and width values must retain the 27 in channel");
assert(transom_width > 0 && transom_width <= channel_width);
assert(transom_height > 0 && transom_thickness > engraving_depth);
assert(model_scale > 0 && model_scale <= 1);
assert(print_flat >= 0 && print_flat < tube_radius * model_scale);
assert(bow_segments >= 8);

function bow_point(index) = [
    bow_path_radius * cos(index * 180 / bow_segments),
    bow_center_y + bow_path_radius * sin(index * 180 / bow_segments)
];

module tube_sphere(point) {
    translate([point[0], point[1], tube_radius]) sphere(r = tube_radius);
}

module tube_segment(first, second) {
    hull() {
        tube_sphere(first);
        tube_sphere(second);
    }
}

module inflatable_hull() {
    union() {
        tube_segment([tube_center_x, tube_radius], [tube_center_x, bow_center_y]);
        tube_segment([-tube_center_x, tube_radius], [-tube_center_x, bow_center_y]);
        for (index = [0:bow_segments - 1])
            tube_segment(bow_point(index), bow_point(index + 1));
    }
}

module drop_stitch_floor() {
    linear_extrude(height = floor_thickness)
        union() {
            translate([-channel_width / 2, floor_rear_y])
                square([channel_width, bow_center_y - floor_rear_y]);
            translate([0, bow_center_y]) circle(r = inner_bow_radius);
        }
}

module transom_part() {
    difference() {
        translate([-transom_width / 2, 0, 0])
            cube([transom_width, transom_thickness, transom_height]);
        translate([0, transom_thickness + boolean_overlap, transom_height * 0.58])
            rotate([90, 0, 0])
                linear_extrude(height = engraving_depth + boolean_overlap)
                    text(revision_string, size = engraving_size,
                         halign = "center", valign = "center");
    }
}

module full_size_assembly() {
    color("firebrick") inflatable_hull();
    color("lightgray") drop_stitch_floor();
    translate([0, transom_y - transom_thickness / 2, floor_thickness])
        color("saddlebrown") transom_part();
}

module printable_hull() {
    intersection() {
        translate([0, 0, -print_flat])
            scale([model_scale, model_scale, model_scale]) inflatable_hull();
        translate([-overall_width, -boat_length, 0])
            cube([2 * overall_width, 2 * boat_length, tube_diameter]);
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
