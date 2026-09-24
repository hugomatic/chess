# Chess

Parametric OpenSCAD chess board with the Foil Claw / Plamp CAD generator.

```bash
uv sync
uv run chess cad --help
```

Explore and verify the catalog:

```bash
uv run chess cad systems --json
uv run chess cad models --system chess --json
uv run chess cad sets chess_board --system chess --json
uv run chess cad validate chess_board --system chess --json
uv run chess cad plan --system chess --product board --json
```

Generate the printable board into the managed archive:

```bash
uv run chess cad generate --system chess --product board \
  --revision my-test --json
```

Generated STL files, manifests, source snapshots, and logs live beneath the
ignored `data/cad/runs/` directory.
