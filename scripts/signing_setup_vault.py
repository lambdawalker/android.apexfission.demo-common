"""Password-protected local state for the APK signing wizard."""

from base64 import b64decode, b64encode
import json
import os
from pathlib import Path
import tempfile

from nacl.exceptions import CryptoError
from nacl.pwhash import argon2id
from nacl.secret import SecretBox
from nacl.utils import random

from github_environment_api import SetupError


def validate_state(state):
    if not isinstance(state, dict):
        raise ValueError("Invalid setup state")
    for field in ("pending", "complete"):
        values = state.get(field)
        if not isinstance(values, list) or any(value not in ("key", "github") for value in values):
            raise ValueError("Invalid setup progress")
    for field in ("keystore", "alias", "github_token"):
        if field in state and not isinstance(state[field], str):
            raise ValueError("Invalid saved answer")
    if "signing_passwords" in state:
        passwords = state["signing_passwords"]
        if not isinstance(passwords, dict) or set(passwords) != {"keystore", "alias", "store", "key"}:
            raise ValueError("Invalid saved signing identity")
        if any(not isinstance(value, str) for value in passwords.values()):
            raise ValueError("Invalid saved signing password")


class SetupVault:
    def __init__(self, path, salt, box, state):
        self.path = path
        self.salt = salt
        self.box = box
        self.state = state

    @classmethod
    def unlock(cls, path, password, *, initial=None):
        try:
            if path.is_symlink() or (path.exists() and (not path.is_file() or path.stat().st_size > 1024 * 1024)):
                raise ValueError
            envelope = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
            salt = random(argon2id.SALTBYTES)
            if envelope is not None:
                if not isinstance(envelope, dict) or envelope["version"] != 1:
                    raise ValueError
                salt = b64decode(envelope["salt"], validate=True)
            key = argon2id.kdf(SecretBox.KEY_SIZE, password.encode("utf-8"), salt,
                               opslimit=argon2id.OPSLIMIT_INTERACTIVE,
                               memlimit=argon2id.MEMLIMIT_INTERACTIVE)
            box = SecretBox(key)
            state = initial if envelope is None else json.loads(
                box.decrypt(b64decode(envelope["ciphertext"], validate=True))
            )
            validate_state(state)
            return cls(path, salt, box, state)
        except (CryptoError, KeyError, TypeError, ValueError, RuntimeError):
            raise SetupError("Could not unlock the setup vault. Check the password or restore your backup.") from None

    def save(self):
        validate_state(self.state)
        if self.path.is_symlink():
            raise SetupError("The vault path must be a regular file.")
        envelope = {
            "version": 1,
            "salt": b64encode(self.salt).decode("ascii"),
            "ciphertext": b64encode(self.box.encrypt(json.dumps(self.state).encode("utf-8"))).decode("ascii"),
        }
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".vault-", dir=self.path.parent) as directory:
            temporary = Path(directory) / "vault"
            temporary.write_text(json.dumps(envelope) + "\n", encoding="utf-8")
            os.chmod(temporary, 0o600)
            with temporary.open("rb") as stream:
                os.fsync(stream.fileno())
            temporary.replace(self.path)
