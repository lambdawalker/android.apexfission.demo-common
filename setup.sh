#!/bin/sh
set -eu

if ! command -v android-repo-setup >/dev/null 2>&1; then
    echo "Install android-repo-setup v0.1.6 from the tooling releases and add it to PATH." >&2
    exit 1
fi
expected_version="android-repo-setup 0.1.6"
actual_version=$(android-repo-setup --version)
if [ "$actual_version" != "$expected_version" ]; then
    echo "Expected $expected_version. Found $actual_version. Install the pinned release before running setup." >&2
    exit 1
fi
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec android-repo-setup --project "$project_dir" "$@"
