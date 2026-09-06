# `infaltable_boat`

Parametric exterior/form model of a U-shaped inflatable catamaran. The
requested identifier intentionally retains the spelling `infaltable_boat`.

| Dimension | Full size | Default 1:24 model |
|---|---:|---:|
| Overall length | 168 in / 4267.2 mm | 7 in / 177.8 mm |
| Overall width | 63 in / 1600.2 mm | 2.625 in / 66.675 mm |
| Tube diameter | 18 in / 457.2 mm | 0.75 in / 19.05 mm |
| Clear channel | 27 in / 685.8 mm | 1.125 in / 28.575 mm |
| Floor thickness | 6 in / 152.4 mm | 0.25 in / 6.35 mm |

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
