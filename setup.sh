#!/usr/bin/env bash

_chess_remove_path_entry() {
  local target="$1"
  local part
  local rebuilt=""
  local -a parts

  IFS=: read -r -a parts <<< "${PATH:-}"
  for part in "${parts[@]}"; do
    [[ "$part" == "$target" ]] && continue
    if [[ -z "$rebuilt" ]]; then
      rebuilt="$part"
    else
      rebuilt="${rebuilt}:$part"
    fi
  done
  PATH="$rebuilt"
}

_chess_setup_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
_chess_old_root="${CHESS_ROOT:-}"

if [[ -n "$_chess_old_root" ]]; then
  _chess_remove_path_entry "$_chess_old_root/.venv/bin"
  _chess_remove_path_entry "$_chess_old_root"
fi

_chess_remove_path_entry "$_chess_setup_dir/.venv/bin"
_chess_remove_path_entry "$_chess_setup_dir"

export CHESS_ROOT="$_chess_setup_dir"
if [[ -n "${1:-}" ]]; then
  case "$1" in
    /*) export CHESS_DATA_DIR="$1" ;;
    *) export CHESS_DATA_DIR="$(realpath -m -- "$PWD/$1")" ;;
  esac
else
  export CHESS_DATA_DIR="$CHESS_ROOT/data"
fi
export PATH="$CHESS_ROOT/.venv/bin:$CHESS_ROOT:$PATH"
hash -r

printf 'CHESS_ROOT=%s\n' "$CHESS_ROOT"
printf 'CHESS_DATA_DIR=%s\n' "$CHESS_DATA_DIR"

unset _chess_setup_dir _chess_old_root
unset -f _chess_remove_path_entry
