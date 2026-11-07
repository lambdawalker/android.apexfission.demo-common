"""Credential-free regression tests for setup security and recovery."""
import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from filelock import FileLock, Timeout
from github_environment_api import SetupError
from setup_demo_apk_signing import BRANCH_POLICY, default_operation, ensure_main_only, generate_password
from signing_setup_ui import SigningSetupApp
from signing_setup_vault import SetupVault


class VaultTests(unittest.TestCase):
    def test_round_trip_wrong_password_and_fresh_nonce(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "answers.vault"
            state = {"pending": ["github"], "complete": ["key"], "github_token": "private-test-token"}
            vault = SetupVault.unlock(path, "test master password", initial=state)
            vault.save()
            first = path.read_bytes()
            self.assertNotIn(b"private-test-token", first)
            self.assertEqual(SetupVault.unlock(path, "test master password").state, state)
            with self.assertRaises(SetupError):
                SetupVault.unlock(path, "wrong password")
            vault.save()
            self.assertNotEqual(first, path.read_bytes())
            data = bytearray(path.read_bytes())
            data[len(data) // 2] ^= 1
            path.write_bytes(data)
            with self.assertRaises(SetupError):
                SetupVault.unlock(path, "test master password")

    def test_invalid_state_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "answers.vault"
            with self.assertRaises(SetupError):
                SetupVault.unlock(path, "test password", initial={"pending": ["delete"], "complete": []})
            target = Path(folder) / "target"
            target.write_text("preserve")
            path.symlink_to(target)
            with self.assertRaises(SetupError):
                SetupVault.unlock(path, "test password")
            self.assertEqual(target.read_text(), "preserve")

    def test_lock_excludes_second_writer(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / "setup.lock")
            with FileLock(path, timeout=0):
                with self.assertRaises(Timeout):
                    with FileLock(path, timeout=0):
                        self.fail("Second writer acquired lock")

    def test_recovery_defaults(self):
        self.assertEqual(default_operation({"pending": [], "complete": []}), "3")
        self.assertEqual(default_operation({"pending": ["github"], "complete": ["key"]}), "2")
        self.assertEqual(default_operation({"pending": [], "complete": ["key", "github"]}), "q")

    def test_generated_password(self):
        import string
        from setup_demo_apk_signing import SYMBOLS
        for _ in range(20):
            password = generate_password()
            self.assertEqual(len(password), 25)
            for group in (string.ascii_lowercase, string.ascii_uppercase, string.digits, SYMBOLS):
                self.assertTrue(set(password).intersection(group))


class PolicyTests(unittest.IsolatedAsyncioTestCase):
    async def test_complete_setup_requires_main_only_without_mutation(self):
        class API:
            def environment_path(self, name):
                return "/environment"

            async def request(self, method, path, **kwargs):
                self_method.assertEqual(method, "GET")
                return {"total_count": 0, "branch_policies": []}

        self_method = self
        with self.assertRaises(SetupError):
            await ensure_main_only(API(), {"deployment_branch_policy": BRANCH_POLICY}, allow_create=False)


class PromptTests(unittest.IsolatedAsyncioTestCase):
    async def test_timeout_cancels_confirmation_but_password_waits(self):
        results = []
        async def flow(app):
            results.append(await app.prompt("Type APPLY", default_label="Cancel"))
            results.append(await app.prompt("Password", secret=True))
            app.exit()

        with patch("signing_setup_ui.PROMPT_SECONDS", 0.1):
            app = SigningSetupApp(flow)
            async with app.run_test() as pilot:
                await pilot.pause(0.4)
                self.assertEqual(results, [""])
                self.assertIsNotNone(app.answer)
                self.assertFalse(app.answer.done())
                await pilot.press("s", "e", "c", "r", "e", "t", "enter")
            self.assertEqual(results, ["", "secret"])
