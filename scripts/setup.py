#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["android-repo-setup @ git+https://github.com/lambdawalker/python.android-repo-setup.git@v0.1.14"]
# ///
"""Thin launcher for the shared repository setup commands."""
from pathlib import Path
import sys
from android_repo_setup.cli import main
sys.argv[1:1] = ["--project", str(Path(__file__).resolve().parents[1])]
raise SystemExit(main())
