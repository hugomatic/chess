render_fn = 96;
$fn = render_fn;
set = "__CLAW_MODEL__"; // [__CLAW_MODEL__, assembly]

part_w = 100;
part_d = 60;
part_h = 4;
boolean_overlap = 0.1;

module __CLAW_MODEL___positive() {
    cube([part_w, part_d, part_h], center = true);
}

module __CLAW_MODEL___negative() {
    echo("BOM", "M3x16 screw", 1);
    cylinder(d = 3.4, h = part_h + 2 * boolean_overlap, center = true);
}

module __CLAW_MODEL__() {
    difference() {
        __CLAW_MODEL___positive();
        __CLAW_MODEL___negative();
    }
}

if (set == "__CLAW_MODEL__") {
    __CLAW_MODEL__();
} else if (set == "assembly") {
    __CLAW_MODEL__();
}
