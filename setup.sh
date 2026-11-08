#!/bin/sh
set -eu

if ! command -v uv >/dev/null 2>&1; then
    echo "Install uv and add it to PATH." >&2
    exit 1
fi
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec uv run "$project_dir/scripts/setup.py" "$@"
