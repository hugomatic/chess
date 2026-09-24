"""Command-line entry point for Chess CAD."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from collections.abc import Mapping
from typing import Any, Callable, TextIO

from chess.cad_cli import add_cad_parser, run_cad_command
from chess.cad_generation import generate_plan, list_runs, load_job_log, load_run
from chess.context import resolve_context


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chess",
        description="Parametric CAD tools for the chess project.",
    )
    add_cad_parser(parser.add_subparsers(dest="command", required=True))
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    env: Mapping[str, str] | None = None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    cad_generate_func: Callable[..., Any] = generate_plan,
    cad_list_runs_func: Callable[..., Any] = list_runs,
    cad_load_run_func: Callable[..., Any] = load_run,
    cad_load_log_func: Callable[..., Any] = load_job_log,
) -> int:
    args = build_parser().parse_args(argv)
    values = os.environ if env is None else env
    return run_cad_command(
        args,
        resolve_context(values),
        sys.stdin if stdin is None else stdin,
        sys.stdout if stdout is None else stdout,
        sys.stderr if stderr is None else stderr,
        {
            "generate": cad_generate_func,
            "list_runs": cad_list_runs_func,
            "load_run": cad_load_run_func,
            "load_job_log": cad_load_log_func,
        },
    )
