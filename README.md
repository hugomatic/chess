# Chess

Parametric OpenSCAD chess board with the Foil Claw / Plamp CAD generator.

```bash
uv sync
source ./setup.sh
chess cad --help
```

Explore and verify the catalog:

```bash
chess cad systems --json
chess cad models --system chess --json
chess cad sets chess_board --system chess --json
chess cad validate chess_board --system chess --json
chess cad plan --system chess --product board --json
```

Generate both printable parts—the board housing and drawer—in one managed run:

```bash
chess cad generate --system chess --product board --json
```

Generated STL files, manifests, source snapshots, and logs live beneath the
ignored `data/cad/runs/` directory.

`setup.sh [DATA_DIR]` selects this checkout for the current shell, exports
`CHESS_ROOT` and `CHESS_DATA_DIR`, and adds the checkout's `.venv/bin` to
`PATH`. Run `uv sync` first; without an argument, data defaults to
`$CHESS_ROOT/data`.
