# Ben's best boat

Parametric exterior/form model of a U-shaped inflatable catamaran. The
Chess CAD identifier remains `infaltable_boat`.

| Dimension | Full size | Default 1:24 model |
|---|---:|---:|
| Overall length | 168 in / 4267.2 mm | 7 in / 177.8 mm |
| Overall width | 72 in / 1828.8 mm | 3 in / 76.2 mm |
| Tube diameter | 18 in / 457.2 mm | 0.75 in / 19.05 mm |
| Clear channel | 36 in / 914.4 mm | 1.5 in / 38.1 mm |
| Floor thickness | 6 in / 152.4 mm | 0.25 in / 6.35 mm |
| Bow front tube (flat) | 12 in / 304.8 mm | 0.5 in / 12.7 mm |
| Bow rise length | 36 in / 914.4 mm | 1.5 in / 38.1 mm |
| Transom inset from stern tube-center | 24 in / 609.6 mm | 1 in / 25.4 mm |
| Transom width (tube-center to tube-center) | 54 in / 1371.6 mm | 2.25 in / 57.15 mm |
| Transom height (flush with tubes) | 18 in / 457.2 mm | 0.75 in / 19.05 mm |
| Motor well drop | 6 in / 152.4 mm | 0.25 in / 6.35 mm |
| Motor well flat | 12 in / 304.8 mm | 0.5 in / 12.7 mm |
| Motor well side angle | 30° from vertical | 30° |

The tubes stay level from the stern, then the entire bow rises in one slope over the last 3 ft, to 24 in overall height at the stem. The bow is three parts: two angled tubes and a 12 in flat front. The transom sits 2'-9" from the stern tip, spanning the tube centers, with sides rounded to the 18 in tubes and flush with them in z. A 6 in motor well is cut into the top center, with a 12 in flat and 30° sides. The floor starts at that station. Two webbing handles sit on the outer side of each tube, spaced along the parallel run, and a metal D-ring hangs under the front tube for a mooring line.

The `infaltable_boat` product generates three separate printable artifacts:
`scale_hull`, `scale_floor`, and `scale_transom`. `assembly` and
`full_size_assembly` are reference views only.

```bash
uv run chess cad validate infaltable_boat --system chess --json
uv run chess cad plan --system chess --product infaltable_boat --json
uv run chess cad generate --system chess --product infaltable_boat --json
```

Override form parameters with repeatable definitions, for example:

```bash
uv run chess cad plan --system chess --product infaltable_boat \
  --define model_scale=0.05 --define transom_height=406.4 --json
```

This CAD captures nominal dimensions and exterior form only. It does not
provide structural design, pressure boundaries, seam patterns, buoyancy or
stability calculations, motor-rating certification, or fabrication approval.
