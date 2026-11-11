#!/bin/sh
set -eu
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
reference=$(sed -n "s/^tooling_ref: ['\"]*\([^'\"]*\)['\"]*$/\1/p" "$project_dir/.project/setup/config.yaml")
if printf '%s\n' "$reference" | grep -Eq '^v[0-9]+\.[0-9]+\.[0-9]+$'; then
    expected_version="android-repo-setup ${reference#v}"
    if ! command -v android-repo-setup >/dev/null 2>&1; then
        echo "Install $expected_version from the tooling releases and add it to PATH." >&2
        exit 1
    fi
    actual_version=$(android-repo-setup --version)
    if [ "$actual_version" != "$expected_version" ]; then
        echo "Expected $expected_version. Found $actual_version." >&2
        exit 1
    fi
    executable=android-repo-setup
elif printf '%s\n' "$reference" | grep -Eq '^[0-9a-f]{40}$'; then
    destination="$project_dir/bin/$reference"
    executable="$destination/bin/android-repo-setup"
    if [ ! -x "$executable" ]; then
        cargo install --locked --root "$destination" --git https://github.com/lambdawalker/gradle.android-repo-setup.git --rev "$reference" android-repo-setup
    fi
else
    echo 'Invalid tooling_ref in .project/setup/config.yaml' >&2
    exit 1
fi
exec "$executable" --project "$project_dir" "$@"
