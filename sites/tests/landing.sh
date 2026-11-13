#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
android-repo-docs build --check
node --test sites/tests/*.test.mjs
