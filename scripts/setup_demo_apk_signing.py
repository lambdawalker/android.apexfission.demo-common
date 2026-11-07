#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "android-repo-setup @ git+https://github.com/lambdawalker/python.android-repo-setup.git@b3294108af351fd5ee8a7743fa641b2fc6143617",
# ]
# ///
"""Launch the shared signing wizard with Demo Common's existing vault location."""

import argparse
from hashlib import sha256
from pathlib import Path

from android_repo_setup import SetupConfig, SetupError, run_wizard


REPOSITORY = "lambdawalker/android.apexfission.demo-common"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=REPOSITORY, help="GitHub repository in owner/name form")
    args = parser.parse_args()
    repository_id = sha256(args.repo.casefold().encode()).hexdigest()[:16]
    vault_path = Path.home() / ".demo-common-signing" / f"setup-{repository_id}.vault"
    try:
        return run_wizard(SetupConfig(repository=args.repo, vault_path=vault_path, key_alias="demo-common"))
    except ValueError as error:
        parser.error(str(error))
    except SetupError as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
