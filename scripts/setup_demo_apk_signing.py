#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx==0.28.1",
#     "PyNaCl==1.6.2",
#     "textual==8.2.8",
# ]
# ///
"""Provision the Demo Common APK signing environment from a trusted terminal."""

import argparse
import asyncio
from base64 import b64encode
from contextlib import AsyncExitStack
from hashlib import sha256
import json
import os
import re
from pathlib import Path
import secrets
import shutil
import string
import subprocess
import sys
import tempfile

from github_environment_api import GitHubAPI, SetupError
from signing_setup_ui import SigningSetupApp


REPOSITORY = "lambdawalker/android.apexfission.demo-common"
ENVIRONMENT = "demo-apk-release"
DEFAULT_ALIAS = "demo-common"
DEFAULT_KEYSTORE = Path.home() / ".demo-common-signing" / "demo-common.jks"
SECRET_NAMES = (
    "ANDROID_KEYSTORE_PASSWORD",
    "ANDROID_KEY_ALIAS",
    "ANDROID_KEY_PASSWORD",
    "ANDROID_KEYSTORE_BASE64",
)
SYMBOLS = "!@#$%^&*()-_=+[]{}:,.?"
BRANCH_POLICY = {"protected_branches": False, "custom_branch_policies": True}


def generate_password():
    groups = (string.ascii_lowercase, string.ascii_uppercase, string.digits, SYMBOLS)
    alphabet = "".join(groups)
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(25))
        if all(any(char in group for char in password) for group in groups):
            return password


async def read_password(ui, label, *, allow_generate):
    prompt = " [Enter to generate]" if allow_generate else ""
    while True:
        value = await ui.prompt(f"{label}{prompt}", secret=True)
        if not value and allow_generate:
            return generate_password(), True
        if len(value) < 6 or any(ord(char) < 32 or ord(char) == 127 for char in value):
            ui.note("Enter at least six characters without control characters.")
        elif value == await ui.prompt(f"Confirm {label.lower()}", secret=True):
            return value, False
        else:
            ui.note("Passwords differ. Try again.")


def run_keytool(keytool, operation, path, alias, store_password, key_password, extra=()):
    env = dict(os.environ, DEMO_KEYTOOL_STORE_PASSWORD=store_password,
               DEMO_KEYTOOL_KEY_PASSWORD=key_password)
    # Env modifiers keep passwords out of command arguments and process listings.
    command = [
        keytool, operation, "-keystore", str(path), "-storetype", "JKS",
        "-alias", alias, "-storepass:env", "DEMO_KEYTOOL_STORE_PASSWORD",
        "-keypass:env", "DEMO_KEYTOOL_KEY_PASSWORD", *extra,
    ]
    result = subprocess.run(
        command, env=env, stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    )
    if result.returncode:
        raise SetupError("keytool failed. Check the JDK, keystore, alias, and passwords.")


def prepare_keystore(keytool, path, alias, store_password, key_password, *, reuse):
    if reuse:
        # A certificate request proves both passwords unlock the private key.
        run_keytool(keytool, "-certreq", path, alias, store_password, key_password)
        return
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".signing-", dir=path.parent) as directory:
        temporary = Path(directory) / "signing.jks"
        run_keytool(
            keytool, "-genkeypair", temporary, alias, store_password, key_password,
            ("-keyalg", "RSA", "-keysize", "3072", "-validity", "10950",
             "-dname", "CN=Demo Common APK Signing", "-noprompt"),
        )
        os.chmod(temporary, 0o600)
        # Install the completed keystore without replacing an existing key.
        os.link(temporary, path)


async def inspect_environment(api):
    path = api.environment_path(ENVIRONMENT)
    environment = await api.request("GET", path, allow_missing=True)
    if environment is None:
        return None, set()
    return environment, set(await api.list_values(ENVIRONMENT, "secrets"))


async def ensure_main_only(api, environment):
    path = api.environment_path(ENVIRONMENT)
    if environment is None:
        await api.request("PUT", path, json={"deployment_branch_policy": BRANCH_POLICY})
    elif environment.get("deployment_branch_policy") != BRANCH_POLICY:
        raise SetupError(f"Configure {ENVIRONMENT} to allow only the main branch in GitHub Settings.")

    policies = await api.request("GET", f"{path}/deployment-branch-policies", params={"per_page": 100})
    entries = policies.get("branch_policies", [])
    if not entries and not policies.get("total_count", 0):
        await api.request("POST", f"{path}/deployment-branch-policies",
                          json={"name": "main", "type": "branch"})
    elif (policies.get("total_count") != 1 or len(entries) != 1
          or entries[0].get("name") != "main" or entries[0].get("type") != "branch"):
        raise SetupError(f"Existing rules for {ENVIRONMENT} must allow only the main branch.")


