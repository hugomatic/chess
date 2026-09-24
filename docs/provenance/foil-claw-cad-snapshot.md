# Foil Claw CAD snapshot provenance

Chess CAD tooling began as a source snapshot from the local Foil Claw
repository at:

- Source: `/home/hugo/code/foil-claw`
- Commit: `5d1b23b11dfd7f6f13c1fb529cc69ddd63cdb656`
- Snapshot date: 2026-09-05

Copied modules include `cad_fs`, `cad_values`, `cad_manufacturing`, `cad_model`,
`cad_profiles`, `cad_dependencies`, `cad_system`, `cad_planning`, `cad_readme`,
`cad_generation`, `cad_scaffold`, and `cad_cli`. Their corresponding unit tests
and the generic `things/3d_template` templates are copied as behavioral and
format compatibility checks.

Intentional adaptations are limited to:

- Python namespace `foil_claw` to `chess`.
- Console command `claw cad` to `chess cad`.
- Environment variables to `CHESS_ROOT` and `CHESS_DATA_DIR`.
- Product-facing labels and repository defaults to the chess board catalog.

The existing `plamp-cad-model/1`, `plamp-cad-system/1`, and related schema
identifiers are intentionally retained so this snapshot remains compatible
with the proven documents and tests. The scaffold token `__CLAW_MODEL__` is
also retained. The copied code is now owned by this repository and is not
automatically synchronized with Foil Claw.
