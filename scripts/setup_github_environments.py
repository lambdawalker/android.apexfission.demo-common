#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "filelock==3.20.0",
#     "httpx==0.28.1",
#     "PyNaCl==1.6.2",
#     "PyYAML==6.0.3",
#     "textual==8.2.8",
# ]
# ///
"""Interactive, review-before-apply setup of publishing GitHub environments."""
import argparse
from contextlib import contextmanager
from dataclasses import dataclass, field
from hashlib import sha256
import os
from pathlib import Path

try:
    from filelock import FileLock, Timeout
except ImportError:  # pragma: no cover - fallback when filelock is not installed
    import fcntl

    class Timeout(Exception):
        pass

    class FileLock:
        def __init__(self, lock_file, timeout=0):
            self.lock_file = str(lock_file)
            self.timeout = timeout
            self._fd = None

        def acquire(self):
            fd = os.open(self.lock_file, os.O_CREAT | os.O_RDWR, 0o600)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                os.close(fd)
                raise Timeout(self.lock_file) from None
            self._fd = fd
            return self

        def release(self):
            if self._fd is not None:
                try:
                    fcntl.flock(self._fd, fcntl.LOCK_UN)
                finally:
                    os.close(self._fd)
                    self._fd = None

        def __enter__(self):
            return self.acquire()

        def __exit__(self, *_):
            self.release()

try:
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical, VerticalScroll
    from textual.widgets import Button, Footer, Header, Input, ProgressBar, Static