OPERATIONS = {
    "1": ("key",),
    "2": ("github",),
    "3": ("key", "github"),
}
LABELS = {"key": "signing keystore", "github": "GitHub environment"}


def state_path(repository):
    repository_id = sha256(repository.casefold().encode()).hexdigest()[:16]
    return DEFAULT_KEYSTORE.parent / f"setup-{repository_id}.json"


def save_state(path, state):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".setup-", dir=path.parent) as directory:
        temporary = Path(directory) / "state.json"
        temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        os.chmod(temporary, 0o600)
        temporary.replace(path)


def load_state(path):
    if not path.exists():
        return {"pending": [], "complete": []}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(state, dict):
            raise ValueError
        for field in ("pending", "complete"):
            if not isinstance(state[field], list) or any(step not in LABELS for step in state[field]):
                raise ValueError
        for field in ("keystore", "alias"):
            if field in state and not isinstance(state[field], str):
                raise ValueError
        return state
    except (KeyError, ValueError, TypeError):
        raise SetupError("The setup record is invalid. Move it aside and run setup again.") from None


def default_operation(state):
    pending = set(state["pending"])
    complete = set(state["complete"])
    steps = pending or (set(LABELS) - complete)
    return next((choice for choice, operations in OPERATIONS.items() if set(operations) == steps), "q")


async def select_operations(ui, record, state):
    while True:
        if state["pending"]:
            ui.note("Incomplete steps: " + ", ".join(LABELS[step] for step in state["pending"]))
        choices = [
            ("Create or verify the signing keystore", "1"),
            ("Set up GitHub using an existing keystore", "2"),
            ("Both operations", "3"),
            ("Exit", "q"),
        ]
        if record.exists():
            choices.insert(-1, ("Reset local setup progress", "r"))
        choice = await ui.prompt("Choose setup operations", options=(choices, default_operation(state)))
        if choice == "q":
            return (), state
        if choice in OPERATIONS:
            return OPERATIONS[choice], state
        if await ui.prompt("Type RESET to clear local progress. Keystore and GitHub secrets are preserved.") == "RESET":
            record.unlink()
            state = load_state(record)


async def choose_keystore(ui, state):
    default_path = state.get("keystore", DEFAULT_KEYSTORE)
    raw_path = (await ui.prompt(f"Keystore path (default {default_path})")).strip()
    path = Path(raw_path or default_path).expanduser().absolute()
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise SetupError("Choose a regular file path for the keystore.")
    path = path.resolve()
    if path.is_relative_to(Path(__file__).resolve().parents[1]):
        raise SetupError("Keep the keystore outside this repository checkout.")
    default_alias = state.get("alias", DEFAULT_ALIAS)
    alias = (await ui.prompt(f"Signing key alias (default {default_alias})")).strip() or default_alias
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", alias):
        raise SetupError("Use a key alias with 1–64 letters, digits, dots, underscores or hyphens.")
    return path, alias


async def confirm_password_backup(ui, generated):
    if not generated:
        return True
    if await ui.prompt("In a private terminal, type SHOW to reveal the generated passwords.") != "SHOW":
        return False
    ui.show_passwords(generated)
    try:
        return await ui.prompt("Save these in your password manager, then type SAVED.") == "SAVED"
    finally:
        ui.show_passwords([])


async def upload_secrets(ui, api, environment, existing, missing, path, alias, store_password, key_password):
    values = (store_password, alias, key_password, b64encode(path.read_bytes()).decode("ascii"))
    if any(len(value.encode("utf-8")) > 48 * 1024 for value in values):
        raise SetupError("A signing secret exceeds GitHub's 48 KiB limit.")
    current, current_secrets = await inspect_environment(api)
    if current != environment or current_secrets != existing:
        raise SetupError("The environment changed during setup. Rerun to review its current state.")
    await ensure_main_only(api, current)
    for name, value in zip(SECRET_NAMES, values):
        if name in missing:
            if name in await api.list_values(ENVIRONMENT, "secrets"):
                raise SetupError("A signing secret was added concurrently. Rerun to review the state.")
            await api.write_secret(ENVIRONMENT, name, value)
            ui.note(f"Uploaded {name}.")
    ui.note("APK signing environment prepared.")


