#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "android-repo-setup @ git+https://github.com/lambdawalker/python.android-repo-setup.git@v0.1.3",
# ]
# ///
"""Launch the shared signing wizard with Demo Common's project secrets directory."""

import argparse

from android_repo_setup import SetupConfig, SetupError, run_wizard


REPOSITORY = "lambdawalker/android.apexfission.demo-common"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=REPOSITORY, help="GitHub repository in owner/name form")
    args = parser.parse_args()
    try:
        return run_wizard(SetupConfig(repository=args.repo, key_alias="demo-common"))
    except ValueError as error:
        parser.error(str(error))
    except SetupError as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
