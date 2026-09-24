# Chess board

Derived from `../3d_template/scad/flat_plate.scad`, retaining its
positive/negative modules, set selector, and companion CAD metadata.

Open `chess_board.scad` in OpenSCAD. `chess_board` exports the board and housing,
`drawer` exports the separate drawer, and `assembly` shows them together. Dimensions are in millimetres.

Defaults: 20 mm squares, 5 mm border, 4 mm thickness, 170 mm overall width.
Change `square_size`, `border_width`, and `board_thickness` to suit your
pieces and printer. Allow additional bed space for any brim.

All 64 squares share one flat playing surface. The grid and its perimeter
use 1 mm-wide, flat-bottom grooves (`groove_width`) that are 1 mm deep
(`groove_depth`). `square_size` is the grid pitch; the default flat square
interior is 19 mm wide. Colour contrast requires painting or a slicer colour
workflow.

The `chess_board` set places the playing face down at Z=0 for printing;
`assembly` shows the board face up. The grooves have vertical sides and a
flat base; check that a 1 mm-wide channel resolves at your chosen nozzle
diameter and layer height.
`revision_string` is engraved at the center of the back, facing upward during
printing. Its text size defaults to 5.5 mm.

To export with the CAD generator:

```bash
uv run chess cad generate --system chess --product board --json
```

Direct OpenSCAD export:

```bash
openscad -o /tmp/chess_board.stl things/chess_board/chess_board.scad
```

## Drawer and housing

The housing has two side walls and a back stop, with no floor. Both side
walls carry continuous 45-degree bottom guides, while 45-degree top ramps
continue around the two sides and back. Matching drawer bevels guide the
drawer into its closed position. Rear-only 45-degree conical side detents
provide a firm snap fit; their deeper drawer dimples engage only at the end
of travel, so normal sliding is largely unaffected. The front closes flush with the
housing; `drawer_open` moves it outward in the assembly view.

The drawer is 27.5 mm tall overall, including its 2.4 mm bottom, leaving
25.1 mm internal height. Default outside dimensions are 219.2 mm wide by
222.6 mm long. Its 6 mm front is unbroken; `revision_string` is engraved
shallowly in the drawer bottom.

Print `chess_board` face-down and `drawer` bottom-down, separately. Housing
rails and drawer bevels grow at 45 degrees in these orientations; the
housing has no floor to bridge. Inspect the slicer preview for the flat
grooves, top ramp bevels, and snap-detent overhangs before a full print.

`slide_clearance` defaults to 0.4 mm per side and `top_clearance` to 0.6 mm.
Print a short rail/bevel and detent fit coupon before committing to both
large parts. The detent uses a 7 mm diameter base; `detent_depth` controls
its 0.8 mm protrusion beyond normal side clearance and can be reduced for a
softer material or a printer with tight clearances. Allow for first-layer
expansion.

Render the non-printable `interference` set with a closed drawer to check the
Boolean intersection before printing. It should be empty; any resulting solid
marks an unintended housing/drawer collision.

```bash
openscad -D 'set="drawer"' -o /tmp/chess_board_drawer.stl things/chess_board/chess_board.scad
openscad -D 'set="assembly"' -D 'drawer_open=80' -o /tmp/chess_board_assembly.stl things/chess_board/chess_board.scad
```