async def setup(ui, repository, keytool):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise SetupError("Repository must be owner/name.")
    record = state_path(repository)
    operations, state = await select_operations(ui, record, load_state(record))
    if not operations:
        return

    def mark_complete(step):
        if step in state["pending"]:
            state["pending"].remove(step)
        if step not in state["complete"]:
            state["complete"].append(step)
        save_state(record, state)

    state["pending"] = list(dict.fromkeys([*state["pending"], *operations]))
    state["complete"] = [step for step in state["complete"] if step not in operations]
    save_state(record, state)
    async with AsyncExitStack() as stack:
        missing = []
        if "github" in operations:
            token = (await ui.prompt("GitHub token", secret=True)).strip()
            if not token:
                raise SetupError("A GitHub token is required.")
            api = await stack.enter_async_context(GitHubAPI(repository, token))
            del token
            environment, existing = await inspect_environment(api)
            missing = [name for name in SECRET_NAMES if name not in existing]
            if not missing:
                ui.note("All APK signing secrets already exist. Existing values were preserved.")
                if operations == OPERATIONS["2"]:
                    mark_complete("github")
                    return

        path, alias = await choose_keystore(ui, state)
        reuse = path.is_file()
        if not reuse and "key" not in operations:
            raise SetupError("GitHub-only setup requires an existing keystore. Choose Both to create one.")
        if "github" in operations and existing.intersection(SECRET_NAMES):
            if not reuse:
                raise SetupError("GitHub already has signing secrets. Use the original keystore.")
            if missing and await ui.prompt(
                "Partial upload found. Type RESUME to confirm this is the original keystore and alias: "
            ) != "RESUME":
                raise SetupError("To resume, use the original keystore, alias, and passwords.")

        store_password, new_store_password = await read_password(ui, "Keystore password", allow_generate=not reuse)
        key_password, new_key_password = await read_password(ui, "Key password", allow_generate=not reuse)
        ui.note(f"Repository {repository}\nKeystore {path}")
        ui.note("Reuse existing keystore." if reuse else "Create a new keystore.")
        if missing:
            ui.note(f"Environment {ENVIRONMENT} (main only)\nUpload missing secrets: " + ", ".join(missing))
        if await ui.prompt("Review the changes above, then type APPLY.") != "APPLY":
            ui.note("Cancelled.")
            return

        generated = [(name, value) for name, value, created in (
            ("Keystore password", store_password, new_store_password),
            ("Key password", key_password, new_key_password),
        ) if created]
        if not await confirm_password_backup(ui, generated):
            ui.note("Cancelled.")
            return

        state.update(keystore=str(path), alias=alias)
        save_state(record, state)
        await asyncio.to_thread(prepare_keystore, keytool, path, alias, store_password, key_password, reuse=reuse)
        ui.note(f"Keystore ready at {path}. Keep an offline backup.")
        mark_complete("key")
        if missing:
            await upload_secrets(ui, api, environment, existing, missing, path, alias, store_password, key_password)
        if "github" in operations:
            mark_complete("github")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=REPOSITORY, help="GitHub repository in owner/name form")
    args = parser.parse_args()
    if not sys.stdin.isatty() or not sys.stdout.isatty() or not sys.stderr.isatty():
        parser.exit(1, "Run this script in an interactive terminal without redirection.\n")
    keytool = shutil.which("keytool")
    if not keytool:
        parser.exit(1, "Install a JDK and add keytool to PATH.\n")
    async def run(ui):
        try:
            await setup(ui, args.repo, keytool)
        except (SetupError, OSError) as error:
            ui.note(str(error) if isinstance(error, SetupError) else
                    "Could not access the keystore or run keytool. Check path and permissions.")
            ui.note("Rerun the wizard to retry unfinished steps.")
            await ui.prompt("Press Enter to close.")
            ui.exit(return_code=1)
        else:
            if ui.messages:
                await ui.prompt("Press Enter to close.")
            ui.exit()

    app = SigningSetupApp(run)
    app.run()
    return app.return_code


if __name__ == "__main__":
    sys.exit(main())
