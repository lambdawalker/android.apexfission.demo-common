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


class SetupVault:
    def __init__(self, path, salt, box, state):
        self.path = path
        self.salt = salt
        self.box = box
        self.state = state

    @classmethod
    def unlock(cls, path, password, *, initial=None):
        try:
            envelope = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
            salt = random(argon2id.SALTBYTES)
            if envelope is not None:
                if envelope["version"] != 1:
                    raise ValueError
                salt = b64decode(envelope["salt"], validate=True)
            key = argon2id.kdf(SecretBox.KEY_SIZE, password.encode("utf-8"), salt,
                               opslimit=argon2id.OPSLIMIT_INTERACTIVE,
                               memlimit=argon2id.MEMLIMIT_INTERACTIVE)
            box = SecretBox(key)
            state = initial if envelope is None else json.loads(
                box.decrypt(b64decode(envelope["ciphertext"], validate=True))
            )
            return cls(path, salt, box, state)
        except (CryptoError, KeyError, TypeError, ValueError, RuntimeError):
            raise SetupError("Could not unlock the setup vault. Check the password or restore your backup.") from None

    def save(self):
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
            temporary.replace(self.path)