except ImportError:  # pragma: no cover - fallback stubs for headless unit test environments
    ComposeResult = object

    class _Widget:
        def __init__(self, *args, **kwargs):
            self.id = kwargs.get('id')
            self.value = kwargs.get('value', '')
            self.password = kwargs.get('password', False)
            self.placeholder = kwargs.get('placeholder', '')
            self.label = args[0] if args else ''
            self.disabled = False
            self.display = True

        def update(self, *args, **kwargs):
            pass

        def focus(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

    class App:
        def __init__(self, *args, **kwargs):
            self._widgets = {}

        def query_one(self, selector, *_):
            key = selector.lstrip('#')
            if key not in self._widgets:
                self._widgets[key] = _Widget(id=key)
            return self._widgets[key]

        def exit(self, *args, **kwargs):
            pass

        def run(self):
            pass

        @contextmanager
        def _sync_noop(self):
            yield

        def run_test(self, *args, **kwargs):
            class _Pilot:
                async def pause(self, *_):
                    pass

                async def __aenter__(self):
                    return self

                async def __aexit__(self, *_):
                    return False

            return _Pilot()

    Horizontal = Vertical = VerticalScroll = Button = Footer = Header = Input = ProgressBar = Static = _Widget

from github_environment_api import GitHubAPI, SetupError, validate_repository


LOCK_DIR = Path.home() / '.projects' / 'android.apexfission.demo-common' / 'secrets'


def lock_path(repository, directory=None):
    validate_repository(repository)
    repository_id = sha256(repository.casefold().encode()).hexdigest()[:16]
    base = (
        Path.home() / '.projects' / repository.split('/')[1].lower() / 'secrets'
        if directory is None
        else Path(directory)
    )
    return base / f'environments-{repository_id}.lock'


@contextmanager
def setup_lock(repository, directory=None):
    path = lock_path(repository, directory=directory)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        with FileLock(str(path), timeout=0):
            yield path
    except Timeout:
        raise SetupError(
            'Another environment setup wizard is running for this repository. Close it before retrying.'
        ) from None


@dataclass
class Setting:
    environment: str
    name: str
    kind: str
    required: bool
    default: str = ''
    existing: bool = False
    current: str = field(default='', repr=False)


def choose_value(setting, entered):
    """Blank always preserves existing values; key input is a file path."""
    if not entered:
        if setting.existing or not setting.required:
            return None
        if setting.default:
            return setting.default
        raise SetupError('This setting is required because it does not exist yet.')
    if setting.name == 'SIGNING_IN_MEMORY_KEY':
        try:
            value = Path(entered).expanduser().read_bytes().decode('utf-8')
        except (OSError, UnicodeError, ValueError):
            raise SetupError('Cannot read the signing key file as UTF-8. Check the path and permissions.') from None
        if not value.strip():
            raise SetupError('The signing key file is empty.')
        return value
    if setting.required and not entered.strip():
        raise SetupError('This required setting cannot contain only whitespace.')
    if setting.name == 'MAVEN_REPOSITORY_URL':
        from publishing_config import validate_url
        try:
            return validate_url(entered)
        except ValueError:
            raise SetupError('Enter an HTTPS repository URL without credentials, query, or fragment.') from None
    return entered


@dataclass
class ApplyResult:
    completed: list = field(default_factory=list)
    failed: str = ''
    message: str = ''


async def verify_pre_apply_state(api, environments, settings, changes):
    if not hasattr(api, 'snapshot'):
        return
    touched = {settings[index].environment for index in changes} | {
        env for env, exists in environments.items() if not exists
    }
    for environment in environments:
        if environment not in touched:
            continue
        exists, variables, secrets = await api.snapshot(environment)
        if environments[environment] != exists:
            raise SetupError(f'Environment {environment} changed during review. Rerun to inspect current state.')
        for index, setting in enumerate(settings):
            if setting.environment != environment or index not in changes:
                continue
            now_exists = setting.name in (variables if setting.kind == 'variable' else secrets)
            now_value = variables.get(setting.name, '') if setting.kind == 'variable' else ''
            if now_exists != setting.existing or (setting.kind == 'variable' and now_value != setting.current):
                raise SetupError(
                    f'{environment} / {setting.name} changed concurrently. Rerun to inspect current state.'
                )


async def apply_changes(api, environments, settings, changes):
    result = ApplyResult()
    label = ''
    try:
        label = 'pre-apply environment check'
        await verify_pre_apply_state(api, environments, settings, changes)
        for environment, exists in environments.items():
            if not exists:
                label = f'{environment} / environment'
                if environment == 'delayed-docs':
                    try:
                        already_exists = await api.ensure_environment(environment, wait_timer=15)
                    except SetupError as error:
                        if 'HTTP 422' not in str(error):
                            raise
                        already_exists = await api.ensure_environment(environment)
                        result.completed.append('Wait timer unavailable. Review delayed-docs in Settings.')
                else:
                    already_exists = await api.ensure_environment(environment)
                result.completed.append(label + (' (already exists)' if already_exists else ' (created)'))
        for index, value in changes.items():
            setting = settings[index]
            label = f'{setting.environment} / {setting.name}'
            if setting.kind == 'variable':
                try:
                    await api.write_variable(setting.environment, setting.name, value, setting.existing)
                except SetupError as error:
                    if 'HTTP 409' in str(error):
                        raise SetupError(
                            f'{label} was modified concurrently (HTTP 409 Conflict). Rerun to inspect current state.'
                        ) from None
                    raise
            else:
                await api.write_secret(setting.environment, setting.name, value)
            result.completed.append(label)
    except SetupError as error:
        result.failed, result.message = label, str(error)
    except Exception:
        # Unexpected library failures must never dump frame locals or secret data.
        result.failed, result.message = label, 'Unexpected setup failure. Rerun to inspect current state.'
    return result


class SetupWizard(App):
    TITLE = 'Publishing • Environment setup'
    SUB_TITLE = 'GitHub configuration'
    BINDINGS = [('ctrl+q', 'quit', 'Exit')]
    CSS = """
    Screen { background: #0b1220; color: #dbeafe; }
    Header { background: #172c47; }
    #card { width: 90%; max-width: 105; height: 1fr; margin: 0 2; padding: 0 2; border: round #38bdf8; background: #101f33; }
    #eyebrow { color: #38bdf8; text-style: bold; margin-bottom: 1; }
    #heading { color: #f0f9ff; text-style: bold; margin-bottom: 1; }
    #body { height: 1fr; min-height: 2; }
    #detail { height: auto; }
    #value { margin-top: 1; border: tall #365575; }
    #error { color: #fda4af; height: auto; }
    #actions { height: 3; margin-top: 1; }
    Button { margin-right: 2; }
    ProgressBar { margin-bottom: 1; }
    Footer { background: #172c47; }
    """

    def __init__(self, repository, settings, *, api_factory=GitHubAPI):
        super().__init__()
        self.repository, self.settings = repository, settings
        self.api_factory, self.api = api_factory, None
        self.environments, self.changes = {}, {}
        from publishing_config import load_config
        self.environment_names = list(dict.fromkeys([*(entry['environment'] for entry in load_config().values()), 'delayed-docs']))
        self.stage, self.index = 'token', 0

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id='card'):
            yield Static('CONNECT  /  CONFIGURE  /  REVIEW  /  APPLY', id='eyebrow')
            yield Static('Connect to GitHub', id='heading')
            yield ProgressBar(total=max(len(self.settings), 1), show_eta=False, id='progress')
            with VerticalScroll(id='body'):
                yield Static(
                    f'Repository: {self.repository}\n\nUse a fine-grained token restricted to this repository, '
                    'with Administration: read/write (create environments) and Environments: read/write '
                    '(variables and secrets). You must be a repository administrator. '
                    'For a classic token use repo scope; authorize organization SSO if required.\n\n'
                    'Paste your token below. It is masked, held only in memory, and never saved. '
                    'Nothing is written until you review and apply.', id='detail', markup=False)
            yield Input(password=True, placeholder='GitHub access token', id='value')
            yield Static('', id='error', markup=False)
            with Horizontal(id='actions'):
                yield Button('Connect →', variant='primary', id='next')
                yield Button('Cancel', id='cancel')
        yield Footer()

    def on_mount(self):
        self.query_one('#value', Input).focus()

    async def on_unmount(self):
        self.changes.clear()
        if self.api:
            await self.api.aclose()

    def show_setting(self):
        if self.index == len(self.settings):
            self.show_review()
            return
        setting = self.settings[self.index]
        self.query_one('#heading', Static).update(f'{setting.environment}  /  {setting.name}')
        self.query_one('#progress', ProgressBar).update(progress=self.index)
        detail = f'Setting {self.index + 1} of {len(self.settings)} · {setting.kind.upper()}\n\n'
        if setting.existing:
            detail += ('Current value: ' + setting.current if setting.kind == 'variable' else 'Secret exists. GitHub never returns its value.')
            detail += '\n\nLeave blank to keep the existing value.'
        else:
            detail += 'Not configured yet. ' + ('Required.' if setting.required else 'Optional; blank leaves it unset.')
            if setting.default:
                detail += f'\nLeave blank to use: {setting.default}'
        if setting.name == 'SIGNING_IN_MEMORY_KEY':
            detail += '\n\nEnter the path to your UTF-8 ASCII-armored private key file. The path is masked; the full multiline file is encrypted before upload.'
        self.query_one('#detail', Static).update(detail)
        entry = self.query_one('#value', Input)
        entry.password = setting.kind == 'secret'
        entry.value = ''
        entry.placeholder = 'Path to signing key file' if setting.name == 'SIGNING_IN_MEMORY_KEY' else 'New value (blank keeps current)'
        self.query_one('#next', Button).label = 'Continue →'
        entry.focus()

    def show_review(self):
        self.stage = 'review'
        self.query_one('#heading', Static).update('Review your changes')
        self.query_one('#progress', ProgressBar).update(progress=len(self.settings))
        lines = [f'Repository: {self.repository}', '']
        for env, exists in self.environments.items():
            action = 'keep environment and protection rules' if exists else 'CREATE environment'
            if env == 'delayed-docs' and not exists:
                action += ' with a 15-minute wait timer where supported'
            lines.append(f'{env}: {action}')
        for index, setting in enumerate(self.settings):
            action = ('UPDATE' if setting.existing else 'CREATE') if index in self.changes else ('KEEP' if setting.existing else 'LEAVE UNSET')
            lines.append(f'{action}  {setting.environment} / {setting.name} ({setting.kind})')
            if index in self.changes and setting.kind == 'variable':
                lines.append(f'    New value: {self.changes[index]}')
        lines += ['', 'Secret values and file paths are hidden. Existing protection rules are preserved.',
                  'GitHub writes are not atomic. If interrupted, rerun to inspect and complete remaining settings.']
        self.query_one('#detail', Static).update('\n'.join(lines))
        self.query_one('#value', Input).display = False
        self.query_one('#next', Button).label = 'Apply changes'
        self.query_one('#next', Button).focus()

    async def on_input_submitted(self, event):
        await self.advance()

    async def on_button_pressed(self, event):
        if event.button.id == 'cancel':
            self.exit()
        else:
            await self.advance()

    async def advance(self):
        button = self.query_one('#next', Button)
        if button.disabled:
            return
        button.disabled = True
        self.query_one('#error', Static).update('')
        try:
            if self.stage == 'token':
                entry = self.query_one('#value', Input)
                try:
                    token = entry.value.strip()
                finally:
                    entry.value = ''
                if not token:
                    raise SetupError('Enter a GitHub token to continue.')
                if self.api:
                    await self.api.aclose()
                self.api = self.api_factory(self.repository, token)
                token = ''
                self.query_one('#heading', Static).update('Reading environment settings…')
                for environment in self.environment_names:
                    exists, variables, secrets = await self.api.snapshot(environment)
                    self.environments[environment] = exists
                    for setting in self.settings:
                        if setting.environment == environment:
                            setting.existing = setting.name in (variables if setting.kind == 'variable' else secrets)
                            setting.current = variables.get(setting.name, '') if setting.kind == 'variable' else ''
                self.stage = 'settings'
                self.show_setting()
            elif self.stage == 'settings':
                entry = self.query_one('#value', Input)
                try:
                    entered = entry.value
                    entry.value = ''
                    value = choose_value(self.settings[self.index], entered)
                finally:
                    entry.value = ''
                    entered = ''
                if value is not None:
                    self.changes[self.index] = value
                self.index += 1
                self.show_setting()
            elif self.stage == 'review':
                self.stage = 'applying'
                self.query_one('#cancel', Button).disabled = True
                self.query_one('#heading', Static).update('Applying changes…')
                result = await apply_changes(self.api, self.environments, self.settings, self.changes)
                self.changes.clear()
                await self.api.aclose()
                self.api = None
                self.stage = 'done'
                self.query_one('#heading', Static).update('Setup incomplete' if result.failed else 'Setup complete')
                text = 'Completed writes:\n' + ('\n'.join(result.completed) or 'None. Existing settings were preserved.')
                if result.failed:
                    text += f'\n\nFailed or uncertain: {result.failed}\n{result.message}\nRemaining changes were not attempted. Rerun to inspect current settings and resume.'
                self.query_one('#detail', Static).update(text)
                button.label = 'Close'
            elif self.stage == 'done':
                self.exit()
        except SetupError as error:
            self.query_one('#error', Static).update(str(error))
        except Exception:
            self.query_one('#error', Static).update('Unexpected setup failure. Check access and rerun; no sensitive details are shown.')
        finally:
            button.disabled = False


def main():
    from publishing_config import DEFAULT_CONFIG, load_config, settings_for
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default='lambdawalker/android.apexfission.demo-common', help='GitHub owner/name')
    parser.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    try:
        validate_repository(args.repo)
        registry = load_config(args.config)
    except (SetupError, ValueError, OSError) as error:
        parser.error(str(error))
    settings = [Setting(entry['environment'], **setting) for entry in registry.values() for setting in settings_for(entry)]
    try:
        with setup_lock(args.repo):
            wizard = SetupWizard(args.repo, settings)
            wizard.environment_names = [*(entry['environment'] for entry in registry.values()), 'delayed-docs']
            wizard.run()
    except SetupError as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
